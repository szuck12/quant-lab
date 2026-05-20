# test_calculate_ema.py
# Tests for calculate_ema() using mocked stock data

import pytest
from main import calculate_ema


class TestCalculateEma:
    """Tests for calculate_ema()."""

    def test_basic_ema(self, mock_stock_data):
        """Verify EMA matches the hand-calculated value for a small
        rising price series with window=3."""

        # [10, 11, 12, 13, 14] window=3, span alpha = 2/4 = 0.5
        # EMA: 10, 10.5, 11.25, 12.125, 13.0625
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_ema("TEST", 3)
        assert result.iloc[-1] == pytest.approx(13.0625, abs=0.0001)

    def test_window_one(self, mock_stock_data):
        """Verify EMA with window=1 equals the last close price."""
        mock_stock_data([10, 20, 30])
        result = calculate_ema("TEST", 1)
        assert result.iloc[-1] == 30.0

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError is raised when there is not enough data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_ema("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify EMA of constant prices equals that constant value."""
        mock_stock_data([50, 50, 50, 50])
        result = calculate_ema("TEST", 2)
        assert result.iloc[-1] == 50.0

    def test_with_weekly_interval(self, mock_stock_data):
        """Verify EMA works with a weekly bar interval."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_ema("TEST", 3, interval="1wk")
        assert result.iloc[-1] == pytest.approx(13.0625, abs=0.0001)

    def test_with_monthly_interval(self, mock_stock_data):
        """Verify EMA works with a monthly bar interval."""
        mock_stock_data([100, 102, 104, 106, 108])
        result = calculate_ema("TEST", 3, interval="1mo")
        assert result.iloc[-1] == pytest.approx(106.125, abs=0.0001)

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N EMA values."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_ema("TEST", 2, count=3)
        assert len(result) == 3
        # Full EMA(span=2): [10, 10.6667, 11.5556, 12.5185, 13.5062]
        assert result.iloc[-1] == pytest.approx(13.5062, abs=0.0001)

    def test_count_with_interval(self, mock_stock_data):
        """Verify count works alongside a custom interval."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_ema("TEST", 2, interval="1wk", count=3)
        assert len(result) == 3
        assert result.iloc[-1] == pytest.approx(13.5062, abs=0.0001)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available EMA values."""
        mock_stock_data([10, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_ema("TEST", 2, count=5)
