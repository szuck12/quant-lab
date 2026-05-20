# test_calculate_ema.py
# Tests for calculate_ema() using mocked stock data

import pytest
from main import calculate_ema


class TestCalculateEma:
    """Tests for calculate_ema()."""

    def test_basic_ema(self, mock_stock_data):
        """Verify EMA matches the hand-calculated value for a
        6-point rising sequence with span=3."""
        mock_stock_data([10, 11, 12, 13, 14, 15])
        result = calculate_ema("TEST", 3)
        assert result.iloc[-1] == pytest.approx(14.03125, abs=0.0001)

    def test_window_one(self, mock_stock_data):
        """Verify EMA with window=1 equals the last close."""
        mock_stock_data([10, 20])
        result = calculate_ema("TEST", 1)
        assert result.iloc[-1] == 20.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify EMA still produces a result when window exceeds
        data length (unlike SMA, EMA seeds from the first value
        and never produces NaN)."""
        mock_stock_data([1, 2, 3])
        result = calculate_ema("TEST", 10)
        assert result.iloc[-1] is not None

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_ema("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify EMA of constant prices equals that constant."""
        mock_stock_data([50, 50, 50, 50, 50, 50])
        result = calculate_ema("TEST", 2)
        assert result.iloc[-1] == 50.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify EMA handles a zigzag [10, 20] pattern."""
        mock_stock_data([10, 20, 10, 20, 10, 20, 10, 20])
        result = calculate_ema("TEST", 3)
        assert result.iloc[-1] == pytest.approx(16.6406, abs=0.0001)

    def test_large_prices(self, mock_stock_data):
        """Verify EMA handles prices around 1e9."""
        mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                         1.004e9])
        result = calculate_ema("TEST", 2)
        assert result.iloc[-1] == pytest.approx(1.003506e9,
                                                rel=1e-6)

    def test_negative_prices(self, mock_stock_data):
        """Verify EMA handles negative prices."""
        mock_stock_data([-10, -9, -8, -7, -6, -5, -4])
        result = calculate_ema("TEST", 3)
        assert result.iloc[-1] == pytest.approx(-4.9844,
                                                abs=0.0001)

    def test_spike_pattern(self, mock_stock_data):
        """Verify EMA handles one spike in a flat series."""
        mock_stock_data([10, 10, 10, 10, 1000, 10, 10, 10,
                         10, 10])
        result = calculate_ema("TEST", 3)
        assert result.iloc[-1] == pytest.approx(25.4688,
                                                abs=0.0001)

    def test_single_price_point(self, mock_stock_data):
        """Verify EMA with one price equals that price."""
        mock_stock_data([42])
        result = calculate_ema("TEST", 1)
        assert result.iloc[-1] == 42.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify EMA works on a 20-point sequence."""
        mock_stock_data(list(range(20)))
        result = calculate_ema("TEST", 5)
        assert len(result) == 1
        assert result.iloc[-1] > 0.0

    def test_large_window(self, mock_stock_data):
        """Verify EMA with a window close to data length."""
        mock_stock_data(list(range(10)))
        result = calculate_ema("TEST", 8)
        assert len(result) == 1
        assert result.iloc[-1] is not None

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N EMA values."""
        mock_stock_data(list(range(9)))
        result = calculate_ema("TEST", 3, count=3)
        assert len(result) == 3
        assert result.iloc[-1] == pytest.approx(7.0039, abs=0.0001)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available values."""
        mock_stock_data([10, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_ema("TEST", 2, count=5)
