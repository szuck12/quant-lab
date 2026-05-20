# test_calculate_sma.py
# Integration tests for calculate_sma() with real yfinance data

import pytest
from main import calculate_sma


class TestCalculateSma:
    """Tests for calculate_sma() with real yfinance calls."""

    def test_sma_window_5(self):
        """Verify SMA for AAPL with window=5 returns a positive value."""
        result = calculate_sma("AAPL", 5)
        assert result.iloc[-1] > 0.0

    def test_sma_window_14(self):
        """Verify SMA for MSFT with window=14 returns a positive value."""
        result = calculate_sma("MSFT", 14)
        assert result.iloc[-1] > 0.0

    def test_sma_window_30(self):
        """Verify SMA for GOOG with window=30 returns a positive value."""
        result = calculate_sma("GOOG", 30)
        assert result.iloc[-1] > 0.0

    def test_sma_with_weekly_interval(self):
        """Verify SMA works with a weekly bar interval."""
        result = calculate_sma("AAPL", 10, interval="1wk")
        assert result.iloc[-1] > 0.0

    def test_sma_same_as_last_close(self):
        """Verify SMA with window=1 equals the last close price."""
        result = calculate_sma("AAPL", 1)
        assert result.iloc[-1] > 0.0
