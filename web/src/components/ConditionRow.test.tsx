import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { ConditionRow } from './ConditionRow';
import type { IndicatorInfo, ConditionRequest } from '../types';

const indicators: IndicatorInfo[] = [
  {
    name: 'RSI',
    description: 'Momentum oscillator (0–100)',
    params: [
      { name: 'window', type: 'int', default: 14, min: 2, max: 50, hint: 'Lookback period' },
    ],
    components: ['value'],
    value_hint: '0–100 (30 = oversold, 70 = overbought)',
  },
];

const condition: ConditionRequest = {
  indicator: 'RSI',
  params: { window: 14 },
  component: null,
  operator: '<',
  value: 30,
  interval: '1d',
};

const ALL_INTERVALS = ['5m', '15m', '30m', '1h', '1d', '1wk', '1mo', '3mo'];
const INTRADAY_INTERVALS = ['5m', '15m', '30m', '1h'];

describe('ConditionRow field heights', () => {
  it('all Row 1 fields have the condition-field class', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const indicator = screen.getByRole('combobox', { name: /indicator/i });
    const operator = screen.getByRole('combobox', { name: /operator/i });
    const value = screen.getByRole('textbox', { name: /value/i });
    const interval = screen.getByRole('combobox', { name: /interval/i });

    [indicator, operator, value, interval].forEach((el) => {
      expect(el.className).toContain('condition-field');
    });
  });

  it('all Row 1 fields share identical base classes for uniform sizing', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const indicator = screen.getByRole('combobox', { name: /indicator/i });
    const operator = screen.getByRole('combobox', { name: /operator/i });
    const value = screen.getByRole('textbox', { name: /value/i });
    const interval = screen.getByRole('combobox', { name: /interval/i });

    const baseClasses = ['rounded-xl', 'border', 'px-3', 'py-2.5', 'text-sm'];

    [indicator, operator, value, interval].forEach((el) => {
      baseClasses.forEach((cls) => {
        expect(el.className).toContain(cls);
      });
    });
  });

  it('Remove button also has the condition-field class when visible', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={true}
      />,
    );

    const remove = screen.getByRole('button', { name: /remove/i });
    expect(remove.className).toContain('condition-field');
  });

  it('all Row 1 labels have the same classes', () => {
    const { container } = render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const row1 = container.querySelector('.flex.flex-wrap.items-end');
    const labels = row1!.querySelectorAll('span.font-display');

    labels.forEach((label) => {
      expect(label.className).toContain('text-xs');
      expect(label.className).toContain('font-display');
      expect(label.className).toContain('mb-1.5');
    });
  });
});

describe('ConditionRow interval dropdown', () => {
  it('renders all 8 interval options', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const interval = screen.getByRole('combobox', { name: /interval/i });
    const options = Array.from(interval.querySelectorAll('option'));
    const values = options.map((o) => o.getAttribute('value'));

    expect(values).toEqual(ALL_INTERVALS);
  });

  it('defaults to daily interval', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const interval = screen.getByRole('combobox', { name: /interval/i });
    expect(interval).toHaveValue('1d');
  });

  it('shows intraday hint for 5m interval', () => {
    render(
      <ConditionRow
        index={0}
        condition={{ ...condition, interval: '5m' }}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    expect(screen.getByText(/intraday data limited/i)).toBeInTheDocument();
  });

  it('does not show intraday hint text for daily interval', () => {
    const { container } = render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const hintSpan = container.querySelector('.h-3.text-\\[10px\\]');
    expect(hintSpan).toBeInTheDocument();
    expect(hintSpan).not.toHaveTextContent(/intraday/i);
  });

  it.each(INTRADAY_INTERVALS)('shows hint for %s interval', (interval) => {
    render(
      <ConditionRow
        index={0}
        condition={{ ...condition, interval }}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    expect(screen.getByText(/intraday data limited/i)).toBeInTheDocument();
  });

  it('hint span has fixed height for layout consistency', () => {
    const { container } = render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const hintSpan = container.querySelector('.h-3.text-\\[10px\\]');
    expect(hintSpan).toBeInTheDocument();
    expect(hintSpan?.className).toContain('h-3');
  });

  it('all Row 1 labels have h-3 spacer for consistent height', () => {
    const { container } = render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const row1 = container.querySelector('.flex.flex-wrap.items-end');
    const spacers = row1!.querySelectorAll('.condition-field ~ span.h-3');

    expect(spacers.length).toBeGreaterThanOrEqual(4);
  });
});

describe('ConditionRow indicator display', () => {
  it('shows indicator description under the indicator select', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    expect(screen.getByText(/momentum oscillator/i)).toBeInTheDocument();
  });

  it('shows value_hint under the indicator select', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    expect(screen.getByText(/30 = oversold/i)).toBeInTheDocument();
  });

  it('formats component names without underscores', () => {
    const adxIndicator: IndicatorInfo[] = [
      {
        name: 'ADX',
        description: 'Trend strength oscillator (0–100)',
        params: [
          { name: 'window', type: 'int', default: 14, min: 5, max: 50, hint: 'DI smoothing period' },
        ],
        components: ['plus_di', 'minus_di', 'adx'],
        value_hint: '0–100',
      },
    ];

    render(
      <ConditionRow
        index={0}
        condition={{ ...condition, indicator: 'ADX' }}
        indicators={adxIndicator}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    const componentSelect = screen.getByRole('combobox', { name: /component/i });
    const options = Array.from(componentSelect.querySelectorAll('option'));
    const labels = options.map((o) => o.textContent);

    expect(labels).toContain('+DI');
    expect(labels).toContain('−DI');
    expect(labels).toContain('ADX');
    expect(labels).not.toContainEqual(expect.stringContaining('_'));
  });

  it('shows Default and Range for parameter hints', () => {
    render(
      <ConditionRow
        index={0}
        condition={condition}
        indicators={indicators}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    expect(screen.getByText(/Default: 14, 2–50/)).toBeInTheDocument();
  });

  it('formats parameter names properly', () => {
    const stochIndicator: IndicatorInfo[] = [
      {
        name: 'STOCH',
        description: 'Momentum vs high-low range (0–100)',
        params: [
          { name: 'window', type: 'int', default: 14, min: 5, max: 50, hint: 'Lookback period' },
          { name: 'smooth_k', type: 'int', default: 3, min: 1, max: 20, hint: '%K smoothing' },
          { name: 'smooth_d', type: 'int', default: 3, min: 1, max: 20, hint: '%D smoothing' },
        ],
        components: ['k', 'd'],
        value_hint: '0–100',
      },
    ];

    render(
      <ConditionRow
        index={0}
        condition={{ ...condition, indicator: 'STOCH' }}
        indicators={stochIndicator}
        onChange={() => {}}
        onRemove={() => {}}
        canRemove={false}
      />,
    );

    expect(screen.getByText('Window')).toBeInTheDocument();
    expect(screen.getByText('Smooth %K')).toBeInTheDocument();
    expect(screen.getByText('Smooth %D')).toBeInTheDocument();
  });
});
