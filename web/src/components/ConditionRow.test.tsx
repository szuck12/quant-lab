import { render, screen } from '@testing-library/react';
import { ConditionRow } from './ConditionRow';
import type { IndicatorInfo, ConditionRequest } from '../types';

const indicators: IndicatorInfo[] = [
  {
    name: 'RSI',
    params: [
      { name: 'window', type: 'int', default: 14, min: 2, max: 200, hint: 'period' },
    ],
    components: ['value'],
    value_hint: '0–100',
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
