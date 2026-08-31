"""Tests for the backtester universe module.

All Wikipedia and file I/O is mocked — no network or filesystem
access in these tests.
"""

from __future__ import annotations

import csv
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from backtester.universe import (
    _detect_ticker_column,
    _is_cache_fresh,
    _read_cache,
    _scrape_sp500,
    _write_cache,
    get_sp500_tickers,
    load_csv_tickers,
    resolve_universe,
)


# ---------------------------------------------------------------------------
# resolve_universe
# ---------------------------------------------------------------------------


class TestResolveUniverse:
    """Tests for the top-level resolve_universe dispatcher."""

    @patch("backtester.universe.get_sp500_tickers")
    def test_resolve_sp500(self, mock_sp500):
        mock_sp500.return_value = ["AAPL", "MSFT"]
        result = resolve_universe("sp500")
        assert result == ["AAPL", "MSFT"]
        mock_sp500.assert_called_once()

    @patch("backtester.universe.get_sp500_tickers")
    def test_resolve_sp500_case_insensitive(self, mock_sp500):
        mock_sp500.return_value = ["AAPL"]
        result = resolve_universe("SP500")
        assert result == ["AAPL"]

    def test_resolve_csv_file(self, tmp_path):
        csv_file = tmp_path / "tickers.csv"
        csv_file.write_text("Symbol\nAAPL\nMSFT\n")
        result = resolve_universe(str(csv_file))
        assert result == ["AAPL", "MSFT"]

    def test_resolve_unknown_source(self):
        with pytest.raises(ValueError, match="not found"):
            resolve_universe("nonexistent.csv")


# ---------------------------------------------------------------------------
# get_sp500_tickers
# ---------------------------------------------------------------------------


class TestGetSP500Tickers:
    """Tests for S&P 500 ticker fetching."""

    @patch("backtester.universe._scrape_sp500")
    @patch("backtester.universe._is_cache_fresh", return_value=True)
    @patch("backtester.universe._read_cache")
    def test_cache_hit(
        self, mock_read, mock_fresh, mock_scrape, tmp_path
    ):
        mock_read.return_value = ["AAPL", "MSFT", "GOOG"]
        cache = tmp_path / "sp500.csv"
        cache.write_text("AAPL\n")  # file must exist
        with patch(
            "backtester.universe._cache_path",
            return_value=cache,
        ):
            result = get_sp500_tickers()
        assert result == ["AAPL", "MSFT", "GOOG"]
        mock_scrape.assert_not_called()

    @patch("backtester.universe._write_cache")
    @patch("backtester.universe._scrape_sp500")
    @patch("backtester.universe._is_cache_fresh", return_value=False)
    @patch("backtester.universe._read_cache")
    def test_cache_miss_scrapes(
        self, mock_read, mock_fresh, mock_scrape,
        mock_write, tmp_path
    ):
        mock_scrape.return_value = ["AAPL", "MSFT"]
        cache = tmp_path / "sp500.csv"
        cache.touch()
        with patch(
            "backtester.universe._cache_path",
            return_value=cache,
        ):
            result = get_sp500_tickers()
        assert result == ["AAPL", "MSFT"]
        mock_scrape.assert_called_once()
        mock_write.assert_called_once_with(cache, ["AAPL", "MSFT"])

    @patch("backtester.universe._write_cache")
    @patch("backtester.universe._scrape_sp500")
    @patch("backtester.universe._read_cache")
    def test_no_cache_file_scrapes(
        self, mock_read, mock_scrape, mock_write, tmp_path
    ):
        mock_scrape.return_value = ["AAPL"]
        cache = tmp_path / "sp500.csv"
        with patch(
            "backtester.universe._cache_path",
            return_value=cache,
        ):
            result = get_sp500_tickers()
        assert result == ["AAPL"]
        mock_scrape.assert_called_once()


# ---------------------------------------------------------------------------
# load_csv_tickers
# ---------------------------------------------------------------------------


