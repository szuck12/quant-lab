# test_calculate_obv.py
# Tests for calculate_obv() using mocked stock data

import pytest
from indicators import calculate_obv


class TestCalculateObv:
    """Tests for calculate_obv()."""

    def test_basic_obv(self, mock_stock_data):
        """Verify OBV matches the known cumulative value for a
        4-point rising sequence."""
        mock_stock_data(
            [10, 11, 12, 13],
            volume_prices=[100, 200, 300, 400],
        )
        result = calculate_obv("TEST", 3)
        # Every close rises: +200 +300 +400 = 900.
        assert result.iloc[-1] == pytest.approx(900.0, abs=0.0001)

    def test_consecutive_increases(self, mock_stock_data):
        """Verify OBV sums volume across consecutive up bars."""
        mock_stock_data(
            [10, 11, 12, 13, 14],
            volume_prices=[10, 20, 30, 40, 50],
        )
        result = calculate_obv("TEST", 3)
        # +20 +30 +40 +50 = 140.
        assert result.iloc[-1] == pytest.approx(140.0, abs=0.0001)

    def test_consecutive_decreases(self, mock_stock_data):
        """Verify OBV subtracts volume across consecutive down
        bars."""
        mock_stock_data(
            [15, 14, 13, 12],
            volume_prices=[10, 20, 30, 40],
        )
        result = calculate_obv("TEST", 3)
        # -20 -30 -40 = -90.
        assert result.iloc[-1] == pytest.approx(-90.0, abs=0.0001)

    def test_unchanged_prices(self, mock_stock_data):
        """Verify equal closes leave the running total
        unchanged."""
        mock_stock_data(
            [10, 10, 11, 11, 10],
            volume_prices=[1, 2, 3, 4, 5],
        )
        result = calculate_obv("TEST", 3)
        # 0, +3, 0, -5 -> -2.
        assert result.iloc[-1] == pytest.approx(-2.0, abs=0.0001)

    def test_alternating_pattern(self, mock_stock_data):
        """Verify OBV handles a zigzag price pattern."""
        mock_stock_data(
            [10, 20, 10, 20],
            volume_prices=[10, 10, 10, 10],
        )
        result = calculate_obv("TEST", 3)
        # +10 -10 +10 = 10.
        assert result.iloc[-1] == pytest.approx(10.0, abs=0.0001)

    def test_large_volume_dominance(self, mock_stock_data):
        """Verify one huge-volume move dominates later small
        moves."""
        mock_stock_data(
            [10, 11, 10, 9],
            volume_prices=[1, 1000000, 1, 1],
        )
        result = calculate_obv("TEST", 3)
        # +1000000 -1 -1 = 999998.
        assert result.iloc[-1] == pytest.approx(999998.0,
                                                abs=0.0001)

    def test_zero_volumes(self, mock_stock_data):
        """Verify all-zero volume is a valid zero result (no
        division in OBV)."""
        mock_stock_data(
            [10, 11, 12, 13],
            volume_prices=[0, 0, 0, 0],
        )
        result = calculate_obv("TEST", 3)
        assert result.iloc[-1] == pytest.approx(0.0, abs=0.0001)

    def test_mixed_zero_volume(self, mock_stock_data):
        """Verify zero-volume bars contribute nothing."""
        mock_stock_data(
            [10, 11, 12, 11],
            volume_prices=[0, 5, 0, 7],
        )
        result = calculate_obv("TEST", 3)
        # +5 +0 -7 = -2.
        assert result.iloc[-1] == pytest.approx(-2.0, abs=0.0001)

    def test_negative_volumes(self, mock_stock_data):
        """Verify OBV handles negative volumes arithmetically."""
        mock_stock_data(
            [10, 11, 12],
            volume_prices=[-100, -200, -300],
        )
        result = calculate_obv("TEST", 2)
        # -200 + -300 = -500.
        assert result.iloc[-1] == pytest.approx(-500.0, abs=0.0001)

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify window larger than the data still computes —
        OBV is cumulative from the fetched start, so only fewer
        than two bars is insufficient."""
        mock_stock_data(
            [10, 11, 12],
            volume_prices=[1, 2, 3],
        )
        result = calculate_obv("TEST", 10)
        # +2 +3 = 5.
        assert len(result) == 1
        assert result.iloc[-1] == pytest.approx(5.0, abs=0.0001)

    def test_single_price_point(self, mock_stock_data):
        """Verify IndexError with only one bar (no previous
        close)."""
        mock_stock_data([42], volume_prices=[100])
        with pytest.raises(IndexError):
            calculate_obv("TEST", 1)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], volume_prices=[])
        with pytest.raises(IndexError):
            calculate_obv("TEST", 5)

    def test_twenty_data_points(self, mock_stock_data):
        """Verify OBV works on a 20-point sequence."""
        n = 20
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_obv("TEST", 5)
        # Strictly increasing: sum of volumes 1..19 = 190.
        assert len(result) == 1
        assert result.iloc[-1] == pytest.approx(190.0, abs=0.0001)

    def test_large_window(self, mock_stock_data):
        """Verify OBV with a window close to data length."""
        n = 10
        mock_stock_data(
            list(range(n)),
            volume_prices=list(range(n)),
        )
        result = calculate_obv("TEST", 8)
        # Sum of volumes 1..9 = 45.
        assert len(result) == 1
        assert result.iloc[-1] == pytest.approx(45.0, abs=0.0001)

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N OBV values."""
        mock_stock_data(
            [10, 11, 12, 13, 14],
            volume_prices=[1, 1, 1, 1, 1],
        )
        result = calculate_obv("TEST", 3, count=3)
        # Cumulative: 1, 2, 3, 4 -> last three are 2, 3, 4.
        assert len(result) == 3
        assert result.iloc[-1] == pytest.approx(4.0, abs=0.0001)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data(
            [10, 11, 12, 13],
            volume_prices=[1, 2, 3, 4],
        )
        with pytest.raises(IndexError):
            calculate_obv("TEST", 2, count=5)

    def test_default_window_obv(self, mock_stock_data):
        """Verify default window=30 is used when no window
        given."""
        mock_stock_data(
            list(range(10, 20)),
            volume_prices=[10] * 10,
        )
        result = calculate_obv("TEST")
        # Strictly increasing: 9 bars x 10 volume = 90.
        assert len(result) == 1
        assert result.iloc[-1] == pytest.approx(90.0, abs=0.0001)
