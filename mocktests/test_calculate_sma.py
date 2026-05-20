# test_calculate_sma.py
# Tests for calculate_sma() using mocked stock data

import pytest
from main import calculate_sma


class TestCalculateSma:
    """Tests for calculate_sma()."""

    def test_basic_sma(self, mock_stock_data):
        """Verify SMA matches the rolling mean for a 6-point
        sequence with window=3."""
        mock_stock_data([10, 11, 12, 13, 14, 15])
        result = calculate_sma("TEST", 3)
        assert result.iloc[-1] == 14.0

    def test_window_one(self, mock_stock_data):
        """Verify SMA with window=1 equals the last close."""
        mock_stock_data([10, 20])
        result = calculate_sma("TEST", 1)
        assert result.iloc[-1] == 20.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length."""
        mock_stock_data([1, 2, 3])
        with pytest.raises(IndexError):
            calculate_sma("TEST", 10)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_sma("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify SMA of constant prices equals that constant."""
        mock_stock_data([50, 50, 50, 50, 50, 50])
        result = calculate_sma("TEST", 2)
        assert result.iloc[-1] == 50.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify SMA handles a zigzag [10, 20] pattern."""
        mock_stock_data([10, 20, 10, 20, 10, 20, 10, 20])
        result = calculate_sma("TEST", 3)
        assert result.iloc[-1] == pytest.approx(16.6667, abs=0.0001)

    def test_large_prices(self, mock_stock_data):
        """Verify SMA handles prices around 1e9 without overflow."""
        mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                         1.004e9])
        result = calculate_sma("TEST", 2)
        assert result.iloc[-1] == 1.0035e9

    def test_negative_prices(self, mock_stock_data):
        """Verify SMA handles negative prices."""
        mock_stock_data([-10, -9, -8, -7, -6, -5, -4])
        result = calculate_sma("TEST", 3)
        assert result.iloc[-1] == -5.0

    def test_spike_pattern(self, mock_stock_data):
        """Verify SMA recovers after one large spike."""
        mock_stock_data([10, 10, 10, 10, 1000, 10, 10, 10,
                         10, 10])
        result = calculate_sma("TEST", 3)
        assert result.iloc[-1] == 10.0

    def test_single_price_point(self, mock_stock_data):
        """Verify SMA with one price equals that price."""
        mock_stock_data([42])
        result = calculate_sma("TEST", 1)
        assert result.iloc[-1] == 42.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify SMA works on a 20-point sequence."""
        mock_stock_data(list(range(20)))
        result = calculate_sma("TEST", 5)
        assert len(result) == 1
        assert result.iloc[-1] == 17.0

    def test_large_window(self, mock_stock_data):
        """Verify SMA with a window close to data length."""
        mock_stock_data(list(range(10)))
        result = calculate_sma("TEST", 8)
        assert len(result) == 1
        assert result.iloc[-1] == 5.5

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N SMA values."""
        mock_stock_data(list(range(9)))
        result = calculate_sma("TEST", 3, count=3)
        assert len(result) == 3
        assert result.iloc[-1] == 7.0

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available values."""
        mock_stock_data([10, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_sma("TEST", 2, count=5)
