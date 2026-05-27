# test_calculate_atr.py
# Tests for calculate_atr() using mocked stock data

import pytest
from indicators import calculate_atr


class TestCalculateAtr:
    """Tests for calculate_atr()."""

    def test_basic_atr(self, mock_stock_data):
        """Verify ATR matches Wilder-smoothed value for a 6-point
        sequence with window=3."""
        mock_stock_data(
            [50, 51, 52, 48, 47, 49],
            high_prices=[51, 53, 53, 50, 49, 50],
            low_prices=[49, 50, 50, 47, 46, 48],
        )
        result = calculate_atr("TEST", window=3)
        # TR = [2, 3, 3, 5, 3, 3]
        # ATR(3) Wilder: seed 2.0, then 2.3333, 2.5556, 3.3704, 3.2469, 3.1646
        assert result.iloc[-1] == pytest.approx(3.1646, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify ATR with window=1 equals the latest TR."""
        mock_stock_data(
            [10, 11, 12, 13],
            high_prices=[11, 12, 13, 14],
            low_prices=[9, 10, 11, 12],
        )
        result = calculate_atr("TEST", window=1)
        # Row 3: HL=14-12=2, HPC=|14-13|=1, LPC=|12-13|=1 -> TR=2
        assert result.iloc[-1] == 2.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify ATR still produces a value even when the window
        exceeds data length (Wilder smoothing seeds at the first
        non-NaN value, like RSI)."""
        mock_stock_data(
            [11.0, 13, 15],
            high_prices=[12.0, 14, 16],
            low_prices=[10.0, 12, 14],
        )
        result = calculate_atr("TEST", window=10)
        assert result.iloc[-1] >= 0

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], high_prices=[], low_prices=[])
        with pytest.raises(IndexError):
            calculate_atr("TEST", window=5)

    def test_constant_prices(self, mock_stock_data):
        """Verify ATR of constant prices equals zero."""
        n = 6
        mock_stock_data(
            [50.0] * n,
            high_prices=[50.0] * n,
            low_prices=[50.0] * n,
        )
        result = calculate_atr("TEST", window=2)
        # HL=0, HPC=0, LPC=0 => TR=0, ATR=0
        assert result.iloc[-1] == 0.0

    def test_alternating_pattern(self, mock_stock_data):
        """Verify ATR handles a zigzag price pattern."""
        mock_stock_data(
            [50, 60, 50, 60, 50, 60, 50, 60],
            high_prices=[52, 62, 52, 62, 52, 62, 52, 62],
            low_prices=[48, 58, 48, 58, 48, 58, 48, 58],
        )
        result = calculate_atr("TEST", window=3)
        assert result.iloc[-1] >= 0

    def test_large_prices(self, mock_stock_data):
        """Verify ATR handles prices around 1e9."""
        n = 6
        mock_stock_data(
            [1e9 + i for i in range(n)],
            high_prices=[1.001e9 + i for i in range(n)],
            low_prices=[0.999e9 + i for i in range(n)],
        )
        result = calculate_atr("TEST", window=2)
        assert result.iloc[-1] > 0

    def test_negative_prices(self, mock_stock_data):
        """Verify ATR handles negative prices (ATR >= 0)."""
        mock_stock_data(
            [-10, -11, -12, -13, -14, -15],
            high_prices=[-9, -10, -11, -12, -13, -14],
            low_prices=[-11, -12, -13, -14, -15, -16],
        )
        result = calculate_atr("TEST", window=3)
        assert result.iloc[-1] >= 0.0

    def test_spike_pattern(self, mock_stock_data):
        """Verify ATR handles a price spike."""
        n = 10
        mock_stock_data(
            [50.0] * 4 + [100] + [50.0] * 5,
            high_prices=[51.0] * 4 + [101] + [51.0] * 5,
            low_prices=[49.0] * 4 + [99] + [49.0] * 5,
        )
        result = calculate_atr("TEST", window=3)
        assert result.iloc[-1] > 0

    def test_single_price_point(self, mock_stock_data):
        """Verify ATR with one bar equals the high-low spread
        (TR is valid using just HL when prev_close is NaN)."""
        mock_stock_data(
            [42.0],
            high_prices=[43.0],
            low_prices=[41.0],
        )
        result = calculate_atr("TEST", window=1)
        assert result.iloc[-1] == 2.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify ATR works on a 20-point sequence."""
        n = 20
        mock_stock_data(
            list(range(n)),
            high_prices=[x + 1 for x in range(n)],
            low_prices=[x - 1 for x in range(n)],
        )
        result = calculate_atr("TEST", window=5)
        assert len(result) == 1
        assert result.iloc[-1] > 0

    def test_large_window(self, mock_stock_data):
        """Verify ATR with a window close to data length."""
        n = 10
        mock_stock_data(
            list(range(n)),
            high_prices=[x + 1 for x in range(n)],
            low_prices=[x - 1 for x in range(n)],
        )
        result = calculate_atr("TEST", window=8)
        assert len(result) == 1
        assert result.iloc[-1] > 0

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N ATR values."""
        n = 9
        mock_stock_data(
            list(range(n)),
            high_prices=[x + 1 for x in range(n)],
            low_prices=[x - 1 for x in range(n)],
        )
        result = calculate_atr("TEST", window=3, count=3)
        assert len(result) == 3

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available values."""
        mock_stock_data(
            [11.0, 13, 15, 17, 19, 21],
            high_prices=[12.0, 14, 16, 18, 20, 22],
            low_prices=[10.0, 12, 14, 16, 18, 20],
        )
        with pytest.raises(IndexError):
            calculate_atr("TEST", window=2, count=10)

    def test_wide_spread(self, mock_stock_data):
        """Verify ATR captures large high-low spreads."""
        n = 6
        mock_stock_data(
            [50.0] * n,
            high_prices=[60.0] * n,
            low_prices=[40.0] * n,
        )
        result = calculate_atr("TEST", window=3)
        # HL=20, HPC=|60-50|=10, LPC=|40-50|=10 => TR=20
        # ATR seeded at 20, Wilder smooth stays at 20
        assert result.iloc[-1] == pytest.approx(20.0, abs=0.01)
