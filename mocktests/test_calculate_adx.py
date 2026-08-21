# test_calculate_adx.py
# Tests for calculate_adx() with mocked yfinance data

import numpy as np
import pytest
from indicators.adx import calculate_adx


class TestCalculateAdx:
    """Tests for calculate_adx()."""

    def test_basic_adx(self, mock_stock_data):
        """Verify ADX matches hand-computed values for a small
        sustained uptrend."""
        n = 10
        closes = list(range(10, 10 + n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=3,
                                               adx_window=3)
        # Every bar: +DM=1, -DM=0, TR=2 -> RMA values are
        # constant, so +DI=50, -DI=0, DX=100, ADX=100.
        assert plus_di.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(0.0, abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_sustained_downtrend(self, mock_stock_data):
        """Verify a sustained downtrend gives mirrored DI values
        and equally high ADX (ADX is non-directional)."""
        closes = list(range(19, 9, -1))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=3,
                                               adx_window=3)
        assert plus_di.iloc[-1] == pytest.approx(0.0, abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_choppy_market_exact(self, mock_stock_data):
        """Verify ADX matches the hand-computed RMA recursion for
        an alternating zigzag."""
        highs = [11, 12, 11, 12, 11, 12, 11, 12]
        lows = [9, 10, 9, 10, 9, 10, 9, 10]
        closes = [10, 11, 10, 11, 10, 11, 10, 11]
        mock_stock_data(closes, high_prices=highs,
                        low_prices=lows)
        plus_di, minus_di, adx = calculate_adx("TEST", window=2,
                                               adx_window=2)
        # RMA(+DM): 1,.5,.75,.625,.6875,.65625,.671875 ->
        # +DI = 33.59375; -DI = 16.40625.
        # DX: 100,0,50,25,37.5,31.25,34.375 ->
        # ADX RMA: 100,50,50,37.5,37.5,34.375,34.375.
        assert plus_di.iloc[-1] == pytest.approx(33.59375,
                                                 abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(16.40625,
                                                  abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(34.375, abs=0.0001)

    def test_choppy_lower_than_trending(self, mock_stock_data):
        """Verify a choppy market produces much lower ADX than a
        trending market (trend-strength concept)."""
        n = 24
        highs = [11, 12] * (n // 2)
        lows = [9, 10] * (n // 2)
        closes = [10, 11] * (n // 2)
        mock_stock_data(closes, high_prices=highs, low_prices=lows)
        _, _, choppy_adx = calculate_adx("TEST", window=2,
                                         adx_window=2)
        # Perfect alternation converges to the fixed point
        # +DI=33.33, -DI=16.67 -> DX=ADX=33.3333.
        assert choppy_adx.iloc[-1] == pytest.approx(33.3333,
                                                    abs=0.01)
        assert choppy_adx.iloc[-1] < 60.0

    def test_competing_movement(self, mock_stock_data):
        """Verify a bar where both movements are positive awards
        only the larger one (+DM is discarded when -DM wins)."""
        mock_stock_data([9, 11, 10],
                        high_prices=[10, 12, 15],
                        low_prices=[8, 10, 6])
        plus_di, minus_di, adx = calculate_adx("TEST", window=1,
                                               adx_window=1)
        # Bar 2: up=3, down=4 -> -DM=4, +DM=0.  TR=9, w=1 so
        # RMA(x)=x: +DI=0, -DI=44.4444, DX=100, ADX=100.
        assert plus_di.iloc[-1] == pytest.approx(0.0, abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(44.4444,
                                                  abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_gap_bar_tr(self, mock_stock_data):
        """Verify True Range picks up the gap via previous
        close."""
        mock_stock_data([10, 20, 21],
                        high_prices=[11, 21, 22],
                        low_prices=[9, 19, 20])
        plus_di, _, _ = calculate_adx("TEST", window=1,
                                      adx_window=1, count=2)
        # Bar 1 TR = max(2, |21-10|, |19-10|) = 11 (gap);
        # +DM=10 -> +DI = 90.9091.  Bar 2: TR=2, +DM=1 -> 50.
        assert plus_di.iloc[0] == pytest.approx(90.9091,
                                                abs=0.0001)
        assert plus_di.iloc[1] == pytest.approx(50.0, abs=0.0001)

    def test_equal_extremes_no_movement(self, mock_stock_data):
        """Verify equal highs/lows yield no directional movement
        -> DX is NaN everywhere -> IndexError."""
        mock_stock_data([12, 13, 12, 14, 12, 13],
                        high_prices=[15] * 6,
                        low_prices=[10] * 6)
        with pytest.raises(IndexError):
            calculate_adx("TEST", window=2, adx_window=2)

    def test_zero_range_bars(self, mock_stock_data):
        """Verify zero True Range (flat H=L=C) raises
        IndexError instead of dividing by zero."""
        mock_stock_data([50] * 6,
                        high_prices=[50] * 6,
                        low_prices=[50] * 6)
        with pytest.raises(IndexError):
            calculate_adx("TEST", window=2, adx_window=2)

    def test_nan_high_resilience(self, mock_stock_data):
        """Verify a NaN high mid-series still yields finite
        results."""
        mock_stock_data([10, 11, 12, 13, 14, 15],
                        high_prices=[11, np.nan, 13, 14, 15,
                                     16],
                        low_prices=[9, 10, 11, 12, 13, 14])
        plus_di, minus_di, adx = calculate_adx("TEST", window=2,
                                               adx_window=2)
        assert np.isfinite(plus_di.iloc[-1])
        assert np.isfinite(minus_di.iloc[-1])
        assert np.isfinite(adx.iloc[-1])

    def test_insufficient_data_empty(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], high_prices=[], low_prices=[])
        with pytest.raises(IndexError):
            calculate_adx("TEST", window=5, adx_window=5)

    def test_single_bar(self, mock_stock_data):
        """Verify IndexError with only one bar (no previous
        bar)."""
        mock_stock_data([42], high_prices=[43],
                        low_prices=[41])
        with pytest.raises(IndexError):
            calculate_adx("TEST", window=1, adx_window=1)

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify windows larger than the data still compute —
        Wilder smoothing is recursive, not rolling."""
        n = 6
        closes = list(range(10, 10 + n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=10,
                                               adx_window=10)
        assert len(plus_di) == 1
        assert len(minus_di) == 1
        assert len(adx) == 1
        assert 0.0 <= adx.iloc[-1] <= 100.0

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N triples."""
        n = 10
        closes = list(range(10, 10 + n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=3,
                                               adx_window=3,
                                               count=3)
        assert len(plus_di) == 3
        assert len(minus_di) == 3
        assert len(adx) == 3
        assert plus_di.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        n = 4
        closes = list(range(10, 10 + n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        with pytest.raises(IndexError):
            calculate_adx("TEST", window=2, adx_window=2,
                          count=5)

    def test_large_prices(self, mock_stock_data):
        """Verify ADX is scale-invariant around 1e9 prices."""
        n = 10
        closes = [1e9 + i * 1e8 for i in range(n)]
        mock_stock_data(closes,
                        high_prices=[c + 1e8 for c in closes],
                        low_prices=[c - 1e8 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=3,
                                               adx_window=3)
        assert plus_di.iloc[-1] == pytest.approx(50.0,
                                                 rel=1e-9)
        assert minus_di.iloc[-1] == pytest.approx(0.0,
                                                  abs=1e-9)
        assert adx.iloc[-1] == pytest.approx(100.0,
                                             rel=1e-9)

    def test_negative_prices(self, mock_stock_data):
        """Verify ADX handles negative prices (differences are
        unchanged by shifts)."""
        closes = list(range(-90, -80))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=3,
                                               adx_window=3)
        assert plus_di.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(0.0, abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_twenty_data_points(self, mock_stock_data):
        """Verify ADX works on a 20-point uptrend."""
        n = 20
        closes = list(range(n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST", window=5,
                                               adx_window=3)
        assert len(plus_di) == 1
        assert plus_di.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(0.0, abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_default_params(self, mock_stock_data):
        """Verify defaults (14, 14) produce valid output on a
        long enough trend."""
        n = 40
        closes = list(range(n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        plus_di, minus_di, adx = calculate_adx("TEST")
        assert plus_di.iloc[-1] == pytest.approx(50.0, abs=0.0001)
        assert minus_di.iloc[-1] == pytest.approx(0.0, abs=0.0001)
        assert adx.iloc[-1] == pytest.approx(100.0, abs=0.0001)

    def test_nondirectionality(self, mock_stock_data):
        """Verify ADX is identical for a trend and its mirror —
        strength without direction."""
        up = list(range(10, 20))
        down = list(range(19, 9, -1))
        mock_stock_data(up,
                        high_prices=[c + 1 for c in up],
                        low_prices=[c - 1 for c in up])
        _, _, adx_up = calculate_adx("TEST", window=3,
                                     adx_window=3)
        mock_stock_data(down,
                        high_prices=[c + 1 for c in down],
                        low_prices=[c - 1 for c in down])
        _, _, adx_down = calculate_adx("TEST", window=3,
                                       adx_window=3)
        assert adx_up.iloc[-1] == pytest.approx(
            adx_down.iloc[-1], abs=0.0001)
