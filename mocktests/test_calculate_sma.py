import pytest
from unittest.mock import patch
from main import calculate_sma


class TestCalculateSma:
    """Tests for calculate_sma()."""

    def test_basic_sma(self, mock_stock_data):
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_sma("TEST", 3)
        assert result == 13.0

    def test_window_one(self, mock_stock_data):
        mock_stock_data([10, 20, 30])
        result = calculate_sma("TEST", 1)
        assert result == 30.0

    def test_insufficient_data(self, mock_stock_data):
        mock_stock_data([10, 20])
        with pytest.raises(IndexError):
            calculate_sma("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        mock_stock_data([50, 50, 50, 50])
        result = calculate_sma("TEST", 2)
        assert result == 50.0

    def test_with_weekly_interval(self, mock_stock_data):
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_sma("TEST", 3, interval="1wk")
        assert result == 13.0

    def test_with_monthly_interval(self, mock_stock_data):
        mock_stock_data([100, 102, 104, 106, 108])
        result = calculate_sma("TEST", 3, interval="1mo")
        assert result == 106.0
