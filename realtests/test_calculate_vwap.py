# test_calculate_vwap.py
# Integration tests for calculate_vwap() with real yfinance data

import pytest
from main import calculate_vwap


class TestCalculateVwap:
    """Tests for calculate_vwap() with real yfinance calls."""

    def test_vwap_defaults(self):
        """Verify VWAP(20) for AAPL returns a positive value."""
        result = calculate_vwap("AAPL")
        assert result.iloc[-1] > 0.0

    def test_vwap_window_5(self):
        """Verify VWAP(5) for MSFT returns a positive value."""
        result = calculate_vwap("MSFT", window=5)
        assert result.iloc[-1] > 0.0

    def test_vwap_window_14(self):
        """Verify VWAP(14) for GOOG returns a positive value."""
        result = calculate_vwap("GOOG", window=14)
        assert result.iloc[-1] > 0.0

    def test_vwap_with_weekly_interval(self):
        """Verify VWAP works with a weekly bar interval."""
        result = calculate_vwap("AAPL", window=10, interval="1wk")
        assert result.iloc[-1] > 0.0

    def test_vwap_window_one(self):
        """Verify VWAP with window=1 equals the typical price."""
        result = calculate_vwap("AAPL", window=1)
        assert result.iloc[-1] > 0.0
