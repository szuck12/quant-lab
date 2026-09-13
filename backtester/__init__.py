# backtester/__init__.py
"""QuantLab backtesting engine.

Provides batch data download, vectorized indicator computation,
strategy simulation, and performance metrics.
"""

from backtester.data_pipeline import DataPipeline
from backtester.engine import BacktestEngine, BacktestResult
from backtester.metrics import compute_metrics

__all__ = [
    "DataPipeline",
    "BacktestEngine",
    "BacktestResult",
    "compute_metrics",
]
