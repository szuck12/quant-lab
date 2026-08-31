# api/routes.py
"""API endpoints for the QuantLab backtester."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from api.schemas import (
    BacktestRequest,
    BacktestResponse,
    ConditionRequest,
    EquityPoint,
    IndicatorInfo,
    MetricsResponse,
    ParamInfo,
    TradeResponse,
)
from backtester.batch_indicators import COMPONENT_MAP, INDICATORS
from backtester.data_pipeline import DataPipeline
from backtester.engine import BacktestEngine, BacktestResult
from backtester.metrics import compute_equity_curve
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Indicator metadata for the frontend form
INDICATOR_SCHEMA: dict[str, dict] = {
    "ADX": {
        "params": [
            {"name": "window", "type": "int", "default": 14, "min": 2, "max": 200},
            {"name": "adx_window", "type": "int", "default": 14, "min": 2, "max": 200},
        ],
    },
    "ATR": {
        "params": [
            {"name": "window", "type": "int", "default": 14, "min": 2, "max": 200},
        ],
    },
    "AV": {
        "params": [
            {"name": "window", "type": "int", "default": 20, "min": 2, "max": 500},
        ],
    },
    "BB": {
        "params": [
            {"name": "window", "type": "int", "default": 20, "min": 2, "max": 500},
            {"name": "num_std", "type": "float", "default": 2.0, "min": 0.5, "max": 5.0},
        ],
    },
    "CCI": {
        "params": [
            {"name": "window", "type": "int", "default": 20, "min": 2, "max": 200},
        ],
    },
    "EMA": {
        "params": [
            {"name": "window", "type": "int", "default": 20, "min": 2, "max": 500},
        ],
    },
    "MACD": {
        "params": [
            {"name": "fast", "type": "int", "default": 12, "min": 2, "max": 100},
            {"name": "slow", "type": "int", "default": 26, "min": 5, "max": 200},
            {"name": "signal", "type": "int", "default": 9, "min": 2, "max": 50},
        ],
    },
    "OBV": {
        "params": [
            {"name": "window", "type": "int", "default": 30, "min": 2, "max": 500},
        ],
    },
    "ROC": {
        "params": [
            {"name": "window", "type": "int", "default": 9, "min": 2, "max": 200},
        ],
    },
    "RSI": {
        "params": [
            {"name": "window", "type": "int", "default": 14, "min": 2, "max": 200},
        ],
    },
    "RVOL": {
        "params": [
            {"name": "window", "type": "int", "default": 10, "min": 2, "max": 200},
        ],
    },
    "SMA": {
        "params": [
            {"name": "window", "type": "int", "default": 50, "min": 2, "max": 500},
        ],
    },
    "STOCH": {
        "params": [
            {"name": "window", "type": "int", "default": 14, "min": 2, "max": 200},
            {"name": "smooth_k", "type": "int", "default": 3, "min": 1, "max": 50},
            {"name": "smooth_d", "type": "int", "default": 3, "min": 1, "max": 50},
        ],
    },
    "VWAP": {
        "params": [
            {"name": "window", "type": "int", "default": 20, "min": 2, "max": 500},
        ],
    },
}

# Period options for the frontend
PERIOD_OPTIONS = [
    {"label": "1 Month", "value": "1mo", "months": 1},
    {"label": "3 Months", "value": "3mo", "months": 3},
    {"label": "6 Months", "value": "6mo", "months": 6},
    {"label": "1 Year", "value": "1yr", "months": 12},
    {"label": "2 Years", "value": "2yr", "months": 24},
    {"label": "3 Years", "value": "3yr", "months": 36},
    {"label": "5 Years", "value": "5yr", "months": 60},
    {"label": "10 Years", "value": "10yr", "months": 120},
    {"label": "15 Years", "value": "15yr", "months": 180},
    {"label": "20 Years", "value": "20yr", "months": 240},
]

VALID_OPERATORS = {"<", ">", "<=", ">=", "=="}


@router.get("/indicators", response_model=list[IndicatorInfo])
def list_indicators() -> list[IndicatorInfo]:
    """Return available indicators with parameter schemas."""
    results = []
    for name in sorted(INDICATORS.keys()):
        schema = INDICATOR_SCHEMA[name]
        components = COMPONENT_MAP.get(name, ["value"])
        params = [ParamInfo(**p) for p in schema["params"]]
        results.append(
            IndicatorInfo(name=name, params=params, components=components)
        )
    return results


@router.get("/periods")
def list_periods() -> list[dict]:
    """Return available analysis periods."""
    return PERIOD_OPTIONS


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest) -> BacktestResponse:
    """Run a backtest and return results."""
    # Validate operators
    for cond in req.conditions:
        if cond.operator not in VALID_OPERATORS:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid operator '{cond.operator}'. "
                f"Valid: {', '.join(sorted(VALID_OPERATORS))}",
            )
        if cond.indicator not in INDICATORS:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown indicator '{cond.indicator}'. "
                f"Valid: {', '.join(sorted(INDICATORS.keys()))}",
            )

    # Validate tickers
    import re

    ticker_re = re.compile(r"^[A-Z0-9.\-]{1,10}$")
    for t in req.tickers:
        if not ticker_re.match(t) or not any(c.isalpha() for c in t):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid ticker '{t}'. Must be 1-10 alphanumeric "
                "characters with at least one letter.",
            )

    # Convert period to start/end dates
    period_months = _get_period_months(req.years)
    end_date = datetime.now()
    _start_date = end_date - timedelta(days=period_months * 30)

    # Build conditions
    from backtester.engine import Condition

    conditions = []
    for c in req.conditions:
        params = tuple(c.params.values()) if c.params else ()
        conditions.append(
            Condition(
                indicator=c.indicator.upper(),
                params=params,
                component=c.component,
                operator=c.operator,
                value=c.value,
                interval=c.interval,
            )
        )

    # Build config
    config = {
        "tickers": req.tickers,
        "hold": req.hold,
        "capital": req.capital,
        "benchmark": req.benchmark,
        "years": req.years,
        "stop_loss": req.stop_loss,
        "universe": None,
        "max_tickers": req.max_tickers,
    }

    # Run backtest
    try:
        engine = BacktestEngine(conditions, config)
        result = engine.run()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not result.trades:
        raise HTTPException(
            status_code=422,
            detail="No trades generated. Try adjusting your conditions "
            "or using a longer analysis period.",
        )

    # Build equity curve with benchmark
    equity_curve = _build_equity_curve(result, req)

    return _to_response(result, req, equity_curve)


def _get_period_months(years: int) -> int:
    """Convert years to approximate months."""
    for opt in PERIOD_OPTIONS:
        if opt["value"] == f"{years}yr":
            return opt["months"]
    return years * 12


def _build_equity_curve(
    result: BacktestResult, req: BacktestRequest
) -> list[EquityPoint]:
    """Build aligned strategy + benchmark equity curves."""
    strategy_eq = compute_equity_curve(result.trades, req.capital)
    if strategy_eq.empty:
        return []

    # Fetch benchmark data
    pipeline = DataPipeline()
    interval = "1d"
    bench_data = pipeline.fetch(
        [req.benchmark], interval, req.years
    )
    bench_df = bench_data.get(req.benchmark, pd.DataFrame())

    if bench_df.empty:
        # No benchmark data — just strategy
        points = []
        for ts, val in strategy_eq.items():
            safe_val = req.capital if pd.isna(val) else float(val)
            points.append(
                EquityPoint(
                    date=ts.strftime("%Y-%m-%d"),
                    strategy=round(safe_val, 2),
                    benchmark=round(req.capital, 2),
                )
            )
        return points

    # Compute benchmark equity: buy-and-hold
    bench_close = bench_df["Close"].dropna()
    if bench_close.empty:
        points = []
        for ts, val in strategy_eq.items():
            points.append(
                EquityPoint(
                    date=ts.strftime("%Y-%m-%d"),
                    strategy=round(val, 2),
                    benchmark=round(req.capital, 2),
                )
            )
        return points

    bench_equity = (bench_close / bench_close.iloc[0]) * req.capital

    # Resample both to business days and align
    start = strategy_eq.index[0]
    end = strategy_eq.index[-1]
    daily_idx = pd.date_range(start=start, end=end, freq="B")

    strat_series = strategy_eq.reindex(daily_idx).ffill()
    bench_series = bench_equity.reindex(daily_idx).ffill()

    # Fill any remaining NaN at start
    strat_series = strat_series.fillna(req.capital)
    bench_series = bench_series.fillna(req.capital)

    points = []
    for ts in daily_idx:
        s_val = strat_series.get(ts)
        if s_val is None or pd.isna(s_val):
            s_val = req.capital
        b_val = bench_series.get(ts)
        if b_val is None or pd.isna(b_val):
            b_val = req.capital
        points.append(
            EquityPoint(
                date=ts.strftime("%Y-%m-%d"),
                strategy=round(float(s_val), 2),
                benchmark=round(float(b_val), 2),
            )
        )
    return points


def _to_response(
    result: BacktestResult,
    req: BacktestRequest,
    equity_curve: list[EquityPoint],
) -> BacktestResponse:
    """Convert BacktestResult to API response."""
    trades = [
        TradeResponse(
            ticker=t.ticker,
            entry_date=t.entry_date.strftime("%Y-%m-%d"),
            entry_price=round(t.entry_price, 2),
            exit_date=t.exit_date.strftime("%Y-%m-%d"),
            exit_price=round(t.exit_price, 2),
            hold_bars=t.hold_bars,
            return_pct=round(t.return_pct, 6),
        )
        for t in result.trades
    ]

    ticker_results: dict[str, list[TradeResponse]] = {}
    for ticker, ticker_trades in result.ticker_results.items():
        ticker_results[ticker] = [
            TradeResponse(
                ticker=t.ticker,
                entry_date=t.entry_date.strftime("%Y-%m-%d"),
                entry_price=round(t.entry_price, 2),
                exit_date=t.exit_date.strftime("%Y-%m-%d"),
                exit_price=round(t.exit_price, 2),
                hold_bars=t.hold_bars,
                return_pct=round(t.return_pct, 6),
            )
            for t in ticker_trades
        ]

    m = result.metrics
    metrics = MetricsResponse(
        total_trades=m.get("total_trades", 0),
        win_rate=round(m.get("win_rate", 0), 4),
        total_return=round(m.get("total_return", 0), 6),
        annualized_return=round(m.get("annualized_return", 0), 6),
        sharpe_ratio=round(m.get("sharpe_ratio", 0), 4),
        sortino_ratio=round(m.get("sortino_ratio", 0), 4),
        max_drawdown=round(m.get("max_drawdown", 0), 6),
        profit_factor=round(m.get("profit_factor", 0), 4),
        avg_trade_return=round(m.get("avg_trade_return", 0), 6),
    )

    bm = result.benchmark_metrics
    benchmark_metrics = MetricsResponse(
        total_trades=0,
        win_rate=0.0,
        total_return=round(bm.get("total_return", 0), 6),
        annualized_return=round(bm.get("annualized_return", 0), 6),
        sharpe_ratio=round(bm.get("sharpe_ratio", 0), 4),
        sortino_ratio=0.0,
        max_drawdown=round(bm.get("max_drawdown", 0), 6),
        profit_factor=0.0,
        avg_trade_return=0.0,
    )

    conditions = [
        ConditionRequest(
            indicator=c.indicator,
            params=dict(zip(_param_names(c), c.params))
            if c.params
            else {},
            component=c.component,
            operator=c.operator,
            value=c.value,
            interval=c.interval,
        )
        for c in result.conditions
    ]

    return BacktestResponse(
        trades=trades,
        metrics=metrics,
        benchmark_metrics=benchmark_metrics,
        equity_curve=equity_curve,
        ticker_results=ticker_results,
        conditions=conditions,
        config=result.config,
    )


def _param_names(cond) -> list[str]:
    """Get parameter names for a condition based on its indicator."""
    schema = INDICATOR_SCHEMA.get(cond.indicator, {})
    params = schema.get("params", [])
    return [p["name"] for p in params[: len(cond.params)]]
