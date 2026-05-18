import pytest
from unittest.mock import patch
import main


class TestMain:
    """Tests for main() with real indicator calculations."""

    def test_sma_dispatch(self):
        with patch("builtins.input", return_value="AAPL SMA 30"):
            main.main()

    def test_ema_dispatch(self):
        with patch("builtins.input", return_value="TSLA EMA 15"):
            main.main()

    def test_rsi_dispatch(self):
        with patch("builtins.input", return_value="MSFT RSI 14"):
            main.main()

    def test_with_weekly_interval(self):
        with patch("builtins.input", return_value="GOOG SMA 10 1wk"):
            main.main()
