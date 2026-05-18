import pytest
from unittest.mock import patch
from main import get_stock_data


class TestGetStockData:
    """Tests for get_stock_data()."""

    def test_returns_ticker_object(self, mock_stock_data):
        mock_ticker = mock_stock_data([10, 11, 12])
        result = get_stock_data("AAPL")
        assert result is mock_ticker

    def test_history_called_with_period(self, mock_stock_data):
        mock_ticker = mock_stock_data([10, 11, 12])
        with patch("builtins.print"):
            get_stock_data("AAPL", period="1mo")
        mock_ticker.history.assert_called_once_with(period="1mo", interval="1d")

    def test_fetched_message(self, mock_stock_data, capsys):
        mock_stock_data([10, 11, 12])
        get_stock_data("AAPL")
        captured = capsys.readouterr()
        assert "Fetched 3 rows for AAPL" in captured.out

    def test_custom_period(self, mock_stock_data):
        mock_ticker = mock_stock_data([10, 11, 12, 13, 14])
        with patch("builtins.print"):
            get_stock_data("MSFT", period="1y")
        mock_ticker.history.assert_called_once_with(period="1y", interval="1d")

    def test_custom_interval(self, mock_stock_data):
        mock_ticker = mock_stock_data([10, 11, 12])
        with patch("builtins.print"):
            get_stock_data("AAPL", period="6mo", interval="1wk")
        mock_ticker.history.assert_called_once_with(period="6mo", interval="1wk")
