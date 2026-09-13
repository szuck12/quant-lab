# backtester/metrics.py
"""Financial performance metrics for backtesting results.

Computes standard backtesting metrics: returns, Sharpe ratio,
Sortino ratio, max drawdown, win rate, and benchmark comparison.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Trade:
    """A completed trade."""

    ticker: str
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp
    exit_price: float
    hold_bars: int
    return_pct: float
    shares: float = 0.0
    invested: float = 0.0


def compute_metrics(
    trades: list[Trade],
    capital: float,
    equity_curve: pd.Series | None = None,
    trading_days: int = 252,
) -> dict:
    """Compute all performance metrics from a list of trades.

    Args:
        trades: List of completed trades.
        capital: Starting capital in USD.
        equity_curve: Optional mark-to-market equity series. When not
            supplied it is reconstructed from the trades.
        trading_days: Trading days per year (default 252).

    Returns:
        Dict of metric name -> value.
    """
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "total_return": 0.0,
            "annualized_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "avg_trade_return": 0.0,
            "profit_factor": 0.0,
            "winning_trades": 0,
            "losing_trades": 0,
        }

    returns = [t.return_pct for t in trades]

    # Dollar P&L per trade when position data is available; otherwise
    # fall back to fractional returns (legacy trades).
    has_shares = any(t.shares > 0 for t in trades)
    if has_shares:
        pnls = [
            t.shares * (t.exit_price - t.entry_price) for t in trades
        ]
    else:
        pnls = list(returns)

    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    total_trades = len(trades)
    winning_trades = len(wins)
    losing_trades = len(losses)
    win_rate = winning_trades / total_trades if total_trades else 0.0

    # Mark-to-market equity curve (open positions included)
    equity = (
        equity_curve
        if equity_curve is not None and not equity_curve.empty
        else compute_equity_curve(trades, capital)
    )
    total_return = (
        (equity.iloc[-1] / capital) - 1.0 if not equity.empty else 0.0
    )

    # Annualize over the actual equity span. Floor at one month to
    # avoid the explosive CAGR of very short backtests.
    if not equity.empty and len(equity) >= 2:
        days = (equity.index[-1] - equity.index[0]).days
    else:
        days = (
            max(t.exit_date for t in trades)
            - min(t.entry_date for t in trades)
        ).days
    years = max(days / 365.25, 1.0 / 12.0)
    annualized = compute_annualized_return(total_return, years)

    daily_returns = equity.pct_change(fill_method=None).dropna()

    sharpe = compute_sharpe_ratio(daily_returns, trading_days)
    sortino = compute_sortino_ratio(daily_returns, trading_days)
    max_dd = compute_max_drawdown(equity)

    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss else 0.0

    avg_trade = np.mean(returns) if returns else 0.0

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "total_return": total_return,
        "annualized_return": annualized,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd,
        "avg_trade_return": avg_trade,
        "profit_factor": profit_factor,
    }


def compute_total_return(
    trades: list[Trade], capital: float
) -> float:
    """Compute total return from a portfolio of trades.

    Uses position-weighted model when trade.shares is available:
    dollar return = shares * (exit - entry) for each trade.
    Falls back to equal-weight model for legacy trades.

    Args:
        trades: List of completed trades.
        capital: Starting capital.

    Returns:
        Total return as a decimal (e.g. 0.182 for 18.2%).
    """
    if not trades:
        return 0.0

    has_position_data = any(t.shares > 0 for t in trades)
    if has_position_data:
        dollar_return = sum(
            t.shares * (t.exit_price - t.entry_price) for t in trades
        )
        return dollar_return / capital if capital else 0.0

    n = len(trades)
    avg_return = sum(t.return_pct for t in trades) / n
    return avg_return * n


def compute_annualized_return(total_return: float, years: float) -> float:
    """Annualize a total return over a number of years.

    Args:
        total_return: Total return as a decimal.
        years: Number of years.

    Returns:
        Annualized return as a decimal.
    """
    if years <= 0 or total_return <= -1.0:
        return 0.0
    return (1.0 + total_return) ** (1.0 / years) - 1.0


def compute_equity_curve(
    trades: list[Trade], capital: float
) -> pd.Series:
    """Build equity curve from trades.

    Creates a Series indexed by date showing portfolio value
    after each trade closes. Days between trades are filled
    with the last known equity value so pct_change() produces
    accurate daily returns for Sharpe/Sortino computation.

    Equity is updated by realized dollar P&L, not by compounding
    the full per-trade return on total equity. A trade only
    affects the capital it actually invested, so overlapping
    positions and partial allocations are counted correctly.

    Args:
        trades: List of completed trades.
        capital: Starting capital.

    Returns:
        Equity curve Series with one value per calendar day.
    """
    if not trades:
        return pd.Series(dtype=float)

    # Process by exit date so the curve reflects realized equity
    # chronologically and the final value includes every trade.
    sorted_trades = sorted(
        trades, key=lambda t: (t.exit_date, t.entry_date)
    )

    # Build equity at each trade exit. Equity moves by realized
    # dollar P&L only: return_pct * invested == shares * (exit-entry).
    # This prevents compounding a trade's full return on capital it
    # never deployed (overlapping or partial positions).
    exit_equity: dict[pd.Timestamp, float] = {}
    equity = capital
    for trade in sorted_trades:
        if trade.invested > 0:
            equity += trade.return_pct * trade.invested
        else:
            # Legacy trades without position data — compound as before.
            equity *= 1.0 + trade.return_pct
        exit_equity[trade.exit_date] = equity

    # Create a date range covering the full period. Include the exact
    # exit dates so no trade is dropped if it lands off a business day.
    start = min(t.entry_date for t in trades)
    end = max(t.exit_date for t in trades)
    daily_idx = pd.date_range(start=start, end=end, freq="B")
    exit_idx = pd.DatetimeIndex(list(exit_equity.keys()))
    combined = daily_idx.union(exit_idx).sort_values()

    # Map exit dates to equity values, forward-fill the rest.
    # Initialize to capital so the curve starts flat at capital.
    series = pd.Series(capital, index=combined, dtype=float)
    for ts, val in exit_equity.items():
        series.loc[ts] = val
    series = series.ffill()

    return series


def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """Maximum peak-to-trough decline.

    Args:
        equity_curve: Portfolio value over time.

    Returns:
        Max drawdown as a negative decimal (e.g. -0.15 for 15%).
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    return drawdown.min()


