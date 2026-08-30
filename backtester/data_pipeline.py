# backtester/data_pipeline.py
"""Batch data download with parquet caching.

Downloads OHLCV data for multiple tickers via yf.download(),
caches results as parquet files, and loads from cache when
available.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).parent / "cache"


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

        Args:
            tickers: List of stock symbols.
            interval: Bar size.
            years: Years of history.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """
        from datetime import datetime, timedelta

        end = datetime.now()
        start = end - timedelta(days=years * 365)

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
            return {}

        if raw.empty:
            print("Error: no data returned from yfinance")
            return {}

        result: dict[str, pd.DataFrame] = {}

        if len(tickers) == 1:
            df = raw.copy()
            df = df.dropna(how="all")
            if not df.empty:
                result[tickers[0]] = df
                print(f"  Downloaded {len(df)} rows for "
                      f"{tickers[0]}")
        else:
            for ticker in tickers:
                try:
                    df = raw[ticker].copy()
                except KeyError:
                    print(f"  Warning: no data for {ticker}")
                    continue
                df = df.dropna(how="all")
                if not df.empty:
                    result[ticker] = df
                    print(f"  Downloaded {len(df)} rows for "
                          f"{ticker}")

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
        """Save a single ticker to parquet cache."""
        path = self._cache_path(ticker, interval)
        try:
            data.to_parquet(path)
        except Exception as exc:
            print(f"  Warning: failed to cache {ticker}: {exc}")

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
