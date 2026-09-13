# api/routes.py
"""API endpoints for the QuantLab backtester."""

from __future__ import annotations

import logging
import threading
from typing import Any

import numpy as np
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
from backtester.engine import BacktestEngine, BacktestResult
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_YEARS = 20  # yfinance max reliable history

# Customer-facing message for any unexpected internal failure. The real
# exception is logged server-side; users never see internal details.
GENERIC_BACKTEST_ERROR = (
    "Something went wrong while running your backtest. "
    "Please try again in a moment."
)

# Indicator metadata for the frontend form
INDICATOR_SCHEMA: dict[str, dict] = {
    "ADX": {
        "description": "Trend strength oscillator (0–100)",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 5,
                "max": 50,
                "hint": "DI smoothing period",
            },
            {
                "name": "adx_window",
                "type": "int",
                "default": 14,
                "min": 5,
                "max": 50,
                "hint": "ADX smoothing period",
            },
        ],
        "value_hint": "0–100 (typically 20–25 for trend threshold)",
    },
    "ATR": {
        "description": "Volatility in price units",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 5,
                "max": 50,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Positive number (price units, e.g. 2.0 for $2 ATR)",
    },
    "AV": {
        "description": "Rolling average of trading volume",
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
        "value_hint": "Volume units (e.g. 5000000 for 5M shares)",
    },
    "BB": {
        "description": "Volatility envelope around price",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 5,
                "max": 100,
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
        "description": "Price deviation from statistical mean",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 5,
                "max": 50,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Typical range: -200 to +200 (±100 = overbought/oversold)",
    },
    "EMA": {
        "description": "Exponential moving average of price",
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
        "value_hint": "Price level (e.g. 150 for $150 EMA)",
    },
    "MACD": {
        "description": "Trend-following momentum indicator",
        "params": [
            {
                "name": "fast",
                "type": "int",
                "default": 12,
                "min": 2,
                "max": 50,
                "hint": "Fast EMA period",
            },
            {
                "name": "slow",
                "type": "int",
                "default": 26,
                "min": 10,
                "max": 100,
                "hint": "Slow EMA period",
            },
            {
                "name": "signal",
                "type": "int",
                "default": 9,
                "min": 2,
                "max": 30,
                "hint": "Signal line period",
            },
        ],
        "value_hint": "MACD units (e.g. 0 for crossover, 0.5 for momentum)",
    },
    "OBV": {
        "description": "Cumulative volume momentum",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 30,
                "min": 2,
                "max": 200,
                "hint": "Smoothing period",
            },
        ],
        "value_hint": "Volume units (OBV is cumulative, large numbers)",
    },
    "ROC": {
        "description": "Price rate of change over N bars",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 9,
                "min": 2,
                "max": 50,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Percentage (e.g. 5 for 5% change, -3 for -3%)",
    },
    "RSI": {
        "description": "Momentum oscillator (0–100)",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 2,
                "max": 50,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "0–100 (30 = oversold, 70 = overbought)",
    },
    "RVOL": {
        "description": "Volume relative to its average",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 10,
                "min": 2,
                "max": 50,
                "hint": "Average volume period",
            },
        ],
        "value_hint": "Ratio (1.0 = average, 2.0 = double average)",
    },
    "SMA": {
        "description": "Simple moving average of price",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 50,
                "min": 2,
                "max": 200,
                "hint": "Lookback period",
            },
        ],
        "value_hint": "Price level (e.g. 150 for $150 SMA)",
    },
    "STOCH": {
        "description": "Momentum vs high-low range (0–100)",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 14,
                "min": 5,
                "max": 50,
                "hint": "Lookback period",
            },
            {
                "name": "smooth_k",
                "type": "int",
                "default": 3,
                "min": 1,
                "max": 20,
                "hint": "%K smoothing",
            },
            {
                "name": "smooth_d",
                "type": "int",
                "default": 3,
                "min": 1,
                "max": 20,
                "hint": "%D smoothing",
            },
        ],
        "value_hint": "0–100 (20 = oversold, 80 = overbought)",
    },
    "VWAP": {
        "description": "Volume-weighted average price",
        "params": [
            {
                "name": "window",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 200,
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
        description = schema.get("description", "")
        results.append(
            IndicatorInfo(
                name=name,
                description=description,
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
    if req.years <= 0:
        raise HTTPException(
            status_code=422,
            detail="Years must be greater than 0.",
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
    except HTTPException:
        raise
    except Exception:
        logger.exception("Backtest failed")
        raise HTTPException(
            status_code=500,
            detail=GENERIC_BACKTEST_ERROR,
        )

    if not result.trades:
        raise HTTPException(
            status_code=422,
            detail=result.reason
            or "No trades were generated for this configuration.",
        )

    # Build equity curve with benchmark
    equity_curve = _build_equity_curve(result, req)

    return _to_response(result, req, equity_curve)


MAX_EQUITY_POINTS = 100


def _naive_date_index(index: pd.Index) -> pd.DatetimeIndex:
    """Return a tz-naive, normalized DatetimeIndex."""
    idx = pd.DatetimeIndex(index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    return idx.normalize()


def _build_equity_curve(
    result: BacktestResult, req: BacktestRequest
) -> list[EquityPoint]:
    """Build aligned, downsampled strategy + benchmark equity curves.

    Both series start at the requested capital on the strategy's first
    date so they can be compared directly. The benchmark is the S&P 500
    proxy (SPY) already fetched by the engine. Timezone-aware strategy
    indexes (intraday) are normalized to naive dates so they align with
    the daily benchmark.
    """
    strategy_eq = result.equity_curve
    if strategy_eq is None or strategy_eq.empty:
        return []

    # Normalize to one point per calendar date (intraday strategies
    # collapse to their daily close). Strip timezones first.
    strat_daily = pd.Series(
        strategy_eq.to_numpy(dtype=float),
        index=_naive_date_index(strategy_eq.index),
    )
    strat_daily = strat_daily.groupby(level=0).last()

    bench_df = result.benchmark_df
    close = pd.Series(dtype=float)
    if bench_df is not None and not bench_df.empty:
        try:
            close_col = bench_df["Close"]
        except KeyError:
            close_col = None
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0] if close_col.shape[1] else None
        if close_col is not None:
            close = pd.Series(
                pd.to_numeric(close_col, errors="coerce").to_numpy(),
                index=_naive_date_index(bench_df.index),
            ).dropna()

    if close.empty:
        bench_daily = pd.Series(req.capital, index=strat_daily.index)
    else:
        close_daily = close.groupby(level=0).last()
        aligned = close_daily.reindex(strat_daily.index).ffill().bfill()
        base = aligned.iloc[0] if len(aligned) else float("nan")
        if pd.isna(base) or base <= 0:
            bench_daily = pd.Series(
                req.capital, index=strat_daily.index
            )
        else:
            bench_daily = (aligned / base) * req.capital

    # Downsample to at most MAX_EQUITY_POINTS, always keeping the last.
    n = len(strat_daily)
    if n > MAX_EQUITY_POINTS:
        idx = np.unique(
            np.linspace(0, n - 1, MAX_EQUITY_POINTS).round().astype(int)
        )
        strat_daily = strat_daily.iloc[idx]
        bench_daily = bench_daily.iloc[idx]

    points: list[EquityPoint] = []
    for ts in strat_daily.index:
        s_val = strat_daily.loc[ts]
        b_val = bench_daily.get(ts, req.capital)
        if pd.isna(s_val):
            s_val = req.capital
        if pd.isna(b_val):
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
        sortino_ratio=round(bm.get("sortino_ratio", 0), 4),
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


# -- Progress tracking for background backtests --

_backtest_counter = 0
_backtest_lock = threading.Lock()
_backtest_progress: dict[int, dict[str, Any]] = {}


def _next_backtest_id() -> int:
    global _backtest_counter
    with _backtest_lock:
        _backtest_counter += 1
        return _backtest_counter


def _build_conditions_and_config(req: BacktestRequest):
    """Build engine conditions and config from a request."""
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
    return conditions, config


def _run_backtest_background(
    backtest_id: int,
    req: BacktestRequest,
) -> None:
    """Run backtest in a background thread with progress tracking."""
    try:
        conditions, config = _build_conditions_and_config(req)
        engine = BacktestEngine(conditions, config)

        def on_progress(pct: int) -> None:
            _backtest_progress[backtest_id]["progress"] = pct

        result = engine.run(on_progress=on_progress)

        if not result.trades:
            detail = (
                result.reason
                or "No trades were generated for this configuration."
            )
            _backtest_progress[backtest_id].update(
                {"status": "error", "detail": detail}
            )
            return

        equity_curve = _build_equity_curve(result, req)
        response = _to_response(result, req, equity_curve)

        _backtest_progress[backtest_id].update(
            {"status": "done", "progress": 100, "result": response}
        )
    except Exception:
        logger.exception("Background backtest %s failed", backtest_id)
        _backtest_progress[backtest_id].update(
            {"status": "error", "detail": GENERIC_BACKTEST_ERROR}
        )


@router.post("/backtest/start")
def start_backtest(req: BacktestRequest) -> dict[str, int]:
    """Start a backtest in the background, return backtest_id."""
    if req.years <= 0:
        raise HTTPException(
            status_code=422,
            detail="Years must be greater than 0.",
        )
    if req.years > MAX_YEARS:
        req.years = MAX_YEARS
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
    for cond in req.conditions:
        if cond.operator not in VALID_OPERATORS:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid operator '{cond.operator}'.",
            )
        if cond.indicator not in INDICATORS:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown indicator '{cond.indicator}'.",
            )

    backtest_id = _next_backtest_id()
    _backtest_progress[backtest_id] = {
        "status": "running",
        "progress": 0,
    }

    thread = threading.Thread(
        target=_run_backtest_background,
        args=(backtest_id, req),
        daemon=True,
    )
    thread.start()

    return {"backtest_id": backtest_id}


@router.get("/backtest/{backtest_id}/progress")
def get_backtest_progress(backtest_id: int) -> dict[str, Any]:
    """Return current progress of a background backtest."""
    info = _backtest_progress.get(backtest_id)
    if info is None:
        raise HTTPException(
            status_code=404, detail="Backtest not found."
        )
    return {
        "status": info["status"],
        "progress": info["progress"],
        "detail": info.get("detail"),
    }


@router.get("/backtest/{backtest_id}/result")
def get_backtest_result(backtest_id: int) -> BacktestResponse:
    """Return results of a completed backtest."""
    info = _backtest_progress.get(backtest_id)
    if info is None:
        raise HTTPException(
            status_code=404, detail="Backtest not found."
        )
    if info["status"] == "running":
        raise HTTPException(
            status_code=202, detail="Backtest still running."
        )
    if info["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail=info.get("detail", "Backtest failed."),
        )
    return info["result"]
