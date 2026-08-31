# backtester/data_pipeline.py
"""Batch data download with parquet caching.

Downloads OHLCV data for multiple tickers via yf.download(),
caches results as parquet files, and loads from cache when
available.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).parent / "cache"
CHUNK_SIZE = 50  # yf.download works best in batches of ~50


class DataPipeline:
    """Batch data download with parquet caching."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(
        self,
        tickers: list[str],
        interval: str,
        years: int,
    ) -> dict[str, pd.DataFrame]:
        """Download data for all tickers at a given interval.

        Checks cache first. Downloads missing tickers via
        yf.download() and saves to parquet.

        Args:
            tickers: List of stock symbols.
            interval: Bar size ("1d", "1wk", "1mo", etc.).
            years: Years of historical data.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame indexed by date.
        """
        result: dict[str, pd.DataFrame] = {}
        to_download: list[str] = []

        for ticker in tickers:
            cached = self._load_cache(ticker, interval)
            if cached is not None and len(cached) > 0:
                result[ticker] = cached
            else:
                to_download.append(ticker)

        if to_download:
            downloaded = self._download_batch(to_download, interval, years)
            for ticker, df in downloaded.items():
                self._save_cache(ticker, interval, df)
                result[ticker] = df

        return result

    def _download_batch(
        self,
        tickers: list[str],
        interval: str,
        years: int,
    ) -> dict[str, pd.DataFrame]:
        """Use yf.download() for batch download.

        For large ticker lists (>CHUNK_SIZE), downloads in chunks
        to avoid API timeouts and memory issues.

        Args:
            tickers: List of stock symbols.
            interval: Bar size.
            years: Years of history.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """
        from datetime import timedelta

        end = datetime.now()
        start = end - timedelta(days=years * 365)

        if len(tickers) <= CHUNK_SIZE:
            return self._download_chunk(
                tickers, start, end, interval
            )

        # Chunked download with progress
        result: dict[str, pd.DataFrame] = {}
        total = len(tickers)
        for i in range(0, total, CHUNK_SIZE):
            chunk = tickers[i : i + CHUNK_SIZE]
            n = min(i + CHUNK_SIZE, total)
            print(f"  Downloading {i + 1}-{n} of {total}...")
            chunk_result = self._download_chunk(
                chunk, start, end, interval
            )
            result.update(chunk_result)
        return result

    def _download_chunk(
        self,
        tickers: list[str],
        start: "datetime",
        end: "datetime",
        interval: str,
    ) -> dict[str, pd.DataFrame]:
        """Download a single chunk of tickers.

        Args:
            tickers: List of stock symbols (small batch).
            start: Start date.
            end: End date.
            interval: Bar size.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """
        import logging as _log

        # Suppress noisy yfinance warnings (e.g. "1 Failed download")
        _yf_logger = _log.getLogger("yfinance")
        _prev_level = _yf_logger.level
        _yf_logger.setLevel(_log.ERROR)

        try:
            raw = yf.download(
                tickers=tickers,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                interval=interval,
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
        except Exception as exc:
            print(f"Error: batch download failed: {exc}")
            _yf_logger.setLevel(_prev_level)
            return {}
        finally:
            _yf_logger.setLevel(_prev_level)

        if raw.empty:
            failed = ", ".join(tickers[:5])
            if len(tickers) > 5:
                failed += f" ... ({len(tickers)} total)"
            print(f"  Warning: no data returned for {failed}")
            return {}

        result: dict[str, pd.DataFrame] = {}
        failed_tickers: list[str] = []

        if len(tickers) == 1:
            df = raw.copy()
            df = df.dropna(how="all")
            # yf.download returns MultiIndex columns even for a single
            # ticker: ('AAPL', 'Close'). Flatten to just 'Close'.
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel("Ticker")
            if not df.empty:
                result[tickers[0]] = df
                print(f"  Downloaded {len(df)} rows for "
                      f"{tickers[0]}")
            else:
                failed_tickers.append(tickers[0])
        else:
            for ticker in tickers:
                try:
                    df = raw[ticker].copy()
                except KeyError:
                    failed_tickers.append(ticker)
                    continue
                df = df.dropna(how="all")
                if not df.empty:
                    result[ticker] = df
                    print(f"  Downloaded {len(df)} rows for "
                          f"{ticker}")
                else:
                    failed_tickers.append(ticker)

        return result

    def _cache_path(self, ticker: str, interval: str) -> Path:
        """Return parquet file path for a ticker+interval."""
        return self.cache_dir / f"{ticker}_{interval}.parquet"

    def _load_cache(self, ticker: str, interval: str) -> pd.DataFrame | None:
        """Load a single ticker from parquet cache.

        Returns None if cache file does not exist.
        """
        path = self._cache_path(ticker, interval)
        if not path.exists():
            return None
        try:
            return pd.read_parquet(path)
        except Exception:
            return None

    def _save_cache(
        self, ticker: str, interval: str, data: pd.DataFrame
    ) -> None:
        """Save a single ticker to parquet cache.

        Silently skips if pyarrow/fastparquet is not installed.
        """
        path = self._cache_path(ticker, interval)
        try:
            data.to_parquet(path)
        except Exception:
            pass  # No parquet engine — caching is optional

    def clear_cache(self) -> int:
        """Remove all cached parquet files.

        Returns:
            Number of files removed.
        """
        count = 0
        for path in self.cache_dir.glob("*.parquet"):
            path.unlink()
            count += 1
        return count
