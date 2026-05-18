import pytest
from main import calculate_rsi


class TestCalculateRsi:
    """Tests for calculate_rsi()."""

    def test_basic_rsi(self, mock_stock_data):
        # [10, 13, 11, 16, 12, 19] window=3
        # last non-NaN RSI = 75.0
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3)
        assert result == pytest.approx(75.0, abs=0.01)

    def test_all_gains(self, mock_stock_data):
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_rsi("TEST", 3)
        assert result == 100.0

    def test_all_losses(self, mock_stock_data):
        mock_stock_data([10, 9, 8, 7, 6])
        result = calculate_rsi("TEST", 3)
        assert result == 0.0

    def test_mid_range_rsi(self, mock_stock_data):
        # [10, 12, 11, 13] window=2
        # last non-NaN RSI = 200/3 = 66.67
        mock_stock_data([10, 12, 11, 13])
        result = calculate_rsi("TEST", 2)
        assert result == pytest.approx(66.6667, abs=0.01)

    def test_insufficient_data(self, mock_stock_data):
        mock_stock_data([10, 20])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 5)

    def test_with_weekly_interval(self, mock_stock_data):
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3, interval="1wk")
        assert result == pytest.approx(75.0, abs=0.01)

    def test_with_monthly_interval(self, mock_stock_data):
        # [50, 51, 50, 52, 51, 55] window=3
        # last non-NaN RSI = ~85.71
        mock_stock_data([50, 51, 50, 52, 51, 55])
        result = calculate_rsi("TEST", 3, interval="1mo")
        assert result == pytest.approx(85.7143, abs=0.01)
