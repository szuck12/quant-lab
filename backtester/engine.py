# backtester/engine.py
"""Core backtesting simulation engine.

Parses strategy conditions, generates entry/exit signals,
simulates portfolio trades, and computes performance metrics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from collections.abc import Callable

import numpy as np
import pandas as pd

from backtester.batch_indicators import compute_indicator
from backtester.data_pipeline import DataPipeline, _normalize_frame
from backtester.metrics import (
    Trade,
    compute_benchmark_metrics,
    compute_metrics,
)

logger = logging.getLogger(__name__)


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
    equity_curve: pd.Series = field(
        default_factory=lambda: pd.Series(dtype=float)
    )
    benchmark_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    reason: str = ""


@dataclass
class _OpenPosition:
    """An open position tracked during the portfolio simulation."""

    ticker: str
    shares: float
    entry_price: float
    invested: float
    entry_date: pd.Timestamp
    entry_bar: int
    exit_bar: int


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
        3. Simulate the portfolio day-by-day in chronological order,
           enforcing real cash availability across all tickers.
        4. Compute metrics from the mark-to-market equity curve.
        5. Compare against the benchmark (SPY, daily).

        Args:
            on_progress: Optional callback receiving progress 0–100.

        Returns:
            BacktestResult with trades, metrics, benchmark, and curves.
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
                equity_curve=pd.Series(dtype=float),
                benchmark_df=pd.DataFrame(),
                reason=(
                    "No market data was returned for the selected "
                    "universe. Yahoo Finance may be rate-limiting or "
                    "unavailable — please try again shortly."
                ),
            )

        # Benchmark is always the S&P 500 proxy (SPY) at daily
        # resolution, independent of the strategy interval.
        bench_data = self.pipeline.fetch(
            [benchmark], "1d", years,
            on_progress=lambda p: _progress(32 + int(3 * p / 100)),
        )
        bench_df = bench_data.get(benchmark, pd.DataFrame())
        _progress(35)

        # Single portfolio shared chronologically across every ticker
        portfolio = Portfolio(
            capital=capital,
            position_size=position_size,
            position_size_base=position_size_base,
        )

        _progress(36)
        (
            all_trades,
            ticker_results,
            equity_curve,
        ) = self._simulate_portfolio(
            all_data,
            portfolio,
            on_progress=lambda p: _progress(36 + int(52 * p / 100)),
        )
        _progress(88)

        # Trades for display/metrics, ordered by entry date
        all_trades.sort(key=lambda t: t.entry_date)

        _progress(89)
        metrics = compute_metrics(all_trades, capital, equity_curve)
        _progress(93)
        metrics["cash_remaining"] = round(portfolio.cash, 2)
        end_prices: dict[str, float] = {}
        for t in portfolio.positions:
            if t in all_data:
                frame = _normalize_frame(all_data[t])
                if not frame.empty:
                    end_prices[t] = float(frame["Close"].iloc[-1])
        metrics["positions_value"] = round(
            sum(
                pos.shares * end_prices.get(t, pos.avg_cost)
                for t, pos in portfolio.positions.items()
            ),
            2,
        )

        # Benchmark is non-fatal: a benchmark data problem must never
        # fail the whole backtest.
        benchmark_metrics: dict = {}
        if not bench_df.empty and not equity_curve.empty:
            try:
                benchmark_metrics = compute_benchmark_metrics(
                    bench_df,
                    equity_curve.index[0],
                    equity_curve.index[-1],
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Benchmark metrics failed: %s", exc)
                benchmark_metrics = {}
        _progress(97)

        reason = ""
        if not all_trades:
            reason = (
                "No trades matched your conditions for this period "
                "and universe. Try loosening thresholds or extending "
                "the period."
            )

        result = BacktestResult(
            trades=all_trades,
            metrics=metrics,
            benchmark_metrics=benchmark_metrics,
            ticker_results=ticker_results,
            conditions=self.conditions,
            config=self.config,
            equity_curve=equity_curve,
            benchmark_df=bench_df,
            reason=reason,
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

    def _signal_mask(self, df: pd.DataFrame) -> pd.Series:
        """Vectorized entry-signal mask for every bar.

        A bar is a signal when all conditions are simultaneously true
        and none of the indicator values are NaN.

        Args:
            df: DataFrame with indicator columns.

        Returns:
            Boolean Series aligned to df.index.
        """
        mask = pd.Series(True, index=df.index, dtype=bool)
        for cond in self.conditions:
            col = self._condition_col_name(cond)
            if col not in df.columns:
                return pd.Series(False, index=df.index, dtype=bool)
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
        return mask

    def _has_any_signal(self, df: pd.DataFrame) -> bool:
        """Vectorized check for any entry signal in the DataFrame.

        Args:
            df: DataFrame with indicator columns.

        Returns:
            True if at least one bar triggers all conditions.
        """
        return bool(self._signal_mask(df).any())

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

    def _simulate_portfolio(
        self,
        all_data: dict[str, pd.DataFrame],
        portfolio: Portfolio,
        on_progress: Callable[[int], None] | None = None,
    ) -> tuple[list[Trade], dict[str, list[Trade]], pd.Series]:
        """Simulate every ticker on one shared chronological timeline.

        Tickers are processed alphabetically within each trading day.
        Exits run before entries, and entries stop for that day once
        available cash is exhausted. This prevents the same capital
        from being deployed more than once on a given date and removes
        cross-ticker time reuse.

        Portfolio equity is marked to market every trading day; open
        positions are valued at their latest known close and are left
        open at the end of the backtest.

        Args:
            all_data: Mapping of ticker -> OHLCV DataFrame.
            portfolio: Shared, stateful portfolio.
            on_progress: Optional callback receiving progress 0–100.

        Returns:
            Tuple of (all trades, per-ticker trades, equity curve).
        """
        hold = self.config["hold"]
        stop_loss = self.config.get("stop_loss")

        # Precompute indicators and signals per ticker
        prepared: dict[str, dict] = {}
        master_index: pd.DatetimeIndex | None = None
        for ticker in sorted(all_data.keys()):
            df = _normalize_frame(all_data[ticker])
            if df.empty:
                continue
            enriched = self._compute_indicators(ticker, df)
            prepared[ticker] = {
                "index": enriched.index,
                "close": enriched["Close"].to_numpy(dtype=float),
                "signal": self._signal_mask(enriched).to_numpy(
                    dtype=bool
                ),
            }
            master_index = (
                enriched.index
                if master_index is None
                else master_index.union(enriched.index)
            )

        tickers = sorted(prepared.keys())
        ticker_results: dict[str, list[Trade]] = {t: [] for t in tickers}
        trades: list[Trade] = []

        if master_index is None or len(master_index) == 0:
            return trades, ticker_results, pd.Series(dtype=float)

        # Map each ticker's local bars onto the master date axis
        for ticker in tickers:
            p = prepared[ticker]
            gpos = master_index.get_indexer(p["index"])
            local_by_global = np.full(len(master_index), -1, dtype=int)
            valid = gpos >= 0
            local_by_global[gpos[valid]] = np.arange(len(gpos))[valid]
            p["local_by_global"] = local_by_global

        open_positions: dict[str, _OpenPosition] = {}
        last_exit_bar: dict[str, int] = {}
        last_close: dict[str, float] = {}
        equity_values = np.empty(len(master_index), dtype=float)
        total = len(master_index)
        report_every = max(1, total // 100)

        for gi in range(total):
            date = master_index[gi]

            # Refresh the latest known close for active tickers
            for ticker in tickers:
                lp = prepared[ticker]["local_by_global"][gi]
                if lp >= 0:
                    last_close[ticker] = prepared[ticker]["close"][lp]

            # --- 1. Exits: hold-period expiry or stop-loss ---
            for ticker in list(open_positions.keys()):
                op = open_positions[ticker]
                lp = prepared[ticker]["local_by_global"][gi]
                if lp < 0:
                    continue
                price = prepared[ticker]["close"][lp]
                if pd.isna(price) or price <= 0:
                    continue
                should_exit = lp >= op.exit_bar
                if stop_loss is not None and not should_exit:
                    ret = (price - op.entry_price) / op.entry_price
                    if ret <= -stop_loss / 100.0:
                        should_exit = True
                if not should_exit:
                    continue
                portfolio.sell(ticker, price)
                ret = (price - op.entry_price) / op.entry_price
                trade = Trade(
                    ticker=ticker,
                    entry_date=op.entry_date,
                    entry_price=op.entry_price,
                    exit_date=date,
                    exit_price=price,
                    hold_bars=lp - op.entry_bar,
                    return_pct=ret,
                    shares=op.shares,
                    invested=op.invested,
                )
                trades.append(trade)
                ticker_results[ticker].append(trade)
                del open_positions[ticker]
                last_exit_bar[ticker] = lp

            # --- 2. Entries: alphabetical, cash-limited, once/day ---
            if portfolio.cash > 0:
                for ticker in tickers:
                    if portfolio.cash <= 0:
                        break
                    if ticker in open_positions:
                        continue
                    lp = prepared[ticker]["local_by_global"][gi]
                    if lp < 0:
                        continue
                    if not prepared[ticker]["signal"][lp]:
                        continue
                    last_exit = last_exit_bar.get(ticker)
                    if last_exit is not None and lp <= last_exit + hold:
                        continue
                    if lp + hold >= len(prepared[ticker]["index"]):
                        continue
                    price = prepared[ticker]["close"][lp]
                    if pd.isna(price) or price <= 0:
                        continue
                    shares = portfolio.calculate_buy_amount(
                        ticker, price
                    )
                    if shares <= 0:
                        continue
                    if not portfolio.buy(ticker, shares, price):
                        continue
                    open_positions[ticker] = _OpenPosition(
                        ticker=ticker,
                        shares=shares,
                        entry_price=price,
                        invested=shares * price,
                        entry_date=date,
                        entry_bar=lp,
                        exit_bar=lp + hold,
                    )

            # --- 3. Mark-to-market equity (open positions included) ---
            value = portfolio.cash
            for ticker, op in open_positions.items():
                px = last_close.get(ticker, op.entry_price)
                value += op.shares * px
            equity_values[gi] = value

            if on_progress and (
                gi % report_every == 0 or gi == total - 1
            ):
                on_progress(int(100 * (gi + 1) / total))

        equity_curve = pd.Series(
            equity_values, index=master_index, dtype=float
        )
        return trades, ticker_results, equity_curve
