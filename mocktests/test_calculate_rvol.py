# test_calculate_rvol.py
# Tests for calculate_rvol() using mocked stock data

import pytest
from indicators import calculate_rvol


class TestCalculateRvol:
    """Tests for calculate_rvol()."""

    def test_basic_rvol(self, mock_stock_data):
        """Verify RVOL matches the known value for a 6-point
        sequence with window=3."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            volume_prices=[100, 200, 150, 300, 250, 400],
        )
        result = calculate_rvol("TEST", window=3)
        # Last RVOL: 400 / ((300+250+400)/3) = 400/316.67
        assert result.iloc[-1] == pytest.approx(1.2632, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify RVOL with window=1 equals 1.0 (volume / itself)."""
        mock_stock_data([10, 20], volume_prices=[100, 200])
        result = calculate_rvol("TEST", window=1)
        assert result.iloc[-1] == 1.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length."""
        mock_stock_data(
            [11.0, 13, 15], volume_prices=[100, 200, 150]
        )
        with pytest.raises(IndexError):
            calculate_rvol("TEST", window=10)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], volume_prices=[])
        with pytest.raises(IndexError):
            calculate_rvol("TEST", window=5)

    def test_constant_volume(self, mock_stock_data):
        """Verify RVOL of constant volume equals 1.0."""
        mock_stock_data(
            [50.0] * 6, volume_prices=[50, 50, 50, 50, 50, 50]
        )
        result = calculate_rvol("TEST", window=2)
        assert result.iloc[-1] == 1.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify RVOL handles a zigzag volume pattern."""
        mock_stock_data(
            [11.0, 21, 11, 21, 11, 21, 11, 21],
            volume_prices=[100, 200, 100, 200, 100, 200,
                           100, 200],
        )
        result = calculate_rvol("TEST", window=3)
        # Last RVOL: 200 / ((200+100+200)/3) = 200/166.67
        assert result.iloc[-1] == pytest.approx(1.2, abs=0.01)

    def test_large_prices(self, mock_stock_data):
        """Verify RVOL handles volumes around 1e9."""
        n = 5
        mock_stock_data(
            [1e9 + i for i in range(n)],
            volume_prices=[1e9 + i for i in range(n)],
        )
        result = calculate_rvol("TEST", window=2)
        # Each rvol value should be ~1.0 (volume / avg of self+prev)
        assert result.iloc[-1] == pytest.approx(1.0, rel=1e-5)

    def test_negative_volume(self, mock_stock_data):
        """Verify RVOL handles negative volumes."""
        mock_stock_data(
            [-11.0, -13, -15, -17, -19, -21, -23],
            volume_prices=[-100, -200, -150, -300, -250,
                           -400, -350],
        )
        result = calculate_rvol("TEST", window=3)
        # Last RVOL: -350 / ((-250+-400+-350)/3) = -350/-333.33
        assert result.iloc[-1] == pytest.approx(1.05, abs=0.01)

    def test_spike_pattern(self, mock_stock_data):
        """Verify RVOL handles one volume spike in a flat series."""
        mock_stock_data(
            [50.0] * 10,
            volume_prices=[100] * 4 + [10000] + [100] * 5,
        )
        result = calculate_rvol("TEST", window=3)
        # Tail returns to 1.0 when avg catches up
        assert result.iloc[-1] == pytest.approx(1.0, abs=0.01)

    def test_single_price_point(self, mock_stock_data):
        """Verify RVOL with one bar equals 1.0 (volume / itself)."""
        mock_stock_data([11.0], volume_prices=[100])
        result = calculate_rvol("TEST", window=1)
        assert result.iloc[-1] == 1.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify RVOL works on a 20-point sequence."""
        n = 20
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_rvol("TEST", window=5)
        assert len(result) == 1
        assert result.iloc[-1] > 0.0

    def test_large_window(self, mock_stock_data):
        """Verify RVOL with a window close to data length."""
        n = 10
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_rvol("TEST", window=8)
        assert len(result) == 1
        assert result.iloc[-1] is not None

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N RVOL values."""
        n = 9
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_rvol("TEST", window=3, count=3)
        assert len(result) == 3
        assert result.iloc[-1] == pytest.approx(1.1429,
                                                abs=0.01)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data(
            [11.0, 13, 15, 17],
            volume_prices=[100, 200, 150, 300],
        )
        with pytest.raises(IndexError):
            calculate_rvol("TEST", window=2, count=5)

    def test_zero_volume(self, mock_stock_data):
        """Verify IndexError when all volume is zero (division
        by zero)."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            volume_prices=[0, 0, 0, 0, 0, 0],
        )
        with pytest.raises(IndexError):
            calculate_rvol("TEST", window=3)
