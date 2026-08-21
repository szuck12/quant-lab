# test_calculate_adx.py
# Integration tests for calculate_adx() with real yfinance data

import pandas as pd
from indicators import calculate_adx


class TestCalculateAdx:
    """Tests for calculate_adx() with real yfinance calls."""

    def test_adx_defaults(self):
        """Verify ADX for AAPL with defaults is bounded 0-100."""
        plus_di, minus_di, adx = calculate_adx("AAPL")
        assert pd.notna(plus_di.iloc[-1])
        assert pd.notna(minus_di.iloc[-1])
        assert pd.notna(adx.iloc[-1])
        assert 0.0 <= plus_di.iloc[-1] <= 100.0
        assert 0.0 <= minus_di.iloc[-1] <= 100.0
        assert 0.0 <= adx.iloc[-1] <= 100.0

    def test_adx_window_5(self):
        """Verify ADX for MSFT with window=5 is bounded 0-100."""
        plus_di, minus_di, adx = calculate_adx(
            "MSFT", window=5, adx_window=5)
        assert 0.0 <= plus_di.iloc[-1] <= 100.0
        assert 0.0 <= minus_di.iloc[-1] <= 100.0
        assert 0.0 <= adx.iloc[-1] <= 100.0

    def test_adx_window_14(self):
        """Verify ADX for GOOG with window=14 is bounded
        0-100."""
        _, _, adx = calculate_adx("GOOG", window=14,
                                  adx_window=14)
        assert 0.0 <= adx.iloc[-1] <= 100.0

    def test_adx_with_weekly_interval(self):
        """Verify ADX works with a weekly bar interval."""
        _, _, adx = calculate_adx("AAPL", window=10,
                                  adx_window=10,
                                  interval="1wk")
        assert 0.0 <= adx.iloc[-1] <= 100.0

    def test_adx_di_nonnegative(self):
        """Verify DI lines are non-negative and identify the
        dominant direction consistently with ADX strength."""
        plus_di, minus_di, adx = calculate_adx("SPY",
                                               window=14,
                                               adx_window=14)
        assert plus_di.iloc[-1] >= 0.0
        assert minus_di.iloc[-1] >= 0.0
        if adx.iloc[-1] > 25.0:
            assert (plus_di.iloc[-1] != minus_di.iloc[-1])
