# test_calculate_macd.py
# Integration tests for calculate_macd() with real yfinance data

import pytest
from indicators import calculate_macd


class TestCalculateMacd:
    """Tests for calculate_macd() with real yfinance calls."""

    def test_macd_defaults(self):
        """Verify MACD(12,26,9) for AAPL returns finite
        values."""
        m, s, h = calculate_macd("AAPL")
        assert not m.isna().iloc[-1]
        assert not s.isna().iloc[-1]
        assert not h.isna().iloc[-1]

    def test_macd_window_5(self):
        """Verify MACD(5,13,4) for MSFT returns a finite
        value."""
        m, s, h = calculate_macd("MSFT", fast=5, slow=13,
                                 signal=4)
        assert not m.isna().iloc[-1]

    def test_macd_window_14(self):
        """Verify MACD(12,26,9) for GOOG returns a finite
        value."""
        m, s, h = calculate_macd("GOOG", fast=12, slow=26,
                                 signal=9)
        assert not m.isna().iloc[-1]

    def test_macd_with_weekly_interval(self):
        """Verify MACD works with a weekly bar interval."""
        m, s, h = calculate_macd("AAPL", fast=5, slow=13,
                                 signal=4, interval="1wk")
        assert not m.isna().iloc[-1]

    def test_macd_window_one(self):
        """Verify MACD with fast=1 produces a finite value."""
        m, s, h = calculate_macd("AAPL", fast=1, slow=5,
                                  signal=2)
        assert not m.isna().iloc[-1]

    def test_macd_bearish_divergence_pattern(self):
        """Verify MACD on SPY contains both positive and negative
        histogram values (bearish/bullish crossovers occur)."""
        m, s, h = calculate_macd("SPY", fast=12, slow=26,
                                  signal=9, count=20)
        assert (h > 0).any(), ("Histogram should have positive"
                               " values (bullish crossover)")
        assert (h < 0).any(), ("Histogram should have negative"
                               " values (bearish crossover)")
