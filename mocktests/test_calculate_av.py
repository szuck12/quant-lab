# test_calculate_av.py
# Tests for calculate_av() using mocked stock data

import pytest
from main import calculate_av


class TestCalculateAv:
    """Tests for calculate_av()."""

    def test_basic_av(self, mock_stock_data):
        """Verify AV matches the known value for a 6-point
        sequence with window=3."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            volume_prices=[100, 200, 150, 300, 250, 400],
        )
        result = calculate_av("TEST", window=3)
        # Last rolling mean of 3: (300 + 250 + 400) / 3 = 316.67
        assert result.iloc[-1] == pytest.approx(316.6667, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify AV with window=1 equals the last volume."""
        mock_stock_data([10, 20], volume_prices=[100, 200])
        result = calculate_av("TEST", window=1)
        assert result.iloc[-1] == 200.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length."""
        mock_stock_data(
            [11.0, 13, 15], volume_prices=[100, 200, 150]
        )
        with pytest.raises(IndexError):
            calculate_av("TEST", window=10)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], volume_prices=[])
        with pytest.raises(IndexError):
            calculate_av("TEST", window=5)

    def test_constant_volume(self, mock_stock_data):
        """Verify AV of constant volume equals the constant."""
        mock_stock_data(
            [50.0] * 6, volume_prices=[50, 50, 50, 50, 50, 50]
        )
        result = calculate_av("TEST", window=2)
        assert result.iloc[-1] == 50.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify AV handles a zigzag volume pattern."""
        mock_stock_data(
            [11.0, 21, 11, 21, 11, 21, 11, 21],
            volume_prices=[100, 200, 100, 200, 100, 200,
                           100, 200],
        )
        result = calculate_av("TEST", window=3)
        # Last rolling mean of 3: (200 + 100 + 200) / 3
        assert result.iloc[-1] == pytest.approx(166.6667,
                                                abs=0.01)

    def test_large_prices(self, mock_stock_data):
        """Verify AV handles volumes around 1e9."""
        n = 5
        mock_stock_data(
            [1e9 + i for i in range(n)],
            volume_prices=[1e9 + i for i in range(n)],
        )
        result = calculate_av("TEST", window=2)
        # Last mean: (1000000003 + 1000000004) / 2
        assert result.iloc[-1] == pytest.approx(1000000003.5,
                                                rel=1e-6)

    def test_negative_volume(self, mock_stock_data):
        """Verify AV handles negative volumes."""
        mock_stock_data(
            [-11.0, -13, -15, -17, -19, -21, -23],
            volume_prices=[-100, -200, -150, -300, -250,
                           -400, -350],
        )
        result = calculate_av("TEST", window=3)
        # Last mean: (-250 + -400 + -350) / 3 = -333.33
        assert result.iloc[-1] == pytest.approx(-333.3333,
                                                abs=0.01)

    def test_spike_pattern(self, mock_stock_data):
        """Verify AV handles one volume spike in a flat series."""
        mock_stock_data(
            [50.0] * 10,
            volume_prices=[100] * 4 + [10000] + [100] * 5,
        )
        result = calculate_av("TEST", window=3)
        assert result.iloc[-1] == pytest.approx(100.0,
                                                abs=0.01)

    def test_single_price_point(self, mock_stock_data):
        """Verify AV with one bar equals the volume itself."""
        mock_stock_data([11.0], volume_prices=[100])
        result = calculate_av("TEST", window=1)
        assert result.iloc[-1] == 100.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify AV works on a 20-point sequence."""
        n = 20
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_av("TEST", window=5)
        assert len(result) == 1
        assert result.iloc[-1] > 0.0

    def test_large_window(self, mock_stock_data):
        """Verify AV with a window close to data length."""
        n = 10
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_av("TEST", window=8)
        assert len(result) == 1
        assert result.iloc[-1] is not None

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N AV values."""
        n = 9
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_av("TEST", window=3, count=3)
        assert len(result) == 3
        # Last 3 means: (3+4+5)/3=4, (4+5+6)/3=5, (5+6+7)/3=6,
        # (6+7+8)/3=7
        assert result.iloc[-1] == pytest.approx(7.0, abs=0.01)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data(
            [11.0, 13, 15, 17],
            volume_prices=[100, 200, 150, 300],
        )
        with pytest.raises(IndexError):
            calculate_av("TEST", window=2, count=5)

    def test_zero_volume(self, mock_stock_data):
        """Verify AV returns 0.0 when all volume is zero (no
        division needed, unlike VWAP)."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            volume_prices=[0, 0, 0, 0, 0, 0],
        )
        result = calculate_av("TEST", window=3)
        assert result.iloc[-1] == 0.0
