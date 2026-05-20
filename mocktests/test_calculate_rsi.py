# test_calculate_rsi.py
# Tests for calculate_rsi() using mocked stock data

import pytest
from main import calculate_rsi


class TestCalculateRsi:
    """Tests for calculate_rsi()."""

    def test_basic_rsi(self, mock_stock_data):
        """Verify RSI matches the hand-calculated Wilder-smoothed value
        for a known sequence of prices with window=3."""

        # [10, 13, 11, 16, 12, 19] window=3, Wilder RMA
        # last non-NaN RSI = 75.07
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == pytest.approx(75.0708, abs=0.01)

    def test_all_gains(self, mock_stock_data):
        """Verify RSI is 100 when every price change is positive."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == 100.0

    def test_all_losses(self, mock_stock_data):
        """Verify RSI is 0 when every price change is negative."""
        mock_stock_data([10, 9, 8, 7, 6])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == 0.0

    def test_mid_range_rsi(self, mock_stock_data):
        """Verify RSI produces a mid-range value for mixed price
        changes."""

        # [10, 12, 11, 13] window=2, Wilder RMA
        # last non-NaN RSI = 83.33
        mock_stock_data([10, 12, 11, 13])
        result = calculate_rsi("TEST", 2)
        assert result.iloc[-1] == pytest.approx(83.3333, abs=0.01)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError is raised when there is not enough data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 5)

    def test_with_weekly_interval(self, mock_stock_data):
        """Verify RSI works with a weekly bar interval."""
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3, interval="1wk")
        assert result.iloc[-1] == pytest.approx(75.0708, abs=0.01)

    def test_with_monthly_interval(self, mock_stock_data):
        """Verify RSI works with a monthly bar interval."""
        # [50, 51, 50, 52, 51, 55] window=3, Wilder RMA
        # last non-NaN RSI = ~84.08
        mock_stock_data([50, 51, 50, 52, 51, 55])
        result = calculate_rsi("TEST", 3, interval="1mo")
        assert result.iloc[-1] == pytest.approx(84.08, abs=0.01)

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N RSI values."""
        # [10, 13, 11, 16, 12, 19] window=3
        # RSI values (rounded): NaN, 100.0, 50.0, 82.61, 46.34, 75.07
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3, count=2)
        assert len(result) == 2
        assert result.iloc[-1] == pytest.approx(75.0708, abs=0.01)

    def test_count_with_interval(self, mock_stock_data):
        """Verify count works alongside a custom interval."""
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3, interval="1wk", count=2)
        assert len(result) == 2
        assert result.iloc[-1] == pytest.approx(75.0708, abs=0.01)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available RSI values."""
        # RSI(3) on [10, 11] produces 1 non-NaN value (Wilder needs
        # only 1 price change to start)
        mock_stock_data([10, 11])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 3, count=2)
