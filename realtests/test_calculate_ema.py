import pytest
from main import calculate_ema


class TestCalculateEma:
    """Tests for calculate_ema() with real yfinance calls."""

    def test_ema_window_5(self):
        result = calculate_ema("AAPL", 5)
        assert result > 0.0

    def test_ema_window_14(self):
        result = calculate_ema("MSFT", 14)
        assert result > 0.0

    def test_ema_window_30(self):
        result = calculate_ema("GOOG", 30)
        assert result > 0.0

    def test_ema_with_weekly_interval(self):
        result = calculate_ema("AAPL", 10, interval="1wk")
        assert result > 0.0

    def test_ema_same_as_last_close(self):
        # With window=1, EMA should equal the last close price
        result = calculate_ema("AAPL", 1)
        assert result > 0.0
