# test_calculate_atr.py
# Integration tests for calculate_atr() with real yfinance data

import pytest
from indicators import calculate_atr


class TestCalculateAtr:
    """Tests for calculate_atr() with real yfinance calls."""

    def test_atr_defaults(self):
        """Verify ATR(14) for AAPL is non-negative and bounded
        by its raw TR."""
        result, tr = calculate_atr("AAPL", _return_raw=True)
        assert result.iloc[-1] >= 0.0
        assert tr.min() <= result.iloc[-1] <= tr.max()

    def test_atr_window_5(self):
        """Verify ATR(5) for MSFT is bounded by its raw TR."""
        result, tr = calculate_atr("MSFT", window=5,
                                   _return_raw=True)
        assert tr.min() <= result.iloc[-1] <= tr.max()

    def test_atr_window_14(self):
        """Verify ATR(14) for GOOG is bounded by its raw TR."""
        result, tr = calculate_atr("GOOG", window=14,
                                   _return_raw=True)
        assert tr.min() <= result.iloc[-1] <= tr.max()

    def test_atr_with_weekly_interval(self):
        """Verify ATR works with a weekly bar interval."""
        result, tr = calculate_atr("AAPL", window=10,
                                   interval="1wk",
                                   _return_raw=True)
        assert tr.min() <= result.iloc[-1] <= tr.max()

    def test_atr_window_one(self):
        """Verify ATR with window=1 equals the latest TR."""
        result, tr = calculate_atr("AAPL", window=1,
                                   _return_raw=True)
        assert result.iloc[-1] == tr.iloc[-1]
