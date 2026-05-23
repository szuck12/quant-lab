# test_calculate_ema.py
# Integration tests for calculate_ema() with real yfinance data

import pytest
from main import calculate_ema


class TestCalculateEma:
    """Tests for calculate_ema() with real yfinance calls."""

    def test_ema_window_5(self):
        """Verify EMA for AAPL with window=5 is within the range
        of its raw close prices."""
        result, close = calculate_ema("AAPL", 5, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_ema_window_14(self):
        """Verify EMA for MSFT with window=14 is within the range
        of its raw close prices."""
        result, close = calculate_ema("MSFT", 14, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_ema_window_30(self):
        """Verify EMA for GOOG with window=30 is within the range
        of its raw close prices."""
        result, close = calculate_ema("GOOG", 30, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_ema_with_weekly_interval(self):
        """Verify EMA works with a weekly bar interval and is
        within the range of its raw close prices."""
        result, close = calculate_ema("AAPL", 10, interval="1wk",
                                      _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_ema_same_as_last_close(self):
        """Verify EMA with window=1 equals the last close price."""
        result, close = calculate_ema("AAPL", 1, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()
