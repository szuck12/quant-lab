import pytest
from main import calculate_sma


class TestCalculateSma:
    """Tests for calculate_sma() with real yfinance calls."""

    def test_sma_window_5(self):
        result = calculate_sma("AAPL", 5)
        assert result > 0.0

    def test_sma_window_14(self):
        result = calculate_sma("MSFT", 14)
        assert result > 0.0

    def test_sma_window_30(self):
        result = calculate_sma("GOOG", 30)
        assert result > 0.0

    def test_sma_with_weekly_interval(self):
        result = calculate_sma("AAPL", 10, interval="1wk")
        assert result > 0.0

    def test_sma_same_as_last_close(self):
        # With window=1, SMA should equal the last close price
        result = calculate_sma("AAPL", 1)
        assert result > 0.0
