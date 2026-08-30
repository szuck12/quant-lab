# backtester/reporting.py
"""Console output formatting for backtest results."""

from __future__ import annotations

from backtester.engine import BacktestResult


def format_results(result: BacktestResult) -> str:
    """Format backtest results for console display.

    Args:
        result: Complete backtest results.

    Returns:
        Formatted string ready for printing.
    """
    lines: list[str] = []
    cfg = result.config

    # Header
    lines.append("\n=== QuantLab Backtest Results ===\n")

    # Strategy summary
    cond_strs = []
    for c in result.conditions:
        parts = [c.indicator]
        if c.component:
            parts.append(c.component)
        parts.append(f"{c.operator}{_fmt_val(c.value)}")
        parts.append(c.interval)
        cond_strs.append(" ".join(parts))
    lines.append(f"Strategy: {' AND '.join(cond_strs)}")

    if result.trades:
        dates = [t.entry_date for t in result.trades]
        start = min(dates).strftime("%Y-%m-%d")
        end = max(t.exit_date for t in result.trades).strftime("%Y-%m-%d")
        lines.append(f"Period: {start} to {end}")

    lines.append(f"Capital: ${cfg['capital']:,.0f}")
    lines.append(f"Hold Period: {cfg['hold']} bars")
    lines.append(f"Benchmark: {cfg['benchmark']}")

    # Per-ticker results
    lines.append("")
    for ticker, trades in result.ticker_results.items():
        lines.append(f"--- {ticker} ---")
        if not trades:
            lines.append("  No trades")
            continue
        n = len(trades)
        wins = sum(1 for t in trades if t.return_pct > 0)
        wr = wins / n * 100 if n else 0
        avg_ret = sum(t.return_pct for t in trades) / n * 100 if n else 0
        total_ret = _ticker_total_return(trades) * 100
        lines.append(f"  Trades: {n}")
        lines.append(f"  Win Rate: {wr:.1f}%")
        lines.append(f"  Avg Return: {avg_ret:.1f}%")
        lines.append(f"  Total Return: {total_ret:.1f}%")

    # Portfolio summary
    lines.append("\n--- Portfolio Summary ---")
    m = result.metrics
    if m:
        lines.append(f"  Total Trades: {m.get('total_trades', 0)}")
        lines.append(
            f"  Win Rate: {m.get('win_rate', 0) * 100:.1f}%"
        )
        lines.append(
            f"  Total Return: {m.get('total_return', 0) * 100:.1f}%"
        )
        lines.append(
            f"  Annualized Return: "
            f"{m.get('annualized_return', 0) * 100:.1f}%"
        )
        lines.append(
            f"  Sharpe Ratio: {m.get('sharpe_ratio', 0):.2f}"
        )
        lines.append(
            f"  Sortino Ratio: {m.get('sortino_ratio', 0):.2f}"
        )
        lines.append(
            f"  Max Drawdown: {m.get('max_drawdown', 0) * 100:.1f}%"
        )
        lines.append(
            f"  Profit Factor: {m.get('profit_factor', 0):.2f}"
        )

    # Benchmark
    bm = result.benchmark_metrics
    if bm:
        lines.append(f"\n--- Benchmark ({cfg['benchmark']}) ---")
        lines.append(
            f"  Total Return: {bm.get('total_return', 0) * 100:.1f}%"
        )
        lines.append(
            f"  Annualized Return: "
            f"{bm.get('annualized_return', 0) * 100:.1f}%"
        )
        lines.append(
            f"  Sharpe Ratio: {bm.get('sharpe_ratio', 0):.2f}"
        )
        lines.append(
            f"  Max Drawdown: {bm.get('max_drawdown', 0) * 100:.1f}%"
        )

        # Comparison
        strat_ret = m.get("total_return", 0) * 100
        bench_ret = bm.get("total_return", 0) * 100
        diff = strat_ret - bench_ret
        strat_sharpe = m.get("sharpe_ratio", 0)
        bench_sharpe = bm.get("sharpe_ratio", 0)
        lines.append("\n--- vs Benchmark ---")
        ret_sign = "+" if diff >= 0 else ""
        lines.append(f"  Return delta: {ret_sign}{diff:.1f}%")
        sharpe_diff = strat_sharpe - bench_sharpe
        sharpe_sign = "+" if sharpe_diff >= 0 else ""
        lines.append(
            f"  Sharpe delta: {sharpe_sign}{sharpe_diff:.2f}"
        )

    lines.append("")
    return "\n".join(lines)


def _fmt_val(val: float) -> str:
    """Format a numeric value for display."""
    if val == int(val):
        return str(int(val))
    return f"{val:.2f}"


def _ticker_total_return(trades: list) -> float:
    """Compute total return for a single ticker's trades."""
    equity = 1.0
    for t in trades:
        equity *= 1.0 + t.return_pct
    return equity - 1.0
