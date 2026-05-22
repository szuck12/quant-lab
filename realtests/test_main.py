# test_main.py
# Integration tests for main() with real yfinance data

import pytest
from unittest.mock import patch
import main


class TestMain:
    """Tests for main() with real indicator calculations."""

    def test_sma_dispatch(self):
        """Verify main() dispatches to SMA with default interval."""
        with patch("builtins.input", return_value="AAPL SMA 30"):
            main.main()

    def test_ema_dispatch(self):
        """Verify main() dispatches to EMA with default interval."""
        with patch("builtins.input", return_value="TSLA EMA 15"):
            main.main()

    def test_rsi_dispatch(self):
        """Verify main() dispatches to RSI with default interval."""
        with patch("builtins.input", return_value="MSFT RSI 14"):
            main.main()

    def test_with_weekly_interval(self):
        """Verify main() works with a weekly bar interval."""
        with patch("builtins.input", return_value="GOOG SMA 10 1wk"):
            main.main()

    def test_multi_ticker_sma(self):
        """Verify main() dispatches to SMA for two tickers."""
        with patch("builtins.input",
                   return_value="AAPL,MSFT SMA 30"):
            main.main()

    def test_macd_dispatch(self):
        """Verify main() dispatches to MACD with default
        interval."""
        with patch("builtins.input",
                   return_value="AAPL MACD 12,26,9"):
            main.main()

    def test_bb_dispatch(self):
        """Verify main() dispatches to BB."""
        with patch("builtins.input",
                   return_value="AAPL BB 20,2.0"):
            main.main()

    def test_vwap_dispatch(self):
        """Verify main() dispatches to VWAP."""
        with patch("builtins.input",
                   return_value="AAPL VWAP 20"):
            main.main()

    def test_av_dispatch(self):
        """Verify main() dispatches to AV."""
        with patch("builtins.input",
                   return_value="AAPL AV 20"):
            main.main()

    def test_rvol_dispatch(self):
        """Verify main() dispatches to RVOL."""
        with patch("builtins.input",
                   return_value="AAPL RVOL 10"):
            main.main()
