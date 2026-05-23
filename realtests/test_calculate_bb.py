# test_calculate_bb.py
# Integration tests for calculate_bb() with real yfinance data

import pytest
from main import calculate_bb


class TestCalculateBb:
    """Tests for calculate_bb() with real yfinance calls."""

    def test_bb_defaults(self):
        """Verify BB(20,2.0) for AAPL returns ordered bands with
        the middle band within raw close prices."""
        (u, m, l), close = calculate_bb("AAPL", _return_raw=True)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]
        assert l.iloc[-1] > 0.0
        assert close.min() <= m.iloc[-1] <= close.max()
        assert close.iloc[-20:].std(ddof=0) > 0

    def test_bb_window_5(self):
        """Verify BB(5,2.0) for MSFT returns ordered bands with
        the middle band within raw close prices."""
        (u, m, l), close = calculate_bb("MSFT", window=5,
                                        num_std=2.0,
                                        _return_raw=True)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]
        assert close.min() <= m.iloc[-1] <= close.max()
        assert close.iloc[-5:].std(ddof=0) > 0

    def test_bb_window_14(self):
        """Verify BB(14,2.0) for GOOG returns ordered bands with
        the middle band within raw close prices."""
        (u, m, l), close = calculate_bb("GOOG", window=14,
                                        num_std=2.0,
                                        _return_raw=True)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]
        assert close.min() <= m.iloc[-1] <= close.max()
        assert close.iloc[-14:].std(ddof=0) > 0

    def test_bb_with_weekly_interval(self):
        """Verify BB works with a weekly bar interval with the
        middle band within raw close prices."""
        (u, m, l), close = calculate_bb("AAPL", window=10,
                                        num_std=2.0,
                                        interval="1wk",
                                        _return_raw=True)
        assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]
        assert close.min() <= m.iloc[-1] <= close.max()
        assert close.iloc[-10:].std(ddof=0) > 0

    def test_bb_window_one(self):
        """Verify BB with window=1 collapses to the close
        price (std=0)."""
        (u, m, l), close = calculate_bb("AAPL", window=1,
                                        num_std=2.0,
                                        _return_raw=True)
        assert u.iloc[-1] == m.iloc[-1] == l.iloc[-1]
        assert close.min() <= m.iloc[-1] <= close.max()
