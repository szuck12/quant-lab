# test_calculate_rsi.py
# Integration tests for calculate_rsi() with real yfinance data

import pytest
from main import calculate_rsi


class TestCalculateRsi:
    """Tests for calculate_rsi() with real yfinance calls."""

    def test_rsi_window_5(self):
        """Verify RSI for AAPL with window=5 is in the valid range."""
        result = calculate_rsi("AAPL", 5)
        assert 0.0 <= result.iloc[-1] <= 100.0

    def test_rsi_window_14(self):
        """Verify RSI for MSFT with window=14 is in the valid range."""
        result = calculate_rsi("MSFT", 14)
        assert 0.0 <= result.iloc[-1] <= 100.0

    def test_rsi_window_30(self):
        """Verify RSI for GOOG with window=30 is in the valid range."""
        result = calculate_rsi("GOOG", 30)
        assert 0.0 <= result.iloc[-1] <= 100.0

    def test_rsi_with_weekly_interval(self):
        """Verify RSI works with a weekly bar interval."""
        result = calculate_rsi("AAPL", 10, interval="1wk")
        assert 0.0 <= result.iloc[-1] <= 100.0

    def test_rsi_window_1(self):
        """Verify RSI with window=1 is either 0 or 100."""
        result = calculate_rsi("AAPL", 1)
        assert result.iloc[-1] in (0.0, 100.0)
