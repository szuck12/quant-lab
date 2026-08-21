# test_calculate_cci.py
# Integration tests for calculate_cci() with real yfinance data

import numpy as np
import pandas as pd
from indicators import calculate_cci


class TestCalculateCci:
    """Tests for calculate_cci() with real yfinance calls."""

    def test_cci_defaults(self):
        """Verify CCI for AAPL with defaults returns a finite
        value."""
        result = calculate_cci("AAPL")
        assert pd.notna(result.iloc[-1])
        assert np.isfinite(result.iloc[-1])

    def test_cci_window_5(self):
        """Verify CCI for MSFT with window=5 returns a finite
        value."""
        result = calculate_cci("MSFT", window=5)
        assert pd.notna(result.iloc[-1])
        assert np.isfinite(result.iloc[-1])

    def test_cci_window_20(self):
        """Verify CCI for GOOG with window=20 returns a finite
        value."""
        result = calculate_cci("GOOG", window=20)
        assert pd.notna(result.iloc[-1])
        assert np.isfinite(result.iloc[-1])

    def test_cci_with_weekly_interval(self):
        """Verify CCI works with a weekly bar interval."""
        result = calculate_cci("SPY", window=10,
                               interval="1wk")
        assert pd.notna(result.iloc[-1])
        assert np.isfinite(result.iloc[-1])

    def test_cci_window_10(self):
        """Verify CCI for TSLA with window=10 returns a finite
        value."""
        result = calculate_cci("TSLA", window=10)
        assert pd.notna(result.iloc[-1])
        assert np.isfinite(result.iloc[-1])
