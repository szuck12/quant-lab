# api/schemas.py
"""Pydantic request/response models for the QuantLab API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# -- Indicator metadata --


class ParamInfo(BaseModel):
    """Parameter definition for an indicator."""

    name: str
    type: str  # "int" or "float"
    default: float
    min: float | None = None
    max: float | None = None
    hint: str = ""  # human-readable description


class IndicatorInfo(BaseModel):
    """Available indicator with its parameter schema."""

    name: str
    params: list[ParamInfo]
    components: list[str]
    value_hint: str = ""  # suggested range for the comparison value


# -- Request models --


class ConditionRequest(BaseModel):
    """A single backtest condition."""

    indicator: str
    params: dict[str, float] = Field(default_factory=dict)
    component: str | None = None
    operator: str
    value: float
    interval: str = "1d"


class BacktestRequest(BaseModel):
    """Full backtest configuration. Tickers are always S&P 500."""

    conditions: list[ConditionRequest] = Field(min_length=1)
    capital: float = Field(default=10000, gt=0, le=1_000_000_000)
    years: int = Field(default=2, ge=1, le=100)
    position_size: float = Field(default=100, ge=0, le=100)
    position_size_base: str = Field(
        default="total", pattern="^(total|unallocated)$"
    )


# -- Response models --


class TradeResponse(BaseModel):
    """A completed trade."""

    ticker: str
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    hold_bars: int
    return_pct: float
    shares: float = 0.0
    invested: float = 0.0


class MetricsResponse(BaseModel):
    """Portfolio performance metrics."""

    total_trades: int
    win_rate: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    profit_factor: float
    avg_trade_return: float
    cash_remaining: float = 0.0
    positions_value: float = 0.0


class EquityPoint(BaseModel):
    """Single point on the equity curve chart."""

    date: str
    strategy: float
    benchmark: float


class BacktestResponse(BaseModel):
    """Complete backtest results for the frontend."""

    trades: list[TradeResponse]
    metrics: MetricsResponse
    benchmark_metrics: MetricsResponse
    equity_curve: list[EquityPoint]
    ticker_results: dict[str, list[TradeResponse]]
    conditions: list[ConditionRequest]
    config: dict
