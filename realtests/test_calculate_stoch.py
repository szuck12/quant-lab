# test_calculate_stoch.py
# Integration tests for calculate_stoch() with real yfinance data

import pytest
from indicators import calculate_stoch


class TestCalculateStoch:
    """Tests for calculate_stoch() with real yfinance calls."""

    def test_stoch_defaults(self):
        """Verify STOCH(14,3,3) for AAPL is within 0-100."""
        k, d = calculate_stoch("AAPL")
        assert 0.0 <= k.iloc[-1] <= 100.0
        assert 0.0 <= d.iloc[-1] <= 100.0

    def test_stoch_window_5(self):
        """Verify STOCH(5,3,3) for MSFT is within 0-100."""
        k, d = calculate_stoch("MSFT", window=5)
        assert 0.0 <= k.iloc[-1] <= 100.0
        assert 0.0 <= d.iloc[-1] <= 100.0

    def test_stoch_window_14(self):
        """Verify STOCH(14,3,3) for GOOG is within 0-100."""
        k, d = calculate_stoch("GOOG", window=14)
        assert 0.0 <= k.iloc[-1] <= 100.0
        assert 0.0 <= d.iloc[-1] <= 100.0

    def test_stoch_with_weekly_interval(self):
        """Verify STOCH works with a weekly bar interval."""
        k, d = calculate_stoch("AAPL", window=10,
                               interval="1wk")
        assert 0.0 <= k.iloc[-1] <= 100.0
        assert 0.0 <= d.iloc[-1] <= 100.0

    def test_stoch_window_one(self):
        """Verify STOCH with window=1 is within 0-100."""
        k, d = calculate_stoch("AAPL", window=1, smooth_k=1,
                               smooth_d=1)
        assert 0.0 <= k.iloc[-1] <= 100.0
        assert 0.0 <= d.iloc[-1] <= 100.0
