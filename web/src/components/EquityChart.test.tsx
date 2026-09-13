import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/react';
import { EquityChart } from './EquityChart';
import type { EquityPoint } from '../types';

const data: EquityPoint[] = [
  { date: '2023-01-02', strategy: 10000, benchmark: 10000 },
  { date: '2023-01-03', strategy: 10100, benchmark: 10050 },
];

describe('EquityChart', () => {
  it('renders without crashing with data', () => {
    const { container } = render(<EquityChart data={data} />);
    expect(container.querySelector('.recharts-responsive-container')).toBeTruthy();
  });

  it('returns null with no data', () => {
    const { container } = render(<EquityChart data={[]} />);
    expect(container.firstChild).toBeNull();
  });
});
