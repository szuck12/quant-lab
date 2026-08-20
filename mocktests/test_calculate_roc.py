# test_calculate_roc.py
# Tests for calculate_roc() using mocked stock data

import pytest
from indicators import calculate_roc


class TestCalculateRoc:
    """Tests for calculate_roc()."""

    def test_basic_roc(self, mock_stock_data):
        """Verify ROC matches the known percentage change for a
        6-point sequence with window=3."""
        mock_stock_data([10, 11, 12, 13, 14, 15])
        result = calculate_roc("TEST", 3)
        # (15 - 12) / 12 * 100 = 25.0
        assert result.iloc[-1] == pytest.approx(25.0, abs=0.0001)

    def test_window_one(self, mock_stock_data):
        """Verify ROC with window=1 is the last bar's percent
        change."""
        mock_stock_data([10, 20])
        result = calculate_roc("TEST", 1)
        assert result.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length."""
        mock_stock_data([1, 2, 3])
        with pytest.raises(IndexError):
            calculate_roc("TEST", 10)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([])
        with pytest.raises(IndexError):
            calculate_roc("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify ROC of constant prices is zero."""
        mock_stock_data([50, 50, 50, 50, 50, 50])
        result = calculate_roc("TEST", 2)
        assert result.iloc[-1] == pytest.approx(0.0, abs=0.0001)

    def test_alternating_pattern(self, mock_stock_data):
        """Verify ROC handles a zigzag [10, 20] pattern."""
        mock_stock_data([10, 20, 10, 20, 10, 20, 10, 20])
        result = calculate_roc("TEST", 3)
        # Last close 20 vs close 3 bars ago 10 -> +100%.
        assert result.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_large_prices(self, mock_stock_data):
        """Verify ROC handles prices around 1e9 without overflow."""
        mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                         1.004e9])
        result = calculate_roc("TEST", 2)
        expected = (1.004e9 - 1.002e9) / 1.002e9 * 100
        assert result.iloc[-1] == pytest.approx(expected, rel=1e-6)

    def test_negative_prices(self, mock_stock_data):
        """Verify ROC handles negative prices."""
        mock_stock_data([-10, -9, -8, -7, -6, -5, -4])
        result = calculate_roc("TEST", 3)
        expected = (-4 - (-7)) / -7 * 100
        assert result.iloc[-1] == pytest.approx(expected,
                                                abs=0.0001)

    def test_spike_pattern(self, mock_stock_data):
        """Verify ROC recovers after one large spike."""
        mock_stock_data([10, 10, 10, 10, 1000, 10, 10, 10,
                         10, 10])
        result = calculate_roc("TEST", 3)
        assert result.iloc[-1] == pytest.approx(0.0, abs=0.0001)

    def test_single_price_point(self, mock_stock_data):
        """Verify IndexError with only one data point (ROC needs
        window + 1 bars)."""
        mock_stock_data([42])
        with pytest.raises(IndexError):
            calculate_roc("TEST", 1)

    def test_twenty_data_points(self, mock_stock_data):
        """Verify ROC works on a 20-point sequence."""
        mock_stock_data(list(range(20)))
        result = calculate_roc("TEST", 5)
        assert len(result) == 1
        assert result.iloc[-1] > 0.0

    def test_large_window(self, mock_stock_data):
        """Verify ROC with a window close to data length."""
        mock_stock_data(list(range(10)))
        result = calculate_roc("TEST", 8)
        assert len(result) == 1
        assert result.iloc[-1] == pytest.approx(800.0, abs=0.0001)

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N ROC values."""
        mock_stock_data(list(range(9)))
        result = calculate_roc("TEST", 3, count=3)
        assert len(result) == 3
        # Last value: (8 - 5) / 5 * 100 = 60.0.
        assert result.iloc[-1] == pytest.approx(60.0, abs=0.0001)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data([10, 11, 12, 13])
        with pytest.raises(IndexError):
            calculate_roc("TEST", 2, count=5)

    def test_default_window_roc(self, mock_stock_data):
        """Verify default window=9 is used when no window
        given."""
        mock_stock_data(list(range(20)))
        result = calculate_roc("TEST")
        assert len(result) == 1
        # Close 19 vs close 9 bars ago (10): 90%.
        expected = (19 - 10) / 10 * 100
        assert result.iloc[-1] == pytest.approx(expected,
                                                abs=0.0001)

    def test_zero_price_denominator(self, mock_stock_data):
        """Verify a zero close `window` bars ago is treated as
        undefined and raises IndexError when no valid values
        remain."""
        mock_stock_data([0, 10, 12, 14])
        with pytest.raises(IndexError):
            calculate_roc("TEST", 3)

    def test_zero_price_partial_recovery(self, mock_stock_data):
        """Verify only the affected row is dropped when a zero
        denominator exists but later valid rows remain."""
        mock_stock_data([0, 10, 12, 14, 16])
        result = calculate_roc("TEST", 3)
        assert len(result) == 1
        # (16 - 10) / 10 * 100 = 60.0
        assert result.iloc[-1] == pytest.approx(60.0, abs=0.0001)
