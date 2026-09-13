# backtester/engine.py
"""Core backtesting simulation engine.

Parses strategy conditions, generates entry/exit signals,
simulates portfolio trades, and computes performance metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable

import numpy as np
import pandas as pd

from backtester.batch_indicators import compute_indicator
from backtester.data_pipeline import DataPipeline
from backtester.metrics import (
    Trade,
    compute_benchmark_metrics,
    compute_metrics,
)


@dataclass
class Condition:
    """A single indicator condition for entry signals."""

    indicator: str
    params: tuple
    component: str | None
    operator: str
    value: float
    interval: str


@dataclass
class BacktestResult:
    """Complete backtest results."""

    trades: list[Trade]
    metrics: dict
    benchmark_metrics: dict
    ticker_results: dict[str, list[Trade]]
    conditions: list[Condition]
    config: dict


@dataclass
class Position:
    """A held position in a ticker."""

    ticker: str
    shares: float
    avg_cost: float
    invested: float


class Portfolio:
    """Tracks positions, cash, and enforces position sizing."""

    def __init__(
        self,
        capital: float,
        position_size: float,
        position_size_base: str,
    ) -> None:
        self.initial_capital = capital
        self.cash = capital
        self.position_size = position_size
        self.position_size_base = position_size_base
        self.positions: dict[str, Position] = {}

    def get_invested(self, ticker: str) -> float:
        pos = self.positions.get(ticker)
        return pos.invested if pos else 0.0

    def calculate_buy_amount(self, ticker: str, price: float) -> float:
        if self.position_size == 0 or price <= 0:
            return 0.0

        if self.position_size_base == "total":
            target = self.initial_capital * (self.position_size / 100)
        else:
            target = self.cash * (self.position_size / 100)

        current = self.get_invested(ticker)
        if current >= target:
            return 0.0

        needed = target - current
        available = min(needed, self.cash)
        if available <= 0:
            return 0.0

        return available / price

    def buy(
        self, ticker: str, shares: float, price: float
    ) -> bool:
        cost = shares * price
        if cost > self.cash or shares <= 0:
            return False

        self.cash -= cost

        if ticker in self.positions:
            pos = self.positions[ticker]
            total_shares = pos.shares + shares
            pos.avg_cost = (
                (pos.avg_cost * pos.shares + price * shares)
                / total_shares
            )
            pos.shares = total_shares
            pos.invested += cost
        else:
            self.positions[ticker] = Position(
                ticker=ticker,
                shares=shares,
                avg_cost=price,
                invested=cost,
            )
        return True

    def sell(self, ticker: str, price: float) -> float:
        pos = self.positions.pop(ticker, None)
        if pos is None:
            return 0.0
        proceeds = pos.shares * price
        self.cash += proceeds
        return proceeds

    def get_total_value(
        self, current_prices: dict[str, float]
    ) -> float:
        value = self.cash
        for ticker, pos in self.positions.items():
            price = current_prices.get(ticker, pos.avg_cost)
            value += pos.shares * price
        return value


class BacktestEngine:
    """Core backtesting simulation."""

    def __init__(
        self,
        conditions: list[Condition],
        config: dict,
    ) -> None:
        self.conditions = conditions
        self.config = config
        self.pipeline = DataPipeline()

    def run(
        self,
        on_progress: Callable[[int], None] | None = None,
    ) -> BacktestResult:
        """Execute the full backtest.

        Steps:
        1. Determine smallest interval from conditions.
        2. Download data for all tickers at that interval.
        3. Compute indicators for each ticker.
        4. Evaluate conditions on each bar.
        5. Simulate portfolio with position sizing.
        6. Compute metrics and benchmark comparison.

        Args:
            on_progress: Optional callback receiving progress 0–100.

        Returns:
            BacktestResult with trades, metrics, and benchmark.
        """
        tickers = self.config["tickers"]
        years = self.config["years"]
        capital = self.config["capital"]
        benchmark = self.config["benchmark"]
        position_size = self.config.get("position_size", 100)
        position_size_base = self.config.get(
            "position_size_base", "total"
        )

        def _progress(pct: int) -> None:
            if on_progress:
                on_progress(min(pct, 100))

        # Resolve universe if specified
        _progress(1)
        universe = self.config.get("universe")
        if universe:
            from backtester.universe import resolve_universe
            tickers = resolve_universe(universe)
            max_tickers = self.config.get("max_tickers")
            if max_tickers:
                tickers = tickers[:max_tickers]

        interval = self._smallest_interval()
        _progress(1)
        _progress(2)
        all_data = self.pipeline.fetch(
            tickers, interval, years,
            on_progress=lambda p: _progress(2 + int(30 * p / 100)),
        )
        _progress(32)

        if not all_data:
            return BacktestResult(
                trades=[],
                metrics={},
                benchmark_metrics={},
                ticker_results={},
                conditions=self.conditions,
                config=self.config,
            )

        # Download benchmark data
        _progress(32)
        bench_data = self.pipeline.fetch(
            [benchmark], interval, years,
            on_progress=lambda p: _progress(32 + int(3 * p / 100)),
        )
        bench_df = bench_data.get(benchmark, pd.DataFrame())
        _progress(35)

        # Create portfolio
        portfolio = Portfolio(
            capital=capital,
            position_size=position_size,
            position_size_base=position_size_base,
        )

        all_trades: list[Trade] = []
        ticker_results: dict[str, list[Trade]] = {}
        skipped = 0

        total_tickers = len(all_data)
        # Ticker loop spans 35%–65% (30% range).
        # Metrics spans 65%–100% (35% range with sub-steps).
        ticker_start = 35
        ticker_end = 65
        ticker_step = (ticker_end - ticker_start) / max(total_tickers, 1)
        _progress(ticker_start)
        for i, (ticker, df) in enumerate(all_data.items()):
            base = ticker_start + int(ticker_step * i)
            enriched = self._compute_indicators(ticker, df)
            _progress(base + int(ticker_step * 0.3))
            # Vectorized: skip tickers with no entry signals
            if not self._has_any_signal(enriched):
                ticker_results[ticker] = []
                skipped += 1
            else:
                trades = self._simulate_ticker(
                    ticker, enriched, portfolio
                )
                ticker_results[ticker] = trades
                all_trades.extend(trades)
            _progress(base + int(ticker_step * 0.9))
        _progress(ticker_end)

        # Sort all trades globally by entry date
        all_trades.sort(key=lambda t: t.entry_date)

        _progress(66)
        metrics = compute_metrics(all_trades, capital)
        _progress(72)
        metrics["cash_remaining"] = round(portfolio.cash, 2)
        metrics["positions_value"] = round(
            portfolio.get_total_value(
                {t: all_data[t]["Close"].iloc[-1]
                 for t in portfolio.positions
                 if t in all_data}
            ),
            2,
        )
        _progress(78)

        benchmark_metrics = {}
        if not bench_df.empty and all_trades:
            _progress(80)
            dates = [t.entry_date for t in all_trades]
            start_date = min(dates)
            end_date = max(t.exit_date for t in all_trades)
            benchmark_metrics = compute_benchmark_metrics(
                bench_df, start_date, end_date
            )
            _progress(86)
        else:
            _progress(84)

        _progress(92)
        result = BacktestResult(
            trades=all_trades,
            metrics=metrics,
            benchmark_metrics=benchmark_metrics,
            ticker_results=ticker_results,
            conditions=self.conditions,
            config=self.config,
        )
        _progress(100)
        return result

    def _smallest_interval(self) -> str:
        """Determine the smallest interval from conditions.

        Returns:
            The smallest interval string.
        """
        order = [
            "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
            "1d", "5d", "1wk", "1mo", "3mo",
        ]
        intervals = [c.interval for c in self.conditions]
        for candidate in order:
            if candidate in intervals:
                return candidate
        return intervals[0] if intervals else "1d"

    def _compute_indicators(
        self, ticker: str, df: pd.DataFrame
    ) -> pd.DataFrame:
        """Add indicator columns to DataFrame.

        Deduplicates identical indicator computations and avoids
        unnecessary DataFrame copies.

        Args:
            ticker: Stock symbol.
            df: Raw OHLCV DataFrame.

        Returns:
            DataFrame with indicator columns added.
        """
        enriched = df.copy()

        # Cache indicator results to avoid recomputing duplicates
        indicator_cache: dict[tuple, pd.Series] = {}

        for cond in self.conditions:
            cache_key = (cond.indicator, cond.params, cond.component)
            if cache_key in indicator_cache:
                series = indicator_cache[cache_key]
            else:
                series = compute_indicator(
                    enriched, cond.indicator, cond.params, cond.component
                )
                indicator_cache[cache_key] = series
            col_name = self._condition_col_name(cond)
            enriched[col_name] = series

        return enriched

    def _condition_col_name(self, cond: Condition) -> str:
        """Generate a column name for a condition.

        Args:
            cond: A Condition object.

        Returns:
            Column name string.
        """
        parts = [cond.indicator]
        if cond.component:
            parts.append(cond.component)
        parts.append(cond.interval)
        return "_".join(parts)

    def _has_any_signal(self, df: pd.DataFrame) -> bool:
        """Vectorized check for any entry signal in the DataFrame.

        Uses pandas boolean masking instead of row-by-row iteration.

        Args:
            df: DataFrame with indicator columns.

        Returns:
            True if at least one bar triggers all conditions.
        """
        mask = pd.Series(True, index=df.index, dtype=bool)
        for cond in self.conditions:
            col = self._condition_col_name(cond)
            if col not in df.columns:
                return False
            col_data = df[col]
            mask &= col_data.notna()
            if cond.operator == ">":
                mask &= (col_data > cond.value).fillna(False)
            elif cond.operator == "<":
                mask &= (col_data < cond.value).fillna(False)
            elif cond.operator == ">=":
                mask &= (col_data >= cond.value).fillna(False)
            elif cond.operator == "<=":
                mask &= (col_data <= cond.value).fillna(False)
            elif cond.operator == "==":
                mask &= (col_data == cond.value).fillna(False)
        return bool(mask.any())

    def _evaluate_conditions(self, row: pd.Series) -> bool:
        """Check if all conditions are met for a single bar.

        Args:
            row: A single DataFrame row with indicator columns.

        Returns:
            True if all conditions are simultaneously true.
        """
        for cond in self.conditions:
            col = self._condition_col_name(cond)
            if col not in row.index:
                return False
            val = row[col]
            if pd.isna(val):
                return False
            if not self._check_condition(val, cond.operator, cond.value):
                return False
        return True

    @staticmethod
    def _check_condition(value: float, operator: str, threshold: float) -> bool:
        """Evaluate a single comparison.

        Args:
            value: Computed indicator value.
            operator: Comparison operator.
            threshold: Threshold value.

        Returns:
            True if the comparison holds.
        """
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        raise ValueError(f"Unknown operator '{operator}'")

    def _simulate_ticker(
        self,
        ticker: str,
        df: pd.DataFrame,
        portfolio: Portfolio | None = None,
    ) -> list[Trade]:
        """Simulate trades for a single ticker.

        Entry: all conditions simultaneously true.
        Exit: after hold_period bars or stop-loss trigger.

        Uses precomputed entry bars for speed — only iterates over
        bars where conditions are met, skipping non-signal bars.

        Args:
            ticker: Stock symbol.
            df: DataFrame with indicator columns.
            portfolio: Portfolio for position sizing (optional).

        Returns:
            List of completed trades.
        """
        trades: list[Trade] = []
        hold = self.config["hold"]
        stop_loss = self.config.get("stop_loss")

        # Precompute signal mask vectorially
        mask = pd.Series(True, index=df.index, dtype=bool)
        for cond in self.conditions:
            col = self._condition_col_name(cond)
            if col not in df.columns:
                return trades
            col_data = df[col]
            mask &= col_data.notna()
            if cond.operator == ">":
                mask &= (col_data > cond.value).fillna(False)
            elif cond.operator == "<":
                mask &= (col_data < cond.value).fillna(False)
            elif cond.operator == ">=":
                mask &= (col_data >= cond.value).fillna(False)
            elif cond.operator == "<=":
                mask &= (col_data <= cond.value).fillna(False)
            elif cond.operator == "==":
                mask &= (col_data == cond.value).fillna(False)

        # Get all entry bar positions
        entry_positions = np.where(mask.values)[0]
        if len(entry_positions) == 0:
            return trades

        # Pre-extract Close prices as numpy array for fast access
        close_arr = df["Close"].values
        idx = df.index

        # Iterate only over signal bars
        last_exit = -1
        for pos in entry_positions:
            # Skip if within cooldown period of last exit
            if pos <= last_exit:
                continue

            entry_price = close_arr[pos]
            if pd.isna(entry_price) or entry_price <= 0:
                continue

            # Skip if hold period extends past available data
            if pos + hold >= len(df):
                break

            # Position sizing via portfolio
            shares = 0.0
            invested = 0.0
            if portfolio is not None:
                shares = portfolio.calculate_buy_amount(
                    ticker, entry_price
                )
                if shares <= 0:
                    continue
                portfolio.buy(ticker, shares, entry_price)
                invested = shares * entry_price

            exit_idx = pos + hold

            # Check stop-loss during hold period
            if stop_loss is not None:
                threshold = -stop_loss / 100.0
                for j in range(pos + 1, min(exit_idx + 1, len(df))):
                    ret = (close_arr[j] - entry_price) / entry_price
                    if ret <= threshold:
                        exit_idx = j
                        break

            if exit_idx >= len(df):
                break

            exit_date = idx[exit_idx]
            exit_price = close_arr[exit_idx]
            ret = (exit_price - entry_price) / entry_price

            # Sell from portfolio
            if portfolio is not None and shares > 0:
                portfolio.sell(ticker, exit_price)

            trades.append(
                Trade(
                    ticker=ticker,
                    entry_date=idx[pos],
                    entry_price=entry_price,
                    exit_date=exit_date,
                    exit_price=exit_price,
                    hold_bars=exit_idx - pos,
                    return_pct=ret,
                    shares=shares,
                    invested=invested,
                )
            )
            last_exit = exit_idx + hold  # cooldown

        return trades
