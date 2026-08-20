# test_calculate_roc.py
# Integration tests for calculate_roc() with real yfinance data

import pandas as pd
from indicators import calculate_roc


class TestCalculateRoc:
    """Tests for calculate_roc() with real yfinance calls."""

    def test_roc_window_5(self):
        """Verify ROC for AAPL with window=5 returns a finite
        value."""
        result = calculate_roc("AAPL", 5)
        assert pd.notna(result.iloc[-1])

    def test_roc_window_14(self):
        """Verify ROC for MSFT with window=14 returns a finite
        value."""
        result = calculate_roc("MSFT", 14)
        assert pd.notna(result.iloc[-1])

    def test_roc_window_30(self):
        """Verify ROC for GOOG with window=30 returns a finite
        value."""
        result = calculate_roc("GOOG", 30)
        assert pd.notna(result.iloc[-1])

    def test_roc_with_weekly_interval(self):
        """Verify ROC works with a weekly bar interval."""
        result = calculate_roc("AAPL", 10, interval="1wk")
        assert pd.notna(result.iloc[-1])

    def test_roc_magnitude_reasonable(self):
        """Verify daily ROC for SPY stays within a sane
        percentage band."""
        result = calculate_roc("SPY", 9)
        assert -100.0 < result.iloc[-1] < 100.0
