# conftest.py
# Shared pytest fixtures for mock tests (fake yfinance Ticker objects)

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


@pytest.fixture
def mock_stock_data():
    """Factory fixture: patches main.yf.Ticker with fake Close prices.

    Usage in tests::

        def test_something(self, mock_stock_data):
            mock_stock_data([10, 11, 12, 13, 14])
            # ... call functions that use main.yf.Ticker ...
    """
    patchers = []

    def _make(close_prices, high_prices=None, low_prices=None,
              volume_prices=None):
        data = {"Close": close_prices}
        if high_prices is not None:
            data["High"] = high_prices
        if low_prices is not None:
            data["Low"] = low_prices
        if volume_prices is not None:
            data["Volume"] = volume_prices
        df = pd.DataFrame(data)
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = df
        p = patch("main.yf.Ticker", return_value=mock_ticker)
        p.start()
        patchers.append(p)
        return mock_ticker

    yield _make

    for p in patchers:
        p.stop()
