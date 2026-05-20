# test_get_stock_data.py
# Integration tests for get_stock_data() with real yfinance data

import pytest
from main import get_stock_data


class TestGetStockData:
    """Tests for get_stock_data() with real yfinance calls."""

    def test_returns_ticker_object(self):
        """Verify get_stock_data returns a Ticker with history data."""
        stock = get_stock_data("AAPL", period="5d")
        assert stock is not None
        hist = stock.history(period="5d")
        assert len(hist) > 0

    def test_fetched_message(self, capsys):
        """Verify the \"Fetched...\" message includes the ticker name."""
        get_stock_data("AAPL", period="5d")
        captured = capsys.readouterr()
        assert "Fetched" in captured.out
        assert "AAPL" in captured.out

    def test_multiple_tickers(self):
        """Verify get_stock_data works for several well-known tickers."""
        for ticker in ["MSFT", "GOOG", "TSLA"]:
            stock = get_stock_data(ticker, period="5d")
            hist = stock.history(period="5d")
            assert len(hist) > 0