def compute_sharpe_ratio(
    daily_returns: pd.Series, trading_days: int = 252
) -> float:
    """Annualized Sharpe ratio (risk-free rate = 0).

    Args:
        daily_returns: Daily return series.
        trading_days: Trading days per year.

    Returns:
        Sharpe ratio.
    """
    std = daily_returns.std()
    if daily_returns.empty or std < 1e-12 or pd.isna(std):
        return 0.0
    return daily_returns.mean() / std * np.sqrt(trading_days)


def compute_sortino_ratio(
    daily_returns: pd.Series, trading_days: int = 252
) -> float:
    """Annualized Sortino ratio (downside deviation, risk-free = 0).

    Uses the textbook downside deviation over all observations:
    ``sqrt(mean(min(r, 0)^2))``. This includes zero-return days in the
    denominator, unlike taking the std of only negative returns.

    Args:
        daily_returns: Daily return series.
        trading_days: Trading days per year.

    Returns:
        Sortino ratio.
    """
    if daily_returns.empty:
        return 0.0
    downside = np.sqrt(np.mean(np.minimum(daily_returns, 0.0) ** 2))
    if not np.isfinite(downside) or downside < 1e-12:
        return 0.0
    return daily_returns.mean() / downside * np.sqrt(trading_days)


def compute_benchmark_metrics(
    benchmark_data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    trading_days: int = 252,
) -> dict:
    """Compute buy-and-hold metrics for a benchmark ticker.

    Args:
        benchmark_data: OHLCV DataFrame for the benchmark.
        start_date: Backtest start date.
        end_date: Backtest end date.
        trading_days: Trading days per year.

    Returns:
        Dict of benchmark metrics.
    """
    mask = (benchmark_data.index >= start_date) & (
        benchmark_data.index <= end_date
    )
    data = benchmark_data.loc[mask]

    if data.empty or len(data) < 2:
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
        }

    close = data["Close"].dropna()
    if len(close) < 2:
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
        }

    total_return = (close.iloc[-1] / close.iloc[0]) - 1.0
    days = (close.index[-1] - close.index[0]).days
    years = max(days / 365.25, 1.0 / 12.0)
    ann_return = compute_annualized_return(total_return, years)

    daily_rets = close.pct_change(fill_method=None).dropna()
    sharpe = compute_sharpe_ratio(daily_rets, trading_days)
    sortino = compute_sortino_ratio(daily_rets, trading_days)

    cummax = close.cummax()
    dd = (close - cummax) / cummax
    max_dd = dd.min()

    return {
        "total_return": total_return,
        "annualized_return": ann_return,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd,
    }
