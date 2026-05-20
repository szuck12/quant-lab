# test_calculate_sma.py
# Tests for calculate_sma() using mocked stock data

import pytest
from unittest.mock import patch
from main import calculate_sma


class TestCalculateSma:
    """Tests for calculate_sma()."""

    def test_basic_sma(self, mock_stock_data):
        """Verify SMA matches the average of the last `window` values."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_sma("TEST", 3)
        assert result.iloc[-1] == 13.0

    def test_window_one(self, mock_stock_data):
        """Verify SMA with window=1 equals the last close price."""
        mock_stock_data([10, 20, 30])
        result = calculate_sma("TEST", 1)
        assert result.iloc[-1] == 30.0

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError is raised when there is not enough data."""
        mock_stock_data([10, 20])
        with pytest.raises(IndexError):
            calculate_sma("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify SMA of constant prices equals that constant value."""
        mock_stock_data([50, 50, 50, 50])
        result = calculate_sma("TEST", 2)
        assert result.iloc[-1] == 50.0

    def test_with_weekly_interval(self, mock_stock_data):
        """Verify SMA works with a weekly bar interval."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_sma("TEST", 3, interval="1wk")
        assert result.iloc[-1] == 13.0

    def test_with_monthly_interval(self, mock_stock_data):
        """Verify SMA works with a monthly bar interval."""
        mock_stock_data([100, 102, 104, 106, 108])
        result = calculate_sma("TEST", 3, interval="1mo")
        assert result.iloc[-1] == 106.0

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N SMA values."""
        mock_stock_data([10, 11, 12, 13, 14, 15, 16])
        result = calculate_sma("TEST", 3, count=3)
        assert len(result) == 3
        assert result.iloc[-1] == 15.0

    def test_count_one(self, mock_stock_data):
        """Verify count=1 returns a single-element Series."""
        mock_stock_data([10, 11, 12, 13, 14])
        result = calculate_sma("TEST", 3, count=1)
        assert len(result) == 1
        assert result.iloc[-1] == 13.0

    def test_count_with_interval(self, mock_stock_data):
        """Verify count works alongside a custom interval."""
        mock_stock_data([10, 11, 12, 13, 14, 15])
        result = calculate_sma("TEST", 3, interval="1wk", count=2)
        assert len(result) == 2
        # SMA: [11, 12, 13, 14], last 2: [13, 14]
        assert result.iloc[-1] == 14.0

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available SMA values."""
        mock_stock_data([10, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_sma("TEST", 2, count=5)
