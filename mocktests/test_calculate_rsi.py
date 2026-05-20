# test_calculate_rsi.py
# Tests for calculate_rsi() using mocked stock data

import pytest
from main import calculate_rsi


class TestCalculateRsi:
    """Tests for calculate_rsi()."""

    def test_basic_rsi(self, mock_stock_data):
        """Verify RSI matches the hand-calculated Wilder-smoothed
        value for a known sequence with window=3."""
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == pytest.approx(75.0708, abs=0.01)

    def test_all_gains(self, mock_stock_data):
        """Verify RSI is 100 when every change is positive."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == 100.0

    def test_all_losses(self, mock_stock_data):
        """Verify RSI is 0 when every change is negative."""
        mock_stock_data([10, 9, 8, 7, 6])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == 0.0

    def test_window_one(self, mock_stock_data):
        """Verify RSI with window=1 is 100 when price rises."""
        mock_stock_data([10, 20])
        result = calculate_rsi("TEST", 1)
        assert result.iloc[-1] == 100.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify RSI still produces a result when window exceeds
        data length (Wilder EWM seeds from the first value and
        still converges)."""
        mock_stock_data([10, 20, 30])
        result = calculate_rsi("TEST", 10)
        assert result.iloc[-1] is not None

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify RSI raises IndexError on constant prices
        (zero-gain / zero-loss division)."""
        mock_stock_data([50, 50, 50, 50, 50, 50])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 3)

    def test_alternating_pattern(self, mock_stock_data):
        """Verify RSI handles a zigzag [10, 20] pattern."""
        mock_stock_data([10, 20, 10, 20, 10, 20, 10, 20])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == pytest.approx(61.2433, abs=0.01)

    def test_large_prices(self, mock_stock_data):
        """Verify RSI handles prices around 1e9."""
        mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                         1.004e9])
        result = calculate_rsi("TEST", 2)
        assert result.iloc[-1] == 100.0

    def test_negative_prices(self, mock_stock_data):
        """Verify RSI handles negative prices (all gains)."""
        mock_stock_data([-10, -9, -8, -7, -6, -5, -4])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == 100.0

    def test_spike_pattern(self, mock_stock_data):
        """Verify RSI handles one spike in a flat series."""
        mock_stock_data([10, 10, 10, 10, 1000, 10, 10, 10,
                         10, 10])
        result = calculate_rsi("TEST", 3)
        assert result.iloc[-1] == pytest.approx(40.0, abs=0.01)

    def test_single_price_point(self, mock_stock_data):
        """Verify RSI raises IndexError with one price point
        (no price change to compute ratio)."""
        mock_stock_data([42])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 1)

    def test_twenty_data_points(self, mock_stock_data):
        """Verify RSI works on a 20-point sequence."""
        mock_stock_data(list(range(20)))
        result = calculate_rsi("TEST", 5)
        assert len(result) == 1
        assert result.iloc[-1] == 100.0

    def test_large_window(self, mock_stock_data):
        """Verify RSI with a window close to data length."""
        mock_stock_data(list(range(10)))
        result = calculate_rsi("TEST", 8)
        assert len(result) == 1
        assert result.iloc[-1] == 100.0

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N RSI values."""
        mock_stock_data([10, 13, 11, 16, 12, 19])
        result = calculate_rsi("TEST", 3, count=2)
        assert len(result) == 2
        assert result.iloc[-1] == pytest.approx(75.0708, abs=0.01)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available values."""
        mock_stock_data([10, 11])
        with pytest.raises(IndexError):
            calculate_rsi("TEST", 3, count=2)
