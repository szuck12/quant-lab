# backtester/__init__.py
"""QuantLab backtesting engine.

Provides batch data download, vectorized indicator computation,
strategy simulation, and performance metrics.
"""

from backtester.cli import parse_backtest_command, run_backtest
from backtester.data_pipeline import DataPipeline
from backtester.engine import BacktestEngine, BacktestResult
from backtester.metrics import compute_metrics

__all__ = [
    "DataPipeline",
    "BacktestEngine",
    "BacktestResult",
    "compute_metrics",
    "parse_backtest_command",
    "run_backtest",
]
