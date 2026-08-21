# test_main.py
# Tests for the main() entry point dispatch logic

import pytest
from unittest.mock import patch
import pandas as pd
import main


_MOCK_SERIES = pd.Series([42.0])
_MOCK_MACD = (pd.Series([42.0]), pd.Series([12.0]),
              pd.Series([30.0]))
_MOCK_BB = (pd.Series([44.0]), pd.Series([42.0]),
            pd.Series([40.0]))
_MOCK_SERIES_VWAP = pd.Series([105.0])
_MOCK_SERIES_AV = pd.Series([20000.0])
_MOCK_SERIES_RVOL = pd.Series([1.2])
_MOCK_STOCH = (pd.Series([80.0]), pd.Series([75.0]))
_MOCK_ADX = (pd.Series([25.0]), pd.Series([15.0]),
             pd.Series([30.0]))


class TestMain:
    """Tests for main()."""

    # ---- ADX dispatch ----

    def test_valid_adx_dispatch(self):
        """Verify main() calls calculate_adx for an ADX input."""
        with patch("builtins.input",
                   return_value="AAPL ADX 14,14"):
            with patch("main.calculate_adx",
                       return_value=_MOCK_ADX) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", window=14, adx_window=14,
                    interval="1d", count=1)

    def test_default_window_adx(self):
        """Verify ADX defaults to (14, 14) when not provided."""
        with patch("builtins.input",
                   return_value="AAPL ADX"):
            with patch("main.calculate_adx",
                       return_value=_MOCK_ADX) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", window=14, adx_window=14,
                    interval="1d", count=1)

    # ---- ATR dispatch ----

    def test_valid_atr_dispatch(self):
        """Verify main() calls calculate_atr for an ATR input."""
        with patch("builtins.input",
                   return_value="AAPL ATR 14"):
            with patch("main.calculate_atr",
                       return_value=_MOCK_SERIES) as mock_atr:
                main.main()
                mock_atr.assert_called_once_with(
                    "AAPL", 14, interval="1d", count=1)

    def test_default_window_atr(self):
        """Verify ATR defaults to window=14 when not provided."""
        with patch("builtins.input",
                   return_value="AAPL ATR"):
            with patch("main.calculate_atr",
                       return_value=_MOCK_SERIES) as mock_atr:
                main.main()
                mock_atr.assert_called_once_with(
                    "AAPL", 14, interval="1d", count=1)

    # ---- CCI dispatch ----

    def test_valid_cci_dispatch(self):
        """Verify main() calls calculate_cci for a CCI input."""
        with patch("builtins.input",
                   return_value="AAPL CCI 20"):
            with patch("main.calculate_cci",
                       return_value=_MOCK_SERIES) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    def test_default_window_cci(self):
        """Verify CCI defaults to window=20 when not provided."""
        with patch("builtins.input",
                   return_value="AAPL CCI"):
            with patch("main.calculate_cci",
                       return_value=_MOCK_SERIES) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    # ---- ROC dispatch ----

    def test_valid_roc_dispatch(self):
        """Verify main() calls calculate_roc for an ROC input."""
        with patch("builtins.input",
                   return_value="AAPL ROC 9"):
            with patch("main.calculate_roc",
                       return_value=_MOCK_SERIES) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 9, interval="1d", count=1)

    def test_default_window_roc(self):
        """Verify ROC defaults to window=9 when not provided."""
        with patch("builtins.input",
                   return_value="AAPL ROC"):
            with patch("main.calculate_roc",
                       return_value=_MOCK_SERIES) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 9, interval="1d", count=1)

    # ---- OBV dispatch ----

    def test_valid_obv_dispatch(self):
        """Verify main() calls calculate_obv for an OBV input."""
        with patch("builtins.input",
                   return_value="AAPL OBV 30"):
            with patch("main.calculate_obv",
                       return_value=_MOCK_SERIES) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 30, interval="1d", count=1)

    def test_default_window_obv(self):
        """Verify OBV defaults to window=30 when not provided."""
        with patch("builtins.input",
                   return_value="AAPL OBV"):
            with patch("main.calculate_obv",
                       return_value=_MOCK_SERIES) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 30, interval="1d", count=1)

    # ---- dispatch with explicit window ----

    def test_valid_sma_dispatch(self):
        """Verify main() calls calculate_sma for an SMA input."""
        with patch("builtins.input", return_value="AAPL SMA 20"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    def test_valid_ema_dispatch(self):
        """Verify main() calls calculate_ema for an EMA input."""
        with patch("builtins.input", return_value="TSLA EMA 15"):
            with patch("main.calculate_ema", return_value=_MOCK_SERIES) as mock_ema:
                main.main()
                mock_ema.assert_called_once_with(
                    "TSLA", 15, interval="1d", count=1)

    def test_valid_rsi_dispatch(self):
        """Verify main() calls calculate_rsi for an RSI input."""
        with patch("builtins.input", return_value="MSFT RSI 14"):
            with patch("main.calculate_rsi", return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with(
                    "MSFT", 14, interval="1d", count=1)

    # ---- default windows ----

    def test_default_window_sma(self):
        """Verify SMA defaults to window=50 when not provided."""
        with patch("builtins.input", return_value="AAPL SMA"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 50, interval="1d", count=1)

    # ---- STOCH dispatch ----

    def test_valid_stoch_dispatch(self):
        """Verify main() calls calculate_stoch for a STOCH input
        with explicit parameters."""
        with patch("builtins.input",
                   return_value="AAPL STOCH 14,3,3"):
            with patch("main.calculate_stoch",
                       return_value=_MOCK_STOCH) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", window=14, smooth_k=3, smooth_d=3,
                    interval="1d", count=1)

    def test_default_window_stoch(self):
        """Verify STOCH defaults to (14,3,3) when not provided."""
        with patch("builtins.input",
                   return_value="AAPL STOCH"):
            with patch("main.calculate_stoch",
                       return_value=_MOCK_STOCH) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", window=14, smooth_k=3, smooth_d=3,
                    interval="1d", count=1)

    def test_default_window_ema(self):
        """Verify EMA defaults to window=20 when not provided."""
        with patch("builtins.input", return_value="TSLA EMA"):
            with patch("main.calculate_ema", return_value=_MOCK_SERIES) as mock_ema:
                main.main()
                mock_ema.assert_called_once_with(
                    "TSLA", 20, interval="1d", count=1)

    def test_default_window_rsi(self):
        """Verify RSI defaults to window=14 when not provided."""
        with patch("builtins.input", return_value="MSFT RSI"):
            with patch("main.calculate_rsi", return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with(
                    "MSFT", 14, interval="1d", count=1)

    def test_valid_macd_dispatch(self):
        """Verify main() calls calculate_macd for MACD input
        with explicit parameters."""
        with patch("builtins.input",
                   return_value="AAPL MACD 12,26,9"):
            with patch("main.calculate_macd",
                       return_value=_MOCK_MACD) as mock_macd:
                main.main()
                mock_macd.assert_called_once_with(
                    "AAPL", fast=12, slow=26, signal=9,
                    interval="1d", count=1)

    def test_default_window_macd(self):
        """Verify MACD defaults to (12,26,9) when not
        provided."""
        with patch("builtins.input",
                   return_value="AAPL MACD"):
            with patch("main.calculate_macd",
                       return_value=_MOCK_MACD) as mock_macd:
                main.main()
                mock_macd.assert_called_once_with(
                    "AAPL", fast=12, slow=26, signal=9,
                    interval="1d", count=1)

    def test_valid_bb_dispatch(self):
        """Verify main() calls calculate_bb for a BB input
        with explicit parameters."""
        with patch("builtins.input",
                   return_value="AAPL BB 20,2.5"):
            with patch("main.calculate_bb",
                       return_value=_MOCK_BB) as mock_bb:
                main.main()
                mock_bb.assert_called_once_with(
                    "AAPL", window=20, num_std=2.5,
                    interval="1d", count=1)

    def test_valid_vwap_dispatch(self):
        """Verify main() calls calculate_vwap for a VWAP input
        with explicit window."""
        with patch("builtins.input",
                   return_value="AAPL VWAP 20"):
            with patch("main.calculate_vwap",
                       return_value=_MOCK_SERIES_VWAP) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    def test_default_window_vwap(self):
        """Verify VWAP defaults to window=20 when not
        provided."""
        with patch("builtins.input",
                   return_value="AAPL VWAP"):
            with patch("main.calculate_vwap",
                       return_value=_MOCK_SERIES_VWAP) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    def test_valid_av_dispatch(self):
        """Verify main() calls calculate_av for an AV input
        with explicit window."""
        with patch("builtins.input",
                   return_value="AAPL AV 20"):
            with patch("main.calculate_av",
                       return_value=_MOCK_SERIES_AV) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    def test_default_window_av(self):
        """Verify AV defaults to window=20 when not
        provided."""
        with patch("builtins.input",
                   return_value="AAPL AV"):
            with patch("main.calculate_av",
                       return_value=_MOCK_SERIES_AV) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=1)

    def test_valid_rvol_dispatch(self):
        """Verify main() calls calculate_rvol for an RVOL input
        with explicit window."""
        with patch("builtins.input",
                   return_value="AAPL RVOL 10"):
            with patch("main.calculate_rvol",
                       return_value=_MOCK_SERIES_RVOL) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 10, interval="1d", count=1)

    def test_default_window_rvol(self):
        """Verify RVOL defaults to window=10 when not
        provided."""
        with patch("builtins.input",
                   return_value="AAPL RVOL"):
            with patch("main.calculate_rvol",
                       return_value=_MOCK_SERIES_RVOL) as mock_fn:
                main.main()
                mock_fn.assert_called_once_with(
                    "AAPL", 10, interval="1d", count=1)

    def test_default_window_bb(self):
        """Verify BB defaults to (20, 2.0) when not
        provided."""
        with patch("builtins.input",
                   return_value="AAPL BB"):
            with patch("main.calculate_bb",
                       return_value=_MOCK_BB) as mock_bb:
                main.main()
                mock_bb.assert_called_once_with(
                    "AAPL", window=20, num_std=2.0,
                    interval="1d", count=1)

    # ---- C<count> syntax ----

    def test_count_with_defaults(self):
        """Verify C<count> sets count without overriding window."""
        with patch("builtins.input", return_value="AAPL SMA C10"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 50, interval="1d", count=10)

    def test_count_with_window_and_interval(self):
        """Verify C<count> works alongside window and interval."""
        with patch("builtins.input", return_value="AAPL SMA 20 C5 1wk"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 20, interval="1wk", count=5)

    def test_count_before_window(self):
        """Verify C<count> can appear before the window."""
        with patch("builtins.input", return_value="AAPL SMA C5 20"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 20, interval="1d", count=5)

    def test_lowercase_count(self):
        """Verify lowercase c<count> is recognised."""
        with patch("builtins.input", return_value="AAPL RSI c3"):
            with patch("main.calculate_rsi", return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with(
                    "AAPL", 14, interval="1d", count=3)

    # ---- case insensitivity ----

    def test_case_insensitive(self):
        """Verify indicator matching is case-insensitive."""
        with patch("builtins.input", return_value="aapl rsi 14"):
            with patch("main.calculate_rsi", return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with(
                    "aapl", 14, interval="1d", count=1)

    # ---- positional flexibility ----

    def test_valid_sma_with_interval(self):
        """Verify main() passes an explicit bar interval to SMA."""
        with patch("builtins.input", return_value="AAPL SMA 20 1wk"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 20, interval="1wk", count=1)

    def test_valid_ema_with_interval(self):
        """Verify main() passes an explicit bar interval to EMA."""
        with patch("builtins.input", return_value="TSLA EMA 15 1mo"):
            with patch("main.calculate_ema", return_value=_MOCK_SERIES) as mock_ema:
                main.main()
                mock_ema.assert_called_once_with(
                    "TSLA", 15, interval="1mo", count=1)

    def test_valid_rsi_with_interval(self):
        """Verify main() passes an explicit bar interval to RSI."""
        with patch("builtins.input", return_value="MSFT RSI 14 1mo"):
            with patch("main.calculate_rsi", return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with(
                    "MSFT", 14, interval="1mo", count=1)

    def test_valid_sma_with_monthly_interval(self):
        """Verify main() works with a monthly bar interval."""
        with patch("builtins.input", return_value="GOOG SMA 10 1mo"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "GOOG", 10, interval="1mo", count=1)

    def test_interval_before_window(self):
        """Verify interval and window are recognised regardless of
        order."""
        with patch("builtins.input", return_value="AAPL SMA 1wk 20"):
            with patch("main.calculate_sma", return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                mock_sma.assert_called_once_with(
                    "AAPL", 20, interval="1wk", count=1)

    # ---- error paths ----

    def test_too_few_args(self):
        """Verify main() exits when fewer than 2 arguments are given."""
        with patch("builtins.input", return_value="AAPL"):
            with pytest.raises(SystemExit):
                main.main()

    def test_unrecognised_arg(self):
        """Verify main() exits when an unrecognised argument is given."""
        with patch("builtins.input", return_value="AAPL SMA 20 extra"):
            with pytest.raises(SystemExit):
                main.main()

    def test_invalid_indicator(self):
        """Verify main() exits when an unrecognised indicator
        is given."""
        with patch("builtins.input", return_value="AAPL XYZ 20"):
            with pytest.raises(SystemExit):
                main.main()

    def test_non_integer_window(self):
        """Verify main() exits when window is not an integer."""
        with patch("builtins.input", return_value="AAPL SMA abc"):
            with pytest.raises(SystemExit):
                main.main()

    def test_count_non_numeric(self):
        """Verify main() exits when C<count> has no digits."""
        with patch("builtins.input", return_value="AAPL SMA C"):
            with pytest.raises(SystemExit):
                main.main()

    def test_macd_requires_comma_separated(self):
        """Verify main() exits when MACD gets a plain integer
        instead of comma-separated params."""
        with patch("builtins.input", return_value="AAPL MACD 20"):
            with pytest.raises(SystemExit):
                main.main()

    @pytest.mark.parametrize("params", ["26,12,9", "12,12,9"])
    def test_macd_fast_not_less_than_slow(self, params):
        """Verify main() exits when fast >= slow for MACD."""
        with patch("builtins.input",
                   return_value=f"AAPL MACD {params}"):
            with pytest.raises(SystemExit):
                main.main()

    def test_negative_window(self):
        """Verify main() exits when window is negative."""
        with patch("builtins.input", return_value="AAPL RSI -5"):
            with pytest.raises(SystemExit):
                main.main()

    def test_zero_window(self):
        """Verify main() exits when window is zero."""
        with patch("builtins.input", return_value="AAPL SMA 0"):
            with pytest.raises(SystemExit):
                main.main()

    def test_negative_count(self):
        """Verify main() exits when count is negative."""
        with patch("builtins.input", return_value="AAPL SMA C-5"):
            with pytest.raises(SystemExit):
                main.main()

    def test_zero_count(self):
        """Verify main() exits when count is zero."""
        with patch("builtins.input", return_value="AAPL SMA C0"):
            with pytest.raises(SystemExit):
                main.main()

    def test_duplicate_window(self):
        """Verify main() exits when two windows are provided."""
        with patch("builtins.input", return_value="AAPL SMA 20 30"):
            with pytest.raises(SystemExit):
                main.main()

    def test_duplicate_count(self):
        """Verify main() exits when two counts are provided."""
        with patch("builtins.input", return_value="AAPL SMA C5 C10"):
            with pytest.raises(SystemExit):
                main.main()

    def test_duplicate_interval(self):
        """Verify main() exits when two intervals are provided."""
        with patch("builtins.input", return_value="AAPL SMA 1wk 1mo"):
            with pytest.raises(SystemExit):
                main.main()

    # ---- multi-ticker ----

    def test_two_tickers_sma(self):
        """Verify main() dispatches to SMA for each of two tickers."""
        with patch("builtins.input", return_value="AAPL,MSFT SMA 20"):
            with patch("main.calculate_sma",
                       return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                assert mock_sma.call_count == 2
                mock_sma.assert_any_call(
                    "AAPL", 20, interval="1d", count=1)
                mock_sma.assert_any_call(
                    "MSFT", 20, interval="1d", count=1)

    def test_three_tickers_ema(self):
        """Verify main() dispatches to EMA for three tickers."""
        with patch("builtins.input",
                   return_value="AAPL,GOOG,TSLA EMA"):
            with patch("main.calculate_ema",
                       return_value=_MOCK_SERIES) as mock_ema:
                main.main()
                assert mock_ema.call_count == 3

    def test_two_tickers_rsi(self):
        """Verify main() dispatches to RSI for two tickers."""
        with patch("builtins.input", return_value="AAPL,MSFT RSI 14"):
            with patch("main.calculate_rsi",
                       return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                assert mock_rsi.call_count == 2

    def test_spaced_commas(self):
        """Verify whitespace around commas is normalised."""
        with patch("builtins.input",
                   return_value="AAPL , MSFT SMA 20"):
            with patch("main.calculate_sma",
                       return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                assert mock_sma.call_count == 2

    def test_double_comma(self):
        """Verify an empty ticker between two commas is filtered."""
        with patch("builtins.input",
                   return_value="AAPL,,MSFT SMA 20"):
            with patch("main.calculate_sma",
                       return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                assert mock_sma.call_count == 2

    def test_multi_ticker_with_count(self):
        """Verify count is passed to each ticker dispatch."""
        with patch("builtins.input", return_value="AAPL,MSFT SMA C3"):
            with patch("main.calculate_sma",
                       return_value=_MOCK_SERIES) as mock_sma:
                main.main()
                assert mock_sma.call_count == 2
                mock_sma.assert_any_call(
                    "AAPL", 50, interval="1d", count=3)
                mock_sma.assert_any_call(
                    "MSFT", 50, interval="1d", count=3)

    def test_multi_ticker_with_interval(self):
        """Verify interval is passed to each ticker dispatch."""
        with patch("builtins.input",
                   return_value="AAPL,MSFT EMA 1wk"):
            with patch("main.calculate_ema",
                       return_value=_MOCK_SERIES) as mock_ema:
                main.main()
                assert mock_ema.call_count == 2
                mock_ema.assert_any_call(
                    "AAPL", 20, interval="1wk", count=1)
                mock_ema.assert_any_call(
                    "MSFT", 20, interval="1wk", count=1)

    def test_multi_ticker_all_args(self):
        """Verify window, interval, and count with two tickers."""
        with patch("builtins.input",
                   return_value="AAPL,MSFT RSI 30 1mo C5"):
            with patch("main.calculate_rsi",
                       return_value=_MOCK_SERIES) as mock_rsi:
                main.main()
                assert mock_rsi.call_count == 2
                mock_rsi.assert_any_call(
                    "AAPL", 30, interval="1mo", count=5)
                mock_rsi.assert_any_call(
                    "MSFT", 30, interval="1mo", count=5)

    def test_multi_ticker_print_single(self, capsys):
        """Verify output for two tickers with count=1."""
        with patch("builtins.input",
                   return_value="AAPL,MSFT SMA 50"):
            with patch("main.calculate_sma",
                       return_value=_MOCK_SERIES):
                main.main()
        captured = capsys.readouterr()
        expected = "AAPL 50-SMA: 42.00\nMSFT 50-SMA: 42.00\n"
        assert captured.out == expected

    def test_multi_ticker_print_multiple(self, capsys):
        """Verify output for two tickers with count>1."""
        data = pd.Series([45.23, 44.10])
        with patch("builtins.input",
                   return_value="AAPL,MSFT RSI C2"):
            with patch("main.calculate_rsi",
                       return_value=data):
                main.main()
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        assert lines[0] == "AAPL 14-RSI (last 2):"
        assert lines[1] == "  45.23"
        assert lines[2] == "  44.10"
        assert lines[3] == "MSFT 14-RSI (last 2):"
        assert lines[4] == "  45.23"
        assert lines[5] == "  44.10"

    def test_multi_ticker_error_isolation(self):
        """Verify a calculation failure for one ticker doesn't
        prevent subsequent tickers from being processed."""
        side_effects = [Exception("Network error"),
                        _MOCK_SERIES]
        with patch("builtins.input",
                   return_value="AAPL,MSFT SMA 20"):
            with patch("main.calculate_sma",
                       side_effect=side_effects) as mock_sma:
                main.main()
                assert mock_sma.call_count == 2
