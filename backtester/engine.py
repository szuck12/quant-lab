# backtester/engine.py
"""Core backtesting simulation engine.

Parses strategy conditions, generates entry/exit signals,
simulates portfolio trades, and computes performance metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

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

    def run(self) -> BacktestResult:
        """Execute the full backtest.

        Steps:
        1. Determine smallest interval from conditions.
        2. Download data for all tickers at that interval.
        3. Compute indicators for each ticker.
        4. Evaluate conditions on each bar.
        5. Simulate portfolio with fixed hold period.
        6. Compute metrics and benchmark comparison.

        Returns:
            BacktestResult with trades, metrics, and benchmark.
        """
        tickers = self.config["tickers"]
        years = self.config["years"]
        capital = self.config["capital"]
        benchmark = self.config["benchmark"]

        interval = self._smallest_interval()
        print("\nStep 1/5: Downloading data...")
        all_data = self.pipeline.fetch(tickers, interval, years)

        if not all_data:
            print("Error: no data available for any ticker")
            return BacktestResult(
                trades=[],
                metrics={},
                benchmark_metrics={},
                ticker_results={},
                conditions=self.conditions,
                config=self.config,
            )

        # Download benchmark data
        bench_data = self.pipeline.fetch([benchmark], interval, years)
        bench_df = bench_data.get(benchmark, pd.DataFrame())

        print("\nStep 2/5: Computing indicators...")
        all_trades: list[Trade] = []
        ticker_results: dict[str, list[Trade]] = {}

        for ticker, df in all_data.items():
            enriched = self._compute_indicators(ticker, df)
            trades = self._simulate_ticker(ticker, enriched)
            ticker_results[ticker] = trades
            all_trades.extend(trades)

        print("\nStep 3/5: Evaluating conditions...")
        for ticker, trades in ticker_results.items():
            n = len(trades)
            if n:
                print(f"  {ticker}: {n} entry signals")
            else:
                print(f"  {ticker}: no entry signals")

        print("\nStep 4/5: Simulating portfolio...")
        total_trades = sum(len(t) for t in ticker_results.values())
        print(f"  Total trades executed: {total_trades}")

        print("\nStep 5/5: Computing metrics...")
        metrics = compute_metrics(all_trades, capital)

        benchmark_metrics = {}
        if not bench_df.empty and all_trades:
            dates = [t.entry_date for t in all_trades]
            start_date = min(dates)
            end_date = max(t.exit_date for t in all_trades)
            benchmark_metrics = compute_benchmark_metrics(
                bench_df, start_date, end_date
            )

        return BacktestResult(
            trades=all_trades,
            metrics=metrics,
            benchmark_metrics=benchmark_metrics,
            ticker_results=ticker_results,
            conditions=self.conditions,
            config=self.config,
        )

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

        Args:
            ticker: Stock symbol.
            df: Raw OHLCV DataFrame.

        Returns:
            DataFrame with indicator columns added.
        """
        enriched = df.copy()

        for cond in self.conditions:
            series = compute_indicator(
                enriched, cond.indicator, cond.params, cond.component
            )
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
        self, ticker: str, df: pd.DataFrame
    ) -> list[Trade]:
        """Simulate trades for a single ticker.

        Entry: all conditions simultaneously true.
        Exit: after hold_period bars or stop-loss trigger.

        Args:
            ticker: Stock symbol.
            df: DataFrame with indicator columns.

        Returns:
            List of completed trades.
        """
        trades: list[Trade] = []
        hold = self.config["hold"]
        stop_loss = self.config.get("stop_loss")
        i = 0

        while i < len(df):
            if self._evaluate_conditions(df.iloc[i]):
                entry_date = df.index[i]
                entry_price = df.iloc[i]["Close"]

                if pd.isna(entry_price) or entry_price <= 0:
                    i += 1
                    continue

                # Skip if hold period extends past available data
                if i + hold >= len(df):
                    break

                exit_idx = i + hold

                # Check stop-loss during hold period
                if stop_loss is not None:
                    for j in range(i + 1, min(exit_idx + 1, len(df))):
                        current_price = df.iloc[j]["Close"]
                        ret = (current_price - entry_price) / entry_price
                        if ret <= -stop_loss / 100.0:
                            exit_idx = j
                            break

                if exit_idx >= len(df):
                    break

                exit_date = df.index[exit_idx]
                exit_price = df.iloc[exit_idx]["Close"]
                ret = (exit_price - entry_price) / entry_price

                trades.append(
                    Trade(
                        ticker=ticker,
                        entry_date=entry_date,
                        entry_price=entry_price,
                        exit_date=exit_date,
                        exit_price=exit_price,
                        hold_bars=exit_idx - i,
                        return_pct=ret,
                    )
                )
                i = exit_idx + 1
            else:
                i += 1

        return trades
