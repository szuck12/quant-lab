# test_calculate_vwap.py
# Integration tests for calculate_vwap() with real yfinance data

import pytest
from indicators import calculate_vwap


class TestCalculateVwap:
    """Tests for calculate_vwap() with real yfinance calls."""

    def test_vwap_defaults(self):
        """Verify VWAP(20) for AAPL is within the range of its
        raw typical prices."""
        result, typical = calculate_vwap("AAPL", _return_raw=True)
        assert typical.min() <= result.iloc[-1] <= typical.max()

    def test_vwap_window_5(self):
        """Verify VWAP(5) for MSFT is within the range of its
        raw typical prices."""
        result, typical = calculate_vwap("MSFT", window=5,
                                         _return_raw=True)
        assert typical.min() <= result.iloc[-1] <= typical.max()

    def test_vwap_window_14(self):
        """Verify VWAP(14) for GOOG is within the range of its
        raw typical prices."""
        result, typical = calculate_vwap("GOOG", window=14,
                                         _return_raw=True)
        assert typical.min() <= result.iloc[-1] <= typical.max()

    def test_vwap_with_weekly_interval(self):
        """Verify VWAP works with a weekly bar interval and is
        within the range of its raw typical prices."""
        result, typical = calculate_vwap("AAPL", window=10,
                                         interval="1wk",
                                         _return_raw=True)
        assert typical.min() <= result.iloc[-1] <= typical.max()

    def test_vwap_window_one(self):
        """Verify VWAP with window=1 equals the typical price."""
        result, typical = calculate_vwap("AAPL", window=1,
                                         _return_raw=True)
        assert typical.min() <= result.iloc[-1] <= typical.max()
