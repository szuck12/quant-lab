import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MetricsTable } from './MetricsTable';
import type { MetricsResponse } from '../types';

const strategy: MetricsResponse = {
  total_trades: 10,
  win_rate: 0.6, total_return: 0.15, annualized_return: 0.1,
  sharpe_ratio: 1.2, sortino_ratio: 1.5, max_drawdown: -0.05,
  profit_factor: 2.0, avg_trade_return: 0.015,
  cash_remaining: 5000, positions_value: 6500,
};

const benchmark: MetricsResponse = {
  total_trades: 0,
  win_rate: 0, total_return: 0.08, annualized_return: 0.06,
  sharpe_ratio: 0.8, sortino_ratio: 0.9, max_drawdown: -0.03,
  profit_factor: 0, avg_trade_return: 0,
  cash_remaining: 0, positions_value: 0,
};

function renderTable() {
  return render(
    <table>
      <MetricsTable strategy={strategy} benchmark={benchmark} />
    </table>,
  );
}

describe('MetricsTable', () => {
  it('shows the Benchmark (SPY) column header', () => {
    renderTable();
    expect(screen.getByText('Benchmark (SPY)')).toBeInTheDocument();
  });

  it('does not render a Profit factor row', () => {
    renderTable();
    expect(screen.queryByText(/profit factor/i)).not.toBeInTheDocument();
  });

  it('shows N/A for benchmark-only-irrelevant metrics', () => {
    renderTable();
    // Total trades, Win rate, Avg trade return = 3 N/A cells
    expect(screen.getAllByText('N/A')).toHaveLength(3);
  });

  it('renders win rate without a plus sign', () => {
    renderTable();
    expect(screen.getByText('60.00%')).toBeInTheDocument();
    expect(screen.queryByText('+60.00%')).not.toBeInTheDocument();
  });

  it('keeps signed percentages for total return', () => {
    renderTable();
    expect(screen.getByText('+15.00%')).toBeInTheDocument();
  });

  it('uses no green/red coloring in the metrics table', () => {
    const { container } = renderTable();
    expect(container.querySelector('.text-emerald-600')).toBeNull();
    expect(container.querySelector('.text-red-500')).toBeNull();
  });
});