class TestLoadCSVTickers:
    """Tests for CSV ticker loading."""

    def test_symbol_column(self, tmp_path):
        csv_file = tmp_path / "tickers.csv"
        csv_file.write_text("Symbol\nAAPL\nMSFT\nGOOG\n")
        result = load_csv_tickers(str(csv_file))
        assert result == ["AAPL", "MSFT", "GOOG"]

    def test_ticker_column(self, tmp_path):
        csv_file = tmp_path / "tickers.csv"
        csv_file.write_text("Ticker\nAAPL\nMSFT\n")
        result = load_csv_tickers(str(csv_file))
        assert result == ["AAPL", "MSFT"]

    def test_first_column_fallback(self, tmp_path):
        csv_file = tmp_path / "tickers.csv"
        csv_file.write_text("MyStocks\nAAPL\nMSFT\n")
        result = load_csv_tickers(str(csv_file))
        assert result == ["AAPL", "MSFT"]

    def test_uppercased_automatically(self, tmp_path):
        csv_file = tmp_path / "tickers.csv"
        csv_file.write_text("Symbol\naapl\nmsft\n")
        result = load_csv_tickers(str(csv_file))
        assert result == ["AAPL", "MSFT"]

    def test_empty_csv_raises(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")
        with pytest.raises((ValueError, Exception)):
            load_csv_tickers(str(csv_file))

    def test_dot_to_dash_not_applied(self, tmp_path):
        """CSV tickers are returned as-is (dots preserved for CSV)."""
        csv_file = tmp_path / "tickers.csv"
        csv_file.write_text("Symbol\nBRK.B\nBF-B\n")
        result = load_csv_tickers(str(csv_file))
        assert "BRK.B" in result
        assert "BF-B" in result


# ---------------------------------------------------------------------------
# _detect_ticker_column
# ---------------------------------------------------------------------------


class TestDetectTickerColumn:
    """Tests for automatic ticker column detection."""

    def test_symbol_column(self):
        df = pd.DataFrame({"Symbol": ["AAPL"], "Name": ["Apple"]})
        assert _detect_ticker_column(df) == "Symbol"

    def test_ticker_column(self):
        df = pd.DataFrame({"ticker": ["AAPL"]})
        assert _detect_ticker_column(df) == "ticker"

    def test_no_match_returns_none(self):
        df = pd.DataFrame({"Company": ["Apple"], "Price": [150]})
        assert _detect_ticker_column(df) is None


# ---------------------------------------------------------------------------
# _is_cache_fresh
# ---------------------------------------------------------------------------


class TestIsCacheFresh:
    """Tests for cache freshness check."""

    def test_fresh_cache(self, tmp_path):
        cache = tmp_path / "sp500.csv"
        cache.write_text("AAPL\n")
        assert _is_cache_fresh(cache, max_age_hours=24) is True

    def test_stale_cache(self, tmp_path):
        cache = tmp_path / "sp500.csv"
        cache.write_text("AAPL\n")
        # Set mtime to 25 hours ago
        stale_time = (
            datetime.now() - timedelta(hours=25)
        ).timestamp()
        import os
        os.utime(cache, (stale_time, stale_time))
        assert _is_cache_fresh(cache, max_age_hours=24) is False


# ---------------------------------------------------------------------------
# _read_cache / _write_cache
# ---------------------------------------------------------------------------


class TestCacheRoundTrip:
    """Tests for cache read/write round trip."""

    def test_write_then_read(self, tmp_path):
        cache = tmp_path / "sp500.csv"
        tickers = ["AAPL", "MSFT", "BRK-B", "GOOG"]
        _write_cache(cache, tickers)
        result = _read_cache(cache)
        assert result == tickers

    def test_read_empty_file(self, tmp_path):
        cache = tmp_path / "sp500.csv"
        cache.write_text("")
        result = _read_cache(cache)
        assert result == []


# ---------------------------------------------------------------------------
# _scrape_sp500 fallback
# ---------------------------------------------------------------------------


class TestScrapeFallback:
    """Tests for fallback when Wikipedia scraping fails."""

    @patch("backtester.universe.urllib.request.urlopen")
    def test_403_error_uses_fallback(self, mock_urlopen):
        """HTTP 403 from Wikipedia → fallback list."""
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            url="https://en.wikipedia.org/wiki/...",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=None,
        )
        tickers = _scrape_sp500()
        # Fallback should return ~500 tickers
        assert len(tickers) > 400
        assert "AAPL" in tickers
        assert "MSFT" in tickers
        # Dots converted to dashes
        assert "BRK-B" in tickers

    @patch("backtester.universe.urllib.request.urlopen")
    def test_network_error_uses_fallback(self, mock_urlopen):
        """Network timeout → fallback list."""
        mock_urlopen.side_effect = TimeoutError("timed out")
        tickers = _scrape_sp500()
        assert len(tickers) > 400
        assert "AAPL" in tickers

    @patch("backtester.universe.pd.read_html")
    @patch("backtester.universe.urllib.request.urlopen")
    def test_user_agent_header_sent(
        self, mock_urlopen, mock_read_html
    ):
        """Request includes a browser-like User-Agent header."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<html></html>"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        # Make pd.read_html raise so fallback is used
        mock_read_html.side_effect = Exception("parse error")

        _scrape_sp500()

        # Verify the request had a User-Agent header
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        # urllib normalizes header name to "User-agent"
        assert "User-agent" in req.headers
        assert "Mozilla" in req.headers["User-agent"]

    @patch("backtester.universe.urllib.request.urlopen")
    def test_dot_to_dash_conversion(self, mock_urlopen):
        """BRK.B from Wikipedia becomes BRK-B."""
        import io

        html = """
        <table><tr><th>Symbol</th></tr>
        <tr><td>BRK.B</td></tr>
        <tr><td>BGNE</td></tr>
        </table>
        """
        mock_resp = MagicMock()
        mock_resp.read.return_value = html.encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        tickers = _scrape_sp500()
        assert "BRK-B" in tickers
        assert "BGNE" in tickers

    def test_fallback_list_contains_common_tickers(self):
        """Fallback list includes major S&P 500 tickers."""
        from backtester.universe import _FALLBACK_SP500

        for ticker in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]:
            assert ticker in _FALLBACK_SP500
