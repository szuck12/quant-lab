# test_calculate_stoch.py
# Tests for calculate_stoch() with mocked yfinance data

import pytest
import pandas as pd
from indicators.stoch import calculate_stoch


class TestCalculateStoch:
    """Tests for calculate_stoch()."""

    def test_basic_stoch(self, mock_stock_data):
        """Verify STOCH matches the known value for a small rising
        sequence with constant range."""
        mock_stock_data(list(range(44, 54)),
                        high_prices=[55] * 10,
                        low_prices=[40] * 10)
        k, d = calculate_stoch("TEST", window=3, smooth_k=3,
                               smooth_d=3)
        assert k.iloc[-1] == pytest.approx(80.0, abs=0.01)
        assert d.iloc[-1] == pytest.approx(73.3333, abs=0.01)

    def test_window_one(self, mock_stock_data):
        """Verify STOCH with window=smooth=1 equals 100% when close
        equals high."""
        mock_stock_data([10, 20],
                        high_prices=[20, 20],
                        low_prices=[5, 5])
        k, d = calculate_stoch("TEST", window=1, smooth_k=1,
                               smooth_d=1)
        assert k.iloc[-1] == 100.0
        assert d.iloc[-1] == 100.0

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length."""
        mock_stock_data([1, 2, 3],
                        high_prices=[5, 5, 5],
                        low_prices=[0, 0, 0])
        with pytest.raises(IndexError):
            calculate_stoch("TEST", 10)

    def test_insufficient_data(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], high_prices=[], low_prices=[])
        with pytest.raises(IndexError):
            calculate_stoch("TEST", 5)

    def test_constant_prices(self, mock_stock_data):
        """Verify STOCH handles all-identical prices."""
        mock_stock_data([50, 50, 50, 50, 50, 50],
                        high_prices=[55] * 6,
                        low_prices=[45] * 6)
        k, d = calculate_stoch("TEST", window=2, smooth_k=2,
                               smooth_d=2)
        assert k.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert d.iloc[-1] == pytest.approx(50.0, abs=0.0001)

    def test_alternating_pattern(self, mock_stock_data):
        """Verify STOCH handles a zigzag price pattern."""
        mock_stock_data([10, 20, 10, 20, 10, 20, 10, 20],
                        high_prices=[25] * 8,
                        low_prices=[5] * 8)
        k, d = calculate_stoch("TEST", window=3, smooth_k=3,
                               smooth_d=3)
        assert k.iloc[-1] == pytest.approx(58.3333, abs=0.01)
        assert d.iloc[-1] == pytest.approx(52.7778, abs=0.01)

    def test_large_prices(self, mock_stock_data):
        """Verify STOCH handles prices around 1e9."""
        closes = [1e9 + i * 1e6 for i in range(10)]
        mock_stock_data(closes,
                        high_prices=[1.01e9] * 10,
                        low_prices=[0.99e9] * 10)
        k, d = calculate_stoch("TEST", window=2, smooth_k=3,
                               smooth_d=3)
        assert k.iloc[-1] == pytest.approx(90.0, abs=0.01)
        assert d.iloc[-1] == pytest.approx(85.0, abs=0.01)

    def test_negative_prices(self, mock_stock_data):
        """Verify STOCH handles negative prices."""
        mock_stock_data([-10, -9, -8, -7, -6, -5, -4],
                        high_prices=[-2] * 7,
                        low_prices=[-12] * 7)
        k, d = calculate_stoch("TEST", window=3, smooth_k=3,
                               smooth_d=3)
        assert 0.0 <= k.iloc[-1] <= 100.0
        assert 0.0 <= d.iloc[-1] <= 100.0

    def test_spike_pattern(self, mock_stock_data):
        """Verify STOCH handles one high spike in a flat series."""
        mock_stock_data([10, 10, 10, 10, 1000, 10, 10, 10, 10,
                         10],
                        high_prices=[1000] * 10,
                        low_prices=[5] * 10)
        k, d = calculate_stoch("TEST", window=3, smooth_k=3,
                               smooth_d=3)
        assert k.iloc[-1] == pytest.approx(0.5025, abs=0.01)
        assert d.iloc[-1] == pytest.approx(0.5025, abs=0.01)

    def test_single_price_point(self, mock_stock_data):
        """Verify STOCH with only one data point."""
        mock_stock_data([42],
                        high_prices=[50],
                        low_prices=[40])
        k, d = calculate_stoch("TEST", window=1, smooth_k=1,
                               smooth_d=1)
        assert k.iloc[-1] == 20.0
        assert d.iloc[-1] == 20.0

    def test_twenty_data_points(self, mock_stock_data):
        """Verify STOCH works on a 20-point sequence."""
        mock_stock_data(list(range(20)),
                        high_prices=[25] * 20,
                        low_prices=[0] * 20)
        k, d = calculate_stoch("TEST", 5, smooth_k=3,
                               smooth_d=3)
        assert len(k) == 1
        assert len(d) == 1
        assert k.iloc[-1] > 0.0
        assert d.iloc[-1] > 0.0

    def test_large_window(self, mock_stock_data):
        """Verify STOCH with a window close to data length."""
        mock_stock_data(list(range(10)),
                        high_prices=[20] * 10,
                        low_prices=[0] * 10)
        k, d = calculate_stoch("TEST", 8, smooth_k=2,
                               smooth_d=2)
        assert len(k) == 1
        assert len(d) == 1
        assert k.iloc[-1] is not None
        assert d.iloc[-1] is not None

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N values."""
        mock_stock_data(list(range(44, 54)),
                        high_prices=[55] * 10,
                        low_prices=[40] * 10)
        k, d = calculate_stoch("TEST", window=3, smooth_k=3,
                               smooth_d=3, count=3)
        assert len(k) == 3
        assert len(d) == 3
        assert k.iloc[-1] == pytest.approx(80.0, abs=0.01)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available data."""
        mock_stock_data([10, 11, 12, 13, 14, 15],
                        high_prices=[20] * 6,
                        low_prices=[5] * 6)
        with pytest.raises(IndexError):
            calculate_stoch("TEST", 3, smooth_k=3, smooth_d=3,
                            count=5)
