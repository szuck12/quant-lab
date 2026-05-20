# test_calculate_macd.py
# Integration tests for calculate_macd() with real yfinance data

import pytest
from main import calculate_macd


class TestCalculateMacd:
    """Tests for calculate_macd() with real yfinance calls."""

    def test_macd_defaults(self):
        """Verify MACD(12,26,9) for AAPL returns positive
        values."""
        m, s, h = calculate_macd("AAPL")
        assert m.iloc[-1] > 0.0
        assert s.iloc[-1] > 0.0

    def test_macd_window_5(self):
        """Verify MACD(5,13,4) for MSFT."""
        m, s, h = calculate_macd("MSFT", fast=5, slow=13,
                                 signal=4)
        assert m.iloc[-1] > 0.0

    def test_macd_window_14(self):
        """Verify MACD(12,26,9) for GOOG."""
        m, s, h = calculate_macd("GOOG", fast=12, slow=26,
                                 signal=9)
        assert m.iloc[-1] > 0.0

    def test_macd_with_weekly_interval(self):
        """Verify MACD works with a weekly bar interval."""
        m, s, h = calculate_macd("AAPL", fast=5, slow=13,
                                 signal=4, interval="1wk")
        assert m.iloc[-1] > 0.0

    def test_macd_window_one(self):
        """Verify MACD with fast=1 produces positive results."""
        m, s, h = calculate_macd("AAPL", fast=1, slow=5,
                                 signal=2)
        assert m.iloc[-1] > 0.0
