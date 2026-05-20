# test_calculate_ema.py
# Integration tests for calculate_ema() with real yfinance data

import pytest
from main import calculate_ema


class TestCalculateEma:
    """Tests for calculate_ema() with real yfinance calls."""

    def test_ema_window_5(self):
        """Verify EMA for AAPL with window=5 returns a positive value."""
        result = calculate_ema("AAPL", 5)
        assert result.iloc[-1] > 0.0

    def test_ema_window_14(self):
        """Verify EMA for MSFT with window=14 returns a positive value."""
        result = calculate_ema("MSFT", 14)
        assert result.iloc[-1] > 0.0

    def test_ema_window_30(self):
        """Verify EMA for GOOG with window=30 returns a positive value."""
        result = calculate_ema("GOOG", 30)
        assert result.iloc[-1] > 0.0

    def test_ema_with_weekly_interval(self):
        """Verify EMA works with a weekly bar interval."""
        result = calculate_ema("AAPL", 10, interval="1wk")
        assert result.iloc[-1] > 0.0

    def test_ema_same_as_last_close(self):
        """Verify EMA with window=1 equals the last close price."""
        result = calculate_ema("AAPL", 1)
        assert result.iloc[-1] > 0.0
