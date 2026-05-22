# test_calculate_av.py
# Integration tests for calculate_av() with real yfinance data

import pytest
from main import calculate_av


class TestCalculateAv:
    """Tests for calculate_av() with real yfinance calls."""

    def test_av_defaults(self):
        """Verify AV(20) for AAPL returns a positive value."""
        result = calculate_av("AAPL")
        assert result.iloc[-1] > 0.0

    def test_av_window_5(self):
        """Verify AV(5) for MSFT returns a positive value."""
        result = calculate_av("MSFT", window=5)
        assert result.iloc[-1] > 0.0

    def test_av_window_14(self):
        """Verify AV(14) for GOOG returns a positive value."""
        result = calculate_av("GOOG", window=14)
        assert result.iloc[-1] > 0.0

    def test_av_with_weekly_interval(self):
        """Verify AV works with a weekly bar interval."""
        result = calculate_av("AAPL", window=10, interval="1wk")
        assert result.iloc[-1] > 0.0

    def test_av_window_one(self):
        """Verify AV with window=1 equals the last volume."""
        result = calculate_av("AAPL", window=1)
        assert result.iloc[-1] > 0.0
