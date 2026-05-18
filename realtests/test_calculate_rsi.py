import pytest
from main import calculate_rsi


class TestCalculateRsi:
    """Tests for calculate_rsi() with real yfinance calls."""

    def test_rsi_window_5(self):
        result = calculate_rsi("AAPL", 5)
        assert 0.0 <= result <= 100.0

    def test_rsi_window_14(self):
        result = calculate_rsi("MSFT", 14)
        assert 0.0 <= result <= 100.0

    def test_rsi_window_30(self):
        result = calculate_rsi("GOOG", 30)
        assert 0.0 <= result <= 100.0

    def test_rsi_with_weekly_interval(self):
        result = calculate_rsi("AAPL", 10, interval="1wk")
        assert 0.0 <= result <= 100.0

    def test_rsi_window_1(self):
        # With window=1, RSI should be 0 or 100 depending on last change
        result = calculate_rsi("AAPL", 1)
        assert result in (0.0, 100.0)
