# test_calculate_bb.py
# Tests for calculate_bb() using mocked stock data

import pytest
from indicators import calculate_bb


class TestCalculateBb:
    """Tests for calculate_bb()."""

    def test_basic_bb(self, mock_stock_data):
        """Verify BB matches the known value for a 6-point
        sequence with window=3, num_std=2.0."""
        mock_stock_data([10.0, 11, 12, 13, 14, 15])
        u, m, l = calculate_bb("TEST", window=3, num_std=2.0)
        assert m.iloc[-1] == 14.0
        assert u.iloc[-1] == pytest.approx(15.6330, abs=0.01)
        assert l.iloc[-1] == pytest.approx(12.3670, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify BB with window=1 collapses to the close
        price (std=0)."""
        mock_stock_data([10.0, 20])
        u, m, l = calculate_bb("TEST", window=1, num_std=2.0)
        assert u.iloc[-1] == 20.0
        assert m.iloc[-1] == 20.0
        assert l.iloc[-1] == 20.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length
        (all NaN)."""
        mock_stock_data([1.0, 2, 3])
        with pytest.raises(IndexError):
            calculate_bb("TEST", window=10, num_std=2.0)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_bb("TEST", window=5, num_std=2.0)

    def test_constant_prices(self, mock_stock_data):
        """Verify BB of constant prices collapses to the
        constant (std=0)."""
        mock_stock_data([50.0] * 10)
        u, m, l = calculate_bb("TEST", window=2, num_std=2.0)
        assert u.iloc[-1] == 50.0
        assert m.iloc[-1] == 50.0
        assert l.iloc[-1] == 50.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify BB handles a zigzag [10, 20] pattern."""
        mock_stock_data([10.0, 20, 10, 20, 10, 20, 10, 20])
        u, m, l = calculate_bb("TEST", window=3, num_std=2.0)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]

    def test_large_prices(self, mock_stock_data):
        """Verify BB handles prices around 1e9."""
        mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                         1.004e9, 1.005e9])
        u, m, l = calculate_bb("TEST", window=2, num_std=2.0)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]

    def test_negative_prices(self, mock_stock_data):
        """Verify BB handles negative prices."""
        mock_stock_data([-10.0, -9, -8, -7, -6, -5, -4, -3])
        u, m, l = calculate_bb("TEST", window=2, num_std=2.0)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]

    def test_spike_pattern(self, mock_stock_data):
        """Verify BB handles one spike in a flat series (bands
        collapse at the end when std becomes 0)."""
        mock_stock_data([10.0] * 4 + [1000] + [10] * 5)
        u, m, l = calculate_bb("TEST", window=3, num_std=2.0)
        assert u.iloc[-1] is not None
        assert m.iloc[-1] is not None
        assert l.iloc[-1] is not None

    def test_single_price_point(self, mock_stock_data):
        """Verify BB with one price collapses to that price."""
        mock_stock_data([42.0])
        u, m, l = calculate_bb("TEST", window=1, num_std=2.0)
        assert u.iloc[-1] == 42.0
        assert m.iloc[-1] == 42.0
        assert l.iloc[-1] == 42.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify BB works on a 20-point sequence."""
        mock_stock_data(list(range(20)))
        u, m, l = calculate_bb("TEST", window=5, num_std=2.0)
        assert len(u) == 1
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]

    def test_large_window(self, mock_stock_data):
        """Verify BB with a window close to data length."""
        mock_stock_data(list(range(10)))
        u, m, l = calculate_bb("TEST", window=8, num_std=2.0)
        assert len(u) == 1
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N triplets."""
        mock_stock_data(list(range(20)))
        u, m, l = calculate_bb("TEST", window=3,
                                num_std=2.0, count=3)
        assert len(u) == 3
        assert len(m) == 3
        assert len(l) == 3

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data([10.0, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_bb("TEST", window=2, num_std=2.0,
                         count=5)

    def test_custom_num_std(self, mock_stock_data):
        """Verify a wider multiplier widens the bands."""
        mock_stock_data([10.0, 11, 12, 13, 14, 15])
        u1, m, l1 = calculate_bb("TEST", window=3,
                                  num_std=1.0)
        u2, _, l2 = calculate_bb("TEST", window=3,
                                  num_std=3.0)
        assert m.iloc[-1] == 14.0
        assert u2.iloc[-1] > u1.iloc[-1]
        assert l2.iloc[-1] < l1.iloc[-1]

    def test_band_ordering(self, mock_stock_data):
        """Verify upper > middle > lower for every returned
        value."""
        mock_stock_data([10.0, 12, 14, 16, 18, 20, 22, 24])
        u, m, l = calculate_bb("TEST", window=3,
                                num_std=2.0, count=4)
        for i in range(len(u)):
            assert u.iloc[i] > m.iloc[i] > l.iloc[i]
