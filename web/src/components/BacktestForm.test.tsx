import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BacktestForm } from './BacktestForm';

const mockIndicator = {
  name: 'RSI',
  params: [{ name: 'window', type: 'int', default: 14, min: 2, max: 200, hint: 'period' }],
  components: ['value'],
  value_hint: '0–100',
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
});
