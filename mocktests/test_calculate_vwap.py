# test_calculate_vwap.py
# Tests for calculate_vwap() using mocked stock data

import pytest
from main import calculate_vwap


class TestCalculateVwap:
    """Tests for calculate_vwap()."""

    def test_basic_vwap(self, mock_stock_data):
        """Verify VWAP matches the known value for a 6-point
        sequence with window=3."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            high_prices=[12.0, 14, 16, 18, 20, 22],
            low_prices=[10.0, 12, 14, 16, 18, 20],
            volume_prices=[100, 200, 150, 300, 250, 400],
        )
        result = calculate_vwap("TEST", window=3)
        assert result.iloc[-1] == pytest.approx(19.2105, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify VWAP with window=1 equals the typical price."""
        mock_stock_data(
            [11.0, 13],
            high_prices=[12.0, 14],
            low_prices=[10.0, 12],
            volume_prices=[100, 200],
        )
        result = calculate_vwap("TEST", window=1)
        expected_tp = (14.0 + 12.0 + 13.0) / 3.0
        assert result.iloc[-1] == expected_tp

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length."""
        mock_stock_data(
            [11.0, 13, 15],
            high_prices=[12.0, 14, 16],
            low_prices=[10.0, 12, 14],
            volume_prices=[100, 200, 150],
        )
        with pytest.raises(IndexError):
            calculate_vwap("TEST", window=10)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], high_prices=[], low_prices=[],
                        volume_prices=[])
        with pytest.raises(IndexError):
            calculate_vwap("TEST", window=5)

    def test_constant_prices(self, mock_stock_data):
        """Verify VWAP of constant prices equals the constant
        typical price."""
        n = 6
        mock_stock_data(
            [50.0] * n,
            high_prices=[50.0] * n,
            low_prices=[50.0] * n,
            volume_prices=[100, 200, 300, 400, 500, 600],
        )
        result = calculate_vwap("TEST", window=2)
        assert result.iloc[-1] == 50.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify VWAP handles a zigzag price pattern."""
        mock_stock_data(
            [11.0, 21, 11, 21, 11, 21, 11, 21],
            high_prices=[12.0, 22, 12, 22, 12, 22, 12, 22],
            low_prices=[10.0, 20, 10, 20, 10, 20, 10, 20],
            volume_prices=[100] * 8,
        )
        result = calculate_vwap("TEST", window=3)
        assert result.iloc[-1] > 0

    def test_large_prices(self, mock_stock_data):
        """Verify VWAP handles prices around 1e9."""
        n = 5
        mock_stock_data(
            [1e9 + i for i in range(n)],
            high_prices=[1.001e9 + i for i in range(n)],
            low_prices=[0.999e9 + i for i in range(n)],
            volume_prices=[1e9] * n,
        )
        result = calculate_vwap("TEST", window=2)
        assert result.iloc[-1] > 0

    def test_negative_prices(self, mock_stock_data):
        """Verify VWAP handles negative prices with positive
        volume."""
        mock_stock_data(
            [-11.0, -13, -15, -17, -19, -21, -23],
            high_prices=[-10.0, -12, -14, -16, -18, -20, -22],
            low_prices=[-12.0, -14, -16, -18, -20, -22, -24],
            volume_prices=[100, 200, 150, 300, 250, 400, 350],
        )
        result = calculate_vwap("TEST", window=3)
        assert result.iloc[-1] < 0

    def test_spike_pattern(self, mock_stock_data):
        """Verify VWAP handles one volume spike in a flat
        series."""
        n = 10
        mock_stock_data(
            [50.0] * n,
            high_prices=[51.0] * n,
            low_prices=[49.0] * n,
            volume_prices=[100] * 4 + [10000] + [100] * 5,
        )
        result = calculate_vwap("TEST", window=3)
        assert result.iloc[-1] is not None

    def test_single_price_point(self, mock_stock_data):
        """Verify VWAP with one bar equals the typical price."""
        mock_stock_data(
            [11.0],
            high_prices=[12.0],
            low_prices=[10.0],
            volume_prices=[100],
        )
        result = calculate_vwap("TEST", window=1)
        expected_tp = (12.0 + 10.0 + 11.0) / 3.0
        assert result.iloc[-1] == expected_tp

    def test_twenty_data_points(self, mock_stock_data):
        """Verify VWAP works on a 20-point sequence."""
        n = 20
        mock_stock_data(
            list(range(n)),
            high_prices=[x + 1 for x in range(n)],
            low_prices=[x - 1 for x in range(n)],
            volume_prices=[100] * n,
        )
        result = calculate_vwap("TEST", window=5)
        assert len(result) == 1
        assert result.iloc[-1] > 0

    def test_large_window(self, mock_stock_data):
        """Verify VWAP with a window close to data length."""
        n = 10
        mock_stock_data(
            list(range(n)),
            high_prices=[x + 1 for x in range(n)],
            low_prices=[x - 1 for x in range(n)],
            volume_prices=[100] * n,
        )
        result = calculate_vwap("TEST", window=8)
        assert len(result) == 1
        assert result.iloc[-1] > 0

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N VWAP values."""
        n = 9
        mock_stock_data(
            list(range(n)),
            high_prices=[x + 1 for x in range(n)],
            low_prices=[x - 1 for x in range(n)],
            volume_prices=[100] * n,
        )
        result = calculate_vwap("TEST", window=3, count=3)
        assert len(result) == 3

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data(
            [11.0, 13, 15, 17],
            high_prices=[12.0, 14, 16, 18],
            low_prices=[10.0, 12, 14, 16],
            volume_prices=[100, 200, 150, 300],
        )
        with pytest.raises(IndexError):
            calculate_vwap("TEST", window=2, count=5)

    def test_zero_volume(self, mock_stock_data):
        """Verify IndexError when all volume is zero (division
        by zero)."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            high_prices=[12.0, 14, 16, 18, 20, 22],
            low_prices=[10.0, 12, 14, 16, 18, 20],
            volume_prices=[0, 0, 0, 0, 0, 0],
        )
        with pytest.raises(IndexError):
            calculate_vwap("TEST", window=3)
