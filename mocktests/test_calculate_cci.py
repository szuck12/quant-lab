# test_calculate_cci.py
# Tests for calculate_cci() with mocked yfinance data

import numpy as np
import pytest
from indicators.cci import calculate_cci


class TestCalculateCci:
    """Tests for calculate_cci()."""

    def test_basic_cci(self, mock_stock_data):
        """Verify CCI matches the hand-computed value for a
        small sequence."""
        # H=L=C so Typical Price equals Close.
        mock_stock_data([10, 10, 10, 22],
                        high_prices=[10, 10, 10, 22],
                        low_prices=[10, 10, 10, 22])
        result = calculate_cci("TEST", 4)
        # SMA=13, MAD=(3+3+3+9)/4=4.5 ->
        # (22-13)/(0.015*4.5)=133.3333.
        assert result.iloc[-1] == pytest.approx(133.3333,
                                                abs=0.0001)
        assert result.iloc[-1] > 100.0

    def test_typical_price_uses_hlc(self, mock_stock_data):
        """Verify CCI is computed from Typical Price, not the
        close alone."""
        mock_stock_data([10, 11, 12, 13, 14],
                        high_prices=[11, 12, 13, 14, 15],
                        low_prices=[9, 10, 11, 12, 13])
        result = calculate_cci("TEST", 5)
        # TP=[10..14], SMA=12,
        # MAD=(2+1+0+1+2)/5=1.2 -> 2/(0.015*1.2)=111.1111.
        assert result.iloc[-1] == pytest.approx(111.1111,
                                                abs=0.0001)

    def test_window_two(self, mock_stock_data):
        """Verify CCI with window=2 matches a hand-computed
        value."""
        mock_stock_data([10, 14],
                        high_prices=[10, 14],
                        low_prices=[10, 14])
        result = calculate_cci("TEST", 2)
        # SMA=12, MAD=2 -> (14-12)/(0.015*2)=66.6667.
        assert result.iloc[-1] == pytest.approx(66.6667,
                                                abs=0.0001)

    def test_zero_deviation_exact(self, mock_stock_data):
        """Verify CCI is exactly zero when the last Typical
        Price equals its SMA."""
        mock_stock_data([10, 10, 16, 12],
                        high_prices=[10, 10, 16, 12],
                        low_prices=[10, 10, 16, 12])
        result = calculate_cci("TEST", 4)
        # SMA=12 equals last TP; MAD=2 -> 0/0.03 = 0.
        assert result.iloc[-1] == pytest.approx(0.0, abs=1e-9)

    def test_constant_prices(self, mock_stock_data):
        """Verify constant prices give zero Mean Deviation and
        raise IndexError instead of dividing by zero."""
        mock_stock_data([50] * 6,
                        high_prices=[50] * 6,
                        low_prices=[50] * 6)
        with pytest.raises(IndexError):
            calculate_cci("TEST", 3)

    def test_window_one_insufficient(self, mock_stock_data):
        """Verify window=1 raises IndexError — every window's
        Mean Deviation is zero by definition."""
        mock_stock_data([10, 11, 12],
                        high_prices=[10, 11, 12],
                        low_prices=[10, 11, 12])
        with pytest.raises(IndexError):
            calculate_cci("TEST", 1)

    def test_window_exceeds_data(self, mock_stock_data):
        """Verify IndexError when window exceeds data length
        (rolling semantics produce all NaN)."""
        mock_stock_data([1, 2, 3],
                        high_prices=[5, 5, 5],
                        low_prices=[0, 0, 0])
        with pytest.raises(IndexError):
            calculate_cci("TEST", 10)

    def test_insufficient_data_empty(self, mock_stock_data):
        """Verify IndexError with no data."""
        mock_stock_data([], high_prices=[], low_prices=[])
        with pytest.raises(IndexError):
            calculate_cci("TEST", 5)

    def test_count_exceeds_data(self, mock_stock_data):
        """Verify IndexError when count exceeds available
        values."""
        mock_stock_data([10, 11, 12, 13],
                        high_prices=[20] * 4,
                        low_prices=[5] * 4)
        with pytest.raises(IndexError):
            calculate_cci("TEST", 2, count=5)

    def test_above_average_positive(self, mock_stock_data):
        """Verify rising Typical Prices give positive CCI."""
        n = 8
        closes = list(range(10, 10 + n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        result = calculate_cci("TEST", 4)
        assert result.iloc[-1] > 0.0

    def test_below_average_negative(self, mock_stock_data):
        """Verify falling Typical Prices give negative CCI."""
        closes = list(range(17, 9, -1))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        result = calculate_cci("TEST", 4)
        assert result.iloc[-1] < 0.0

    def test_large_deviation_larger_magnitude(self,
                                              mock_stock_data):
        """Verify larger deviation relative to Mean Deviation
        produces larger |CCI|."""
        mock_stock_data([10, 11, 12, 30],
                        high_prices=[10, 11, 12, 30],
                        low_prices=[10, 11, 12, 30])
        extreme = calculate_cci("TEST", 4)
        mock_stock_data([10, 11, 12, 14],
                        high_prices=[10, 11, 12, 14],
                        low_prices=[10, 11, 12, 14])
        moderate = calculate_cci("TEST", 4)
        assert abs(extreme.iloc[-1]) > abs(moderate.iloc[-1])

    def test_nan_resilience(self, mock_stock_data):
        """Verify a NaN high mid-series still yields finite
        results once clean windows are available."""
        mock_stock_data([10, 11, 12, 13, 14, 15, 16],
                        high_prices=[11, np.nan, 13, 14, 15,
                                     16, 17],
                        low_prices=[9, 10, 11, 12, 13, 14,
                                    15])
        result = calculate_cci("TEST", 3)
        assert np.isfinite(result.iloc[-1])

    def test_count_multiple(self, mock_stock_data):
        """Verify count returns the last N values."""
        mock_stock_data([10, 11, 12, 13, 14],
                        high_prices=[11, 12, 13, 14, 15],
                        low_prices=[9, 10, 11, 12, 13])
        result = calculate_cci("TEST", 3, count=3)
        # Every 3-bar window of a linear ramp gives
        # SMA=middle, MAD=2/3 -> CCI=100.
        assert len(result) == 3
        for value in result:
            assert value == pytest.approx(100.0, abs=0.0001)

    def test_large_prices(self, mock_stock_data):
        """Verify CCI is scale-invariant around 1e9 prices."""
        scale = 1e8
        base = [10, 10, 10, 22]
        scaled = [v * scale for v in base]
        mock_stock_data(scaled,
                        high_prices=scaled,
                        low_prices=scaled)
        result = calculate_cci("TEST", 4)
        assert result.iloc[-1] == pytest.approx(133.3333,
                                                rel=1e-6)

    def test_negative_prices(self, mock_stock_data):
        """Verify CCI handles negative prices (differences are
        unchanged by shifts)."""
        shifted = [v - 100 for v in [10, 10, 10, 22]]
        mock_stock_data(shifted,
                        high_prices=shifted,
                        low_prices=shifted)
        result = calculate_cci("TEST", 4)
        assert result.iloc[-1] == pytest.approx(133.3333,
                                                abs=0.0001)

    def test_twenty_data_points(self, mock_stock_data):
        """Verify CCI works on a 20-point sequence."""
        n = 20
        closes = list(range(n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        result = calculate_cci("TEST", 5)
        assert len(result) == 1
        assert np.isfinite(result.iloc[-1])

    def test_default_window(self, mock_stock_data):
        """Verify default window=20 runs on sufficient data."""
        n = 40
        closes = list(range(n))
        mock_stock_data(closes,
                        high_prices=[c + 1 for c in closes],
                        low_prices=[c - 1 for c in closes])
        result = calculate_cci("TEST")
        assert len(result) == 1
        assert np.isfinite(result.iloc[-1])
