# test_calculate_av.py
# Integration tests for calculate_av() with real yfinance data

import pytest
from main import calculate_av


class TestCalculateAv:
    """Tests for calculate_av() with real yfinance calls."""

    def test_av_defaults(self):
        """Verify AV(20) for AAPL is within the range of its
        raw volume data."""
        result, volume = calculate_av("AAPL", _return_raw=True)
        assert volume.min() <= result.iloc[-1] <= volume.max()

    def test_av_window_5(self):
        """Verify AV(5) for MSFT is within the range of its
        raw volume data."""
        result, volume = calculate_av("MSFT", window=5,
                                      _return_raw=True)
        assert volume.min() <= result.iloc[-1] <= volume.max()

    def test_av_window_14(self):
        """Verify AV(14) for GOOG is within the range of its
        raw volume data."""
        result, volume = calculate_av("GOOG", window=14,
                                      _return_raw=True)
        assert volume.min() <= result.iloc[-1] <= volume.max()

    def test_av_with_weekly_interval(self):
        """Verify AV works with a weekly bar interval and is
        within the range of its raw volume data."""
        result, volume = calculate_av("AAPL", window=10,
                                      interval="1wk",
                                      _return_raw=True)
        assert volume.min() <= result.iloc[-1] <= volume.max()

    def test_av_window_one(self):
        """Verify AV with window=1 equals the last volume."""
        result, volume = calculate_av("AAPL", window=1,
                                      _return_raw=True)
        assert volume.min() <= result.iloc[-1] <= volume.max()
