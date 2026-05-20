# test_main.py
# Tests for the main() entry point dispatch logic

import pytest
from unittest.mock import patch
import pandas as pd
import main


_MOCK_SERIES = pd.Series([42.0])


class TestMain:
    """Tests for main()."""

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
        """Verify main() exits when an unrecognised indicator is given."""
        with patch("builtins.input", return_value="AAPL MACD 20"):
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
