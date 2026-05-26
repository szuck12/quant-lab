# test_calculate_rvol.py
# Integration tests for calculate_rvol() with real yfinance data

import pytest
from indicators import calculate_rvol


class TestCalculateRvol:
    """Tests for calculate_rvol() with real yfinance calls."""

    def test_rvol_defaults(self):
        """Verify RVOL(10) for AAPL returns a positive value."""
        result = calculate_rvol("AAPL")
        assert result.iloc[-1] > 0.0

    def test_rvol_window_5(self):
        """Verify RVOL(5) for MSFT returns a positive value."""
        result = calculate_rvol("MSFT", window=5)
        assert result.iloc[-1] > 0.0

    def test_rvol_window_14(self):
        """Verify RVOL(14) for GOOG returns a positive value."""
        result = calculate_rvol("GOOG", window=14)
        assert result.iloc[-1] > 0.0

    def test_rvol_with_weekly_interval(self):
        """Verify RVOL works with a weekly bar interval."""
        result = calculate_rvol("AAPL", window=10,
                                interval="1wk")
        assert result.iloc[-1] > 0.0

    def test_rvol_window_one(self):
        """Verify RVOL with window=1 equals 1.0."""
        result = calculate_rvol("AAPL", window=1)
        assert result.iloc[-1] == 1.0
