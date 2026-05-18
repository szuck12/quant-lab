import pytest
from unittest.mock import patch
import main


class TestMain:
    """Tests for main()."""

    def test_valid_sma_dispatch(self):
        with patch("builtins.input", return_value="AAPL SMA 20"):
            with patch("main.calculate_sma") as mock_sma:
                main.main()
                mock_sma.assert_called_once_with("AAPL", 20, interval="1d")

    def test_valid_ema_dispatch(self):
        with patch("builtins.input", return_value="TSLA EMA 15"):
            with patch("main.calculate_ema") as mock_ema:
                main.main()
                mock_ema.assert_called_once_with("TSLA", 15, interval="1d")

    def test_valid_rsi_dispatch(self):
        with patch("builtins.input", return_value="MSFT RSI 14"):
            with patch("main.calculate_rsi") as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with("MSFT", 14, interval="1d")

    def test_case_insensitive(self):
        with patch("builtins.input", return_value="aapl rsi 14"):
            with patch("main.calculate_rsi") as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with("aapl", 14, interval="1d")

    def test_valid_sma_with_interval(self):
        with patch("builtins.input", return_value="AAPL SMA 20 1wk"):
            with patch("main.calculate_sma") as mock_sma:
                main.main()
                mock_sma.assert_called_once_with("AAPL", 20, interval="1wk")

    def test_valid_ema_with_interval(self):
        with patch("builtins.input", return_value="TSLA EMA 15 1mo"):
            with patch("main.calculate_ema") as mock_ema:
                main.main()
                mock_ema.assert_called_once_with("TSLA", 15, interval="1mo")

    def test_valid_rsi_with_interval(self):
        with patch("builtins.input", return_value="MSFT RSI 14 1mo"):
            with patch("main.calculate_rsi") as mock_rsi:
                main.main()
                mock_rsi.assert_called_once_with("MSFT", 14, interval="1mo")

    def test_valid_sma_with_monthly_interval(self):
        with patch("builtins.input", return_value="GOOG SMA 10 1mo"):
            with patch("main.calculate_sma") as mock_sma:
                main.main()
                mock_sma.assert_called_once_with("GOOG", 10, interval="1mo")

    def test_too_few_args(self):
        with patch("builtins.input", return_value="AAPL SMA"):
            with pytest.raises(SystemExit):
                main.main()

    def test_invalid_interval(self):
        with patch("builtins.input", return_value="AAPL SMA 20 extra"):
            with pytest.raises(SystemExit):
                main.main()

    def test_invalid_indicator(self):
        with patch("builtins.input", return_value="AAPL MACD 20"):
            with pytest.raises(SystemExit):
                main.main()

    def test_non_integer_period(self):
        with patch("builtins.input", return_value="AAPL SMA abc"):
            with pytest.raises(SystemExit):
                main.main()

    def test_negative_period(self):
        with patch("builtins.input", return_value="AAPL RSI -5"):
            with pytest.raises(SystemExit):
                main.main()

    def test_zero_period(self):
        with patch("builtins.input", return_value="AAPL SMA 0"):
            with pytest.raises(SystemExit):
                main.main()
