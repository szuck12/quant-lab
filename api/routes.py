# api/routes.py
"""API endpoints for the QuantLab backtester."""

from __future__ import annotations

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

MAX_YEARS = 20  # yfinance max reliable history

# Indicator metadata for the frontend form
INDICATOR_SCHEMA: dict[str, dict] = {
    "ADX": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 2,
                "max": 200,
                "hint": "DI smoothing period",
            },
            {
                "name": "adx_window",
                "type": "int",
                "default": 14,
                "min": 2,
                "max": 200,
                "hint": "ADX smoothing period",
            },
        ],
        "value_hint": "0–100 (typically 20–25 for trend threshold)",
    },
    "ATR": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 2,
                "max": 200,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Positive number (price units, e.g. 2.0 for $2 ATR)",
    },
    "AV": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 500,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Volume units (e.g. 5000000 for 5M shares)",
    },
    "BB": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 500,
                "hint": "SMA period",
            },
            {
                "name": "num_std",
                "type": "float",
                "default": 2.0,
                "min": 0.5,
                "max": 5.0,
                "hint": "Standard deviations",
            },
        ],
        "value_hint": "Price level (e.g. 150 for upper band)",
    },
    "CCI": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 200,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Typical range: -200 to +200 (±100 = overbought/oversold)",
    },
    "EMA": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 500,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Price level (e.g. 150 for $150 EMA)",
    },
    "MACD": {
        "params": [
            {
                "name": "fast",
                "type": "int",
                "default": 12,
                "min": 2,
                "max": 100,
                "hint": "Fast EMA period",
            },
            {
                "name": "slow",
                "type": "int",
                "default": 26,
                "min": 5,
                "max": 200,
                "hint": "Slow EMA period",
            },
            {
                "name": "signal",
                "type": "int",
                "default": 9,
                "min": 2,
                "max": 50,
                "hint": "Signal line period",
            },
        ],
        "value_hint": "MACD units (e.g. 0 for crossover, 0.5 for momentum)",
    },
    "OBV": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 30,
                "min": 2,
                "max": 500,
                "hint": "Smoothing period",
            },
        ],
        "value_hint": "Volume units (OBV is cumulative, large numbers)",
    },
    "ROC": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 9,
                "min": 2,
                "max": 200,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Percentage (e.g. 5 for 5% change, -3 for -3%)",
    },
    "RSI": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 2,
                "max": 200,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "0–100 (30 = oversold, 70 = overbought)",
    },
    "RVOL": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 10,
                "min": 2,
                "max": 200,
                "hint": "Average volume period",
            },
        ],
        "value_hint": "Ratio (1.0 = average, 2.0 = double average)",
    },
    "SMA": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 50,
                "min": 2,
                "max": 500,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Price level (e.g. 150 for $150 SMA)",
    },
    "STOCH": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 2,
                "max": 200,
                "hint": "Lookback period",
            },
            {
                "name": "smooth_k",
                "type": "int",
                "default": 3,
                "min": 1,
                "max": 50,
                "hint": "%K smoothing",
            },
            {
                "name": "smooth_d",
                "type": "int",
                "default": 3,
                "min": 1,
                "max": 50,
                "hint": "%D smoothing",
            },
        ],
        "value_hint": "0–100 (20 = oversold, 80 = overbought)",
    },
    "VWAP": {
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 500,
                "hint": "Rolling period",
            },
        ],
        "value_hint": "Price level (e.g. 150 for $150 VWAP)",
    },
}

VALID_OPERATORS = {"<", ">", "<=", ">=", "=="}


@router.get("/indicators", response_model=list[IndicatorInfo])
def list_indicators() -> list[IndicatorInfo]:
    """Return available indicators with parameter schemas."""
    results = []
    for name in sorted(INDICATORS.keys()):
        schema = INDICATOR_SCHEMA[name]
        components = COMPONENT_MAP.get(name, ["value"])
        params = [ParamInfo(**p) for p in schema["params"]]
        value_hint = schema.get("value_hint", "")
        results.append(
            IndicatorInfo(
                name=name,
                params=params,
                components=components,
                value_hint=value_hint,
            )
        )
    return results


@router.get("/config")
def get_config() -> dict:
    """Return global backtest configuration defaults."""
    return {
        "max_years": MAX_YEARS,
        "default_years": 2,
        "default_capital": 10000,
        "default_hold": 10,
        "default_benchmark": "SPY",
    }


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest) -> BacktestResponse:
    """Run a backtest across S&P 500 and return results."""
    # Validate years
    if req.years < 1:
        raise HTTPException(
            status_code=422,
            detail="Years must be at least 1.",
        )
    if req.years > MAX_YEARS:
        # Clamp to max — don't error, just use what's available
        req.years = MAX_YEARS

    # Validate capital
    if req.capital <= 0:
        raise HTTPException(
            status_code=422,
            detail="Capital must be a positive number.",
        )
    if req.capital > 1_000_000_000:
        raise HTTPException(
            status_code=422,
            detail="Capital cannot exceed $1,000,000,000.",
        )

    # Validate conditions
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

    # Build config — universe resolution handled by the engine
    config = {
        "tickers": [],
        "hold": 10,
        "capital": req.capital,
        "benchmark": "SPY",
        "years": req.years,
        "stop_loss": None,
        "universe": "sp500",
        "max_tickers": None,
        "position_size": req.position_size,
        "position_size_base": req.position_size_base,
    }

    # Run backtest
    try:
        engine = BacktestEngine(conditions, config)
        result = engine.run()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {e}",
        )

    if not result.trades:
        raise HTTPException(
            status_code=422,
            detail="No trades generated across S&P 500. "
            "Try adjusting your conditions, using a longer "
            "period, or changing the indicator threshold.",
        )

    # Build equity curve with benchmark
    equity_curve = _build_equity_curve(result, req)

    return _to_response(result, req, equity_curve)


def _build_equity_curve(
    result: BacktestResult, req: BacktestRequest
) -> list[EquityPoint]:
    """Build aligned strategy + benchmark equity curves."""
    strategy_eq = compute_equity_curve(result.trades, req.capital)
    if strategy_eq.empty:
        return []

    # Fetch benchmark data
    pipeline = DataPipeline()
    bench_data = pipeline.fetch(["SPY"], "1d", req.years)
    bench_df = bench_data.get("SPY", pd.DataFrame())

    if bench_df.empty or bench_df["Close"].dropna().empty:
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

    bench_close = bench_df["Close"].dropna()
    bench_equity = (bench_close / bench_close.iloc[0]) * req.capital

    start = strategy_eq.index[0]
    end = strategy_eq.index[-1]
    daily_idx = pd.date_range(start=start, end=end, freq="B")

    strat_series = strategy_eq.reindex(daily_idx).ffill()
    bench_series = bench_equity.reindex(daily_idx).ffill()

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
            shares=round(t.shares, 4),
            invested=round(t.invested, 2),
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
                shares=round(t.shares, 4),
                invested=round(t.invested, 2),
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
        cash_remaining=round(m.get("cash_remaining", 0), 2),
        positions_value=round(m.get("positions_value", 0), 2),
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
