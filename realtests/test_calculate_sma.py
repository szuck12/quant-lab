# test_calculate_sma.py
# Integration tests for calculate_sma() with real yfinance data

import pytest
from main import calculate_sma


class TestCalculateSma:
    """Tests for calculate_sma() with real yfinance calls."""

    def test_sma_window_5(self):
        """Verify SMA for AAPL with window=5 is within the range
        of its raw close prices."""
        result, close = calculate_sma("AAPL", 5, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_sma_window_14(self):
        """Verify SMA for MSFT with window=14 is within the range
        of its raw close prices."""
        result, close = calculate_sma("MSFT", 14, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_sma_window_30(self):
        """Verify SMA for GOOG with window=30 is within the range
        of its raw close prices."""
        result, close = calculate_sma("GOOG", 30, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_sma_with_weekly_interval(self):
        """Verify SMA works with a weekly bar interval and is
        within the range of its raw close prices."""
        result, close = calculate_sma("AAPL", 10, interval="1wk",
                                      _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()

    def test_sma_same_as_last_close(self):
        """Verify SMA with window=1 equals the last close price."""
        result, close = calculate_sma("AAPL", 1, _return_raw=True)
        assert close.min() <= result.iloc[-1] <= close.max()
