import pytest
from main import calculate_ema


class TestCalculateEma:
    """Tests for calculate_ema()."""

    def test_basic_ema(self, mock_stock_data):
        # [10, 11, 12, 13, 14] window=3, span alpha = 2/4 = 0.5
        # EMA: 10, 10.5, 11.25, 12.125, 13.0625
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_ema("TEST", 3)
        assert result == pytest.approx(13.0625, abs=0.0001)

    def test_window_one(self, mock_stock_data):
        mock_stock_data([10, 20, 30])
        result = calculate_ema("TEST", 1)
        assert result == 30.0

    def test_insufficient_data(self, mock_stock_data):
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_ema("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        mock_stock_data([50, 50, 50, 50])
        result = calculate_ema("TEST", 2)
        assert result == 50.0

    def test_with_weekly_interval(self, mock_stock_data):
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_ema("TEST", 3, interval="1wk")
        assert result == pytest.approx(13.0625, abs=0.0001)

    def test_with_monthly_interval(self, mock_stock_data):
        mock_stock_data([100, 102, 104, 106, 108])
        result = calculate_ema("TEST", 3, interval="1mo")
        assert result == pytest.approx(106.125, abs=0.0001)
