import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { App } from './App';

const mockIndicator = {
  name: 'RSI',
  description: 'Momentum oscillator (0–100)',
  params: [
    { name: 'window', type: 'int', default: 14, min: 2, max: 50,
      hint: 'Lookback period' },
  ],
  components: ['value'],
  value_hint: '0–100 (30 = oversold, 70 = overbought)',
};

function stubFetch(progressResponse: object) {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const u = String(url);
    if (u.includes('/api/indicators')) {
      return Promise.resolve({ ok: true, json: async () => [mockIndicator] });
    }
    if (u.includes('/api/config')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          max_years: 10, default_years: 5, default_capital: 10000,
        }),
      });
    }
    if (u.includes('/api/backtest/start')) {
      return Promise.resolve({ ok: true, json: async () => ({ backtest_id: 1 }) });
    }
    if (u.includes('/progress')) {
      return Promise.resolve({ ok: true, json: async () => progressResponse });
    }
    return Promise.resolve({ ok: true, json: async () => ({}) });
  }));
}

describe('App backtest error surfacing', () => {
  beforeEach(() => {
    window.location.hash = '/backtest';
  });

  it('shows the server-provided error detail', async () => {
    stubFetch({
      status: 'error',
      progress: 0,
      detail: 'No market data was returned for the selected universe.',
    });
    render(<App />);

    const runButton = await screen.findByRole(
      'button', { name: /run backtest/i },
    );
    await userEvent.click(runButton);

    await waitFor(
      () => {
        expect(
          screen.getByText(/No market data was returned/i),
        ).toBeInTheDocument();
      },
      { timeout: 4000 },
    );
  });

  it('falls back to a generic message when no detail is given', async () => {
    stubFetch({ status: 'error', progress: 0 });
    render(<App />);

    const runButton = await screen.findByRole(
      'button', { name: /run backtest/i },
    );
    await userEvent.click(runButton);

    await waitFor(
      () => {
        expect(screen.getByText(/Backtest failed/i)).toBeInTheDocument();
      },
      { timeout: 4000 },
    );
  });
});
