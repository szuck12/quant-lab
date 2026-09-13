import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BacktestForm } from './BacktestForm';

const mockIndicator = {
  name: 'RSI',
  description: 'Momentum oscillator (0–100)',
  params: [{ name: 'window', type: 'int', default: 14, min: 2, max: 50, hint: 'Lookback period' }],
  components: ['value'],
  value_hint: '0–100 (30 = oversold, 70 = overbought)',
};

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
    if (url.includes('/api/indicators')) {
      return Promise.resolve({ ok: true, json: async () => [mockIndicator] });
    }
    if (url.includes('/api/config')) {
      return Promise.resolve({ ok: true, json: async () => ({ max_years: 10, default_years: 5, default_capital: 10000 }) });
    }
    return Promise.resolve({ ok: true, json: async () => ({}) });
  }));
});

describe('BacktestForm number inputs', () => {
  it('renders number inputs for years and position size', async () => {
    render(<BacktestForm loading={false} onSubmit={() => {}} />);

    const yearsInput = await screen.findByRole('spinbutton', { name: /last n years/i });
    const positionInput = screen.getByRole('spinbutton', { name: /position size/i });

    expect(yearsInput.getAttribute('type')).toBe('number');
    expect(positionInput.getAttribute('type')).toBe('number');
  });

  it('years input has step="any" for decimal support', async () => {
    render(<BacktestForm loading={false} onSubmit={() => {}} />);

    const yearsInput = await screen.findByRole('spinbutton', { name: /last n years/i });
    expect(yearsInput.getAttribute('step')).toBe('any');
  });

  it('years input allows min of 0', async () => {
    render(<BacktestForm loading={false} onSubmit={() => {}} />);

    const yearsInput = await screen.findByRole('spinbutton', { name: /last n years/i });
    expect(yearsInput.getAttribute('min')).toBe('0');
  });
});

describe('MetricsTable benchmark display', () => {
  it('shows "Benchmark (SPY)" as column header', async () => {
    const { MetricsTable } = await import('./MetricsTable');
    const strategy = {
      total_trades: 10, winning_trades: 6, losing_trades: 4,
      win_rate: 0.6, total_return: 0.15, annualized_return: 0.1,
      sharpe_ratio: 1.2, sortino_ratio: 1.5, max_drawdown: -0.05,
      profit_factor: 2.0, avg_trade_return: 0.015,
      cash_remaining: 5000, positions_value: 6500,
    };
    const benchmark = {
      total_trades: 0, winning_trades: 0, losing_trades: 0,
      win_rate: 0, total_return: 0.08, annualized_return: 0.06,
      sharpe_ratio: 0.8, sortino_ratio: 0.9, max_drawdown: -0.03,
      profit_factor: 0, avg_trade_return: 0,
      cash_remaining: 0, positions_value: 0,
    };
    render(
      <table>
        <MetricsTable strategy={strategy} benchmark={benchmark} />
      </table>,
    );
    expect(screen.getByText('Benchmark (SPY)')).toBeInTheDocument();
  });
});
