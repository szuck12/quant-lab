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
    trading_days: int = 252,
) -> dict:
    """Compute all performance metrics from a list of trades.

    Args:
        trades: List of completed trades.
        capital: Starting capital in USD.
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
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r <= 0]

    total_trades = len(trades)
    winning_trades = len(wins)
    losing_trades = len(losses)
    win_rate = winning_trades / total_trades if total_trades else 0.0

    total_return = compute_total_return(trades, capital)
    n_bars = sum(t.hold_bars for t in trades)
    years = max(n_bars / trading_days, 0.01)
    annualized = compute_annualized_return(total_return, years)

    equity = compute_equity_curve(trades, capital)
    daily_returns = equity.pct_change(fill_method=None).dropna()

    sharpe = compute_sharpe_ratio(daily_returns, trading_days)
    sortino = compute_sortino_ratio(daily_returns, trading_days)
    max_dd = compute_max_drawdown(equity)

    gross_profit = sum(w for w in wins) if wins else 0.0
    gross_loss = abs(sum(l_ for l_ in losses)) if losses else 0.0
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

    Args:
        trades: List of completed trades.
        capital: Starting capital.

    Returns:
        Equity curve Series with one value per calendar day.
    """
    if not trades:
        return pd.Series(dtype=float)

    sorted_trades = sorted(trades, key=lambda t: t.entry_date)

    # Build equity at each trade exit
    exit_equity: dict[pd.Timestamp, float] = {}
    equity = capital
    for trade in sorted_trades:
        equity *= 1.0 + trade.return_pct
        exit_equity[trade.exit_date] = equity

    # Create a daily date range covering the full period
    start = sorted_trades[0].entry_date
    end = sorted_trades[-1].exit_date
    daily_idx = pd.date_range(start=start, end=end, freq="B")

    # Map exit dates to equity values, forward-fill the rest
    series = pd.Series(index=daily_idx, dtype=float)
    for ts, val in exit_equity.items():
        if ts in series.index:
            series.loc[ts] = val
    series = series.ffill()
    series.iloc[0] = capital

    return series


def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """Maximum peak-to-trough decline.

    Args:
        equity_curve: Portfolio value over time.

    Returns:
        Max drawdown as a positive decimal (e.g. 0.15 for 15%).
    """
    if equity_curve.empty or len(equity_curve) < 2:
        return 0.0
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    return abs(drawdown.min())


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
    """Annualized Sortino ratio (downside deviation only).

    Args:
        daily_returns: Daily return series.
        trading_days: Trading days per year.

    Returns:
        Sortino ratio.
    """
    if daily_returns.empty:
        return 0.0
    neg = daily_returns[daily_returns < 0]
    neg_std = neg.std()
    if neg.empty or neg_std < 1e-12 or pd.isna(neg_std):
        return 0.0
    return daily_returns.mean() / neg_std * np.sqrt(trading_days)


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
            "max_drawdown": 0.0,
        }

    total_return = (data["Close"].iloc[-1] / data["Close"].iloc[0]) - 1.0
    days = (data.index[-1] - data.index[0]).days
    years = max(days / 365.25, 0.01)
    ann_return = compute_annualized_return(total_return, years)

    daily_rets = data["Close"].pct_change().dropna()
    sharpe = compute_sharpe_ratio(daily_rets, trading_days)

    cummax = data["Close"].cummax()
    dd = (data["Close"] - cummax) / cummax
    max_dd = abs(dd.min())

    return {
        "total_return": total_return,
        "annualized_return": ann_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
    }
