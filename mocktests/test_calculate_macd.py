# test_calculate_macd.py
# Tests for calculate_macd() using mocked stock data

import pytest
from indicators import calculate_macd


class TestCalculateMacd:
    """Tests for calculate_macd()."""

    def test_basic_macd(self, mock_stock_data):
        """Verify MACD matches the known value for a 6-point
        sequence with fast=3, slow=5, signal=2."""
        mock_stock_data([10.0, 11, 12, 13, 14, 15])
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2)
        assert m.iloc[-1] == pytest.approx(0.7679, abs=0.01)
        assert s.iloc[-1] == pytest.approx(0.7100, abs=0.01)
        assert h.iloc[-1] == pytest.approx(0.0579, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify MACD with fast=1, slow=2, signal=1 on a
        rising 2-point series."""
        mock_stock_data([10.0, 20])
        m, s, h = calculate_macd("TEST", fast=1, slow=2,
                                 signal=1)
        assert m.iloc[-1] == pytest.approx(3.3333, abs=0.001)
        assert s.iloc[-1] == pytest.approx(3.3333, abs=0.001)
        assert h.iloc[-1] == pytest.approx(0.0, abs=0.001)

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify MACD still produces a result when slow
        exceeds data length (EMAs never produce NaN with
        adjust=False)."""
        mock_stock_data([1.0, 2, 3])
        m, s, h = calculate_macd("TEST", fast=3, slow=10,
                                 signal=2)
        assert m.iloc[-1] is not None
        assert s.iloc[-1] is not None
        assert h.iloc[-1] is not None

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_macd("TEST", fast=3, slow=5, signal=2)

    def test_constant_prices(self, mock_stock_data):
        """Verify MACD of constant prices is all zeros."""
        mock_stock_data([50.0] * 10)
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2)
        assert m.iloc[-1] == 0.0
        assert s.iloc[-1] == 0.0
        assert h.iloc[-1] == 0.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify MACD handles a zigzag [10, 20] pattern."""
        mock_stock_data([10.0, 20, 10, 20, 10, 20, 10, 20])
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2)
        assert m.iloc[-1] == pytest.approx(0.8747, abs=0.01)
        assert s.iloc[-1] == pytest.approx(0.5942, abs=0.01)
        assert h.iloc[-1] == pytest.approx(0.2806, abs=0.01)

    def test_large_prices(self, mock_stock_data):
        """Verify MACD handles prices around 1e9."""
        mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                         1.004e9, 1.005e9])
        m, s, h = calculate_macd("TEST", fast=2, slow=4,
                                 signal=2)
        assert m.iloc[-1] > 0.0

    def test_negative_prices(self, mock_stock_data):
        """Verify MACD handles negative prices."""
        mock_stock_data([-10.0, -9, -8, -7, -6, -5, -4, -3])
        m, s, h = calculate_macd("TEST", fast=2, slow=4,
                                 signal=2)
        assert m.iloc[-1] > 0.0

    def test_spike_pattern(self, mock_stock_data):
        """Verify MACD handles one spike in a flat series."""
        mock_stock_data([10.0] * 4 + [1000] + [10] * 5)
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2)
        # Spike pushes MACD negative, then it recovers
        assert s.iloc[-1] is not None

    def test_single_price_point(self, mock_stock_data):
        """Verify MACD with one price point returns all zeros
        (EMAs equal each other, MACD=0)."""
        mock_stock_data([42.0])
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2)
        assert m.iloc[-1] == 0.0
        assert s.iloc[-1] == 0.0
        assert h.iloc[-1] == 0.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify MACD works on a 20-point sequence."""
        mock_stock_data(list(range(20)))
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2)
        assert len(m) == 1
        assert m.iloc[-1] > 0.0

    def test_large_window(self, mock_stock_data):
        """Verify MACD with a slow close to data length."""
        mock_stock_data(list(range(10)))
        m, s, h = calculate_macd("TEST", fast=2, slow=8,
                                 signal=2)
        assert len(m) == 1
        assert m.iloc[-1] is not None

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N triplets."""
        mock_stock_data(list(range(20)))
        m, s, h = calculate_macd("TEST", fast=3, slow=5,
                                 signal=2, count=3)
        assert len(m) == 3
        assert len(s) == 3
        assert len(h) == 3

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data([10.0, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_macd("TEST", fast=3, slow=5, signal=2,
                           count=5)

    def test_fast_equals_slow(self, mock_stock_data):
        """Verify MACD is all zeros when fast equals slow."""
        mock_stock_data([10.0, 11, 12, 13, 14, 15])
        m, s, h = calculate_macd("TEST", fast=5, slow=5,
                                 signal=2)
        assert m.iloc[-1] == 0.0
        assert s.iloc[-1] == 0.0
        assert h.iloc[-1] == 0.0

    def test_rising_series(self, mock_stock_data):
        """Verify MACD produces positive values on a uniformly
        rising series."""
        mock_stock_data([10.0, 12, 14, 16, 18, 20, 22, 24])
        m, s, h = calculate_macd("TEST", fast=2, slow=4,
                                  signal=2)
        assert m.iloc[-1] == pytest.approx(1.9165, abs=0.01)
        assert s.iloc[-1] == pytest.approx(1.8773, abs=0.01)
        assert h.iloc[-1] == pytest.approx(0.0392, abs=0.01)

    def test_macd_crossover(self, mock_stock_data):
        """Verify histogram changes sign during a trend reversal
        (MACD crosses the signal line)."""
        prices = ([10.0] * 8 + [11, 12, 13, 14, 15, 16, 17, 18,
                  19, 20] + [19, 18, 17, 16, 15, 14, 13, 12, 11,
                  10])
        mock_stock_data(prices)
        m, s, h = calculate_macd("TEST", fast=3, slow=8,
                                  signal=3, count=15)
        assert (h > 0).any(), ("Histogram should have positive"
                               " values after crossing above")
        assert (h < 0).any(), ("Histogram should have negative"
                               " values after crossing below")

    def test_histogram_consistency(self, mock_stock_data):
        """Verify histogram == macd_line - signal_line for every
        returned value."""
        mock_stock_data([10.0, 12, 14, 16, 18, 20, 22, 24])
        m, s, h = calculate_macd("TEST", fast=2, slow=4,
                                  signal=2, count=3)
        for i in range(len(h)):
            assert h.iloc[i] == pytest.approx(m.iloc[i]
                                              - s.iloc[i],
                                              abs=1e-10)

    def test_reverse_fast_slow(self, mock_stock_data):
        """Verify MACD(fast, slow) == -MACD(slow, fast)
        (mathematical identity of the difference of EMAs)."""
        mock_stock_data([10.0, 12, 14, 16, 18, 20, 22, 24])
        m1, s1, h1 = calculate_macd("TEST", fast=3, slow=7,
                                     signal=3, count=3)
        m2, s2, h2 = calculate_macd("TEST", fast=7, slow=3,
                                     signal=3, count=3)
        assert m1.iloc[-1] == pytest.approx(-m2.iloc[-1],
                                            abs=1e-10)
        assert s1.iloc[-1] == pytest.approx(-s2.iloc[-1],
                                            abs=1e-10)
        assert h1.iloc[-1] == pytest.approx(-h2.iloc[-1],
                                            abs=1e-10)
