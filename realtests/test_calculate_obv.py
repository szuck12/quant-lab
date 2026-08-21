# test_calculate_obv.py
# Integration tests for calculate_obv() with real yfinance data

import pandas as pd
from indicators import calculate_obv


class TestCalculateObv:
    """Tests for calculate_obv() with real yfinance calls."""

    def test_obv_defaults(self):
        """Verify OBV for AAPL with defaults returns a finite
        value."""
        result = calculate_obv("AAPL")
        assert pd.notna(result.iloc[-1])

    def test_obv_window_5(self):
        """Verify OBV for MSFT with window=5 returns a finite
        value."""
        result = calculate_obv("MSFT", window=5)
        assert pd.notna(result.iloc[-1])

    def test_obv_window_14(self):
        """Verify OBV for GOOG with window=14 returns a finite
        value."""
        result = calculate_obv("GOOG", window=14)
        assert pd.notna(result.iloc[-1])

    def test_obv_with_weekly_interval(self):
        """Verify OBV works with a weekly bar interval."""
        result = calculate_obv("AAPL", window=10,
                               interval="1wk")
        assert pd.notna(result.iloc[-1])

    def test_obv_window_one(self):
        """Verify OBV with window=1 returns a finite value."""
        result = calculate_obv("SPY", window=1)
        assert pd.notna(result.iloc[-1])
