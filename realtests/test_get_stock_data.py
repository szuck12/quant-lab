import pytest
from main import get_stock_data


class TestGetStockData:
    """Tests for get_stock_data() with real yfinance calls."""

    def test_returns_ticker_object(self):
        stock = get_stock_data("AAPL", period="5d")
        assert stock is not None
        hist = stock.history(period="5d")
        assert len(hist) > 0

    def test_fetched_message(self, capsys):
        get_stock_data("AAPL", period="5d")
        captured = capsys.readouterr()
        assert "Fetched" in captured.out
        assert "AAPL" in captured.out

    def test_multiple_tickers(self):
        for ticker in ["MSFT", "GOOG", "TSLA"]:
            stock = get_stock_data(ticker, period="5d")
            hist = stock.history(period="5d")
            assert len(hist) > 0
