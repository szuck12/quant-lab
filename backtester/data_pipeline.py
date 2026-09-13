# backtester/data_pipeline.py
"""Batch data download with parquet caching.

Downloads OHLCV data for multiple tickers via yf.download(),
caches results as parquet files, and loads from cache when
available.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).parent / "cache"
CHUNK_SIZE = 200  # yf.download handles larger batches efficiently

# In-memory cache: key = f"{ticker}_{interval}_{years}" -> DataFrame
_memory_cache: dict[str, pd.DataFrame] = {}


class DataPipeline:
    """Batch data download with parquet caching."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(
        self,
        tickers: list[str],
        interval: str,
        years: float,
        on_progress: Callable[[int], None] | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Download data for all tickers at a given interval.

        Checks cache first. Downloads missing tickers via
        yf.download() and saves to parquet.

        Args:
            tickers: List of stock symbols.
            interval: Bar size ("1d", "1wk", "1mo", etc.).
            years: Years of historical data (supports decimals).
            on_progress: Optional callback receiving 0–100 within
                the download phase (cache checks + batch download).

        Returns:
            Dict mapping ticker -> OHLCV DataFrame indexed by date.
        """
        result: dict[str, pd.DataFrame] = {}
        to_download: list[str] = []
        total = len(tickers)

        for i, ticker in enumerate(tickers):
            cache_key = f"{ticker}_{interval}_{years}"
            # Check in-memory cache first
            if cache_key in _memory_cache:
                result[ticker] = _memory_cache[cache_key]
                continue
            cached = self._load_cache(ticker, interval, years)
            if cached is not None and len(cached) > 0:
                _memory_cache[cache_key] = cached
                result[ticker] = cached
            else:
                to_download.append(ticker)
            # Report cache-check progress (0–5% of download phase)
            if on_progress and total > 0:
                on_progress(int(5 * (i + 1) / total))

        if to_download:
            # Download phase: 5%–100% of download phase
            downloaded = self._download_batch(
                to_download, interval, years,
                on_progress=on_progress,
                progress_offset=5,
                progress_range=95,
            )
            for ticker, df in downloaded.items():
                self._save_cache(ticker, interval, years, df)
                cache_key = f"{ticker}_{interval}_{years}"
                _memory_cache[cache_key] = df
                result[ticker] = df
        elif on_progress:
            on_progress(100)

        return result

    def _download_batch(
        self,
        tickers: list[str],
        interval: str,
        years: float,
        on_progress: Callable[[int], None] | None = None,
        progress_offset: int = 0,
        progress_range: int = 100,
    ) -> dict[str, pd.DataFrame]:
        """Use yf.download() for batch download.

        For large ticker lists (>CHUNK_SIZE), downloads in parallel
        chunks to avoid API timeouts and memory issues.

        Args:
            tickers: List of stock symbols.
            interval: Bar size.
            years: Years of history.
            on_progress: Optional callback receiving progress.
            progress_offset: Starting percentage for this phase.
            progress_range: Percentage range for this phase.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from datetime import timedelta

        end = datetime.now()
        start = end - timedelta(days=years * 365)

        def _report(pct: int) -> None:
            if on_progress:
                on_progress(progress_offset + int(progress_range * pct / 100))

        if len(tickers) <= CHUNK_SIZE:
            result = self._download_chunk(
                tickers, start, end, interval
            )
            _report(100)
            return result

        # Parallel chunk download
        chunks = [
            tickers[i : i + CHUNK_SIZE]
            for i in range(0, len(tickers), CHUNK_SIZE)
        ]
        result: dict[str, pd.DataFrame] = {}
        total = len(tickers)
        completed_chunks = 0

        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {
                pool.submit(
                    self._download_chunk, c, start, end, interval
                ): c
                for c in chunks
            }
            for future in as_completed(futures):
                chunk_idx = chunks.index(futures[future])
                start_idx = chunk_idx * CHUNK_SIZE + 1
                end_idx = min(
                    (chunk_idx + 1) * CHUNK_SIZE, total
                )
                result.update(future.result())
                completed_chunks += 1
                _report(int(100 * completed_chunks / len(chunks)))

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
            _yf_logger.setLevel(_prev_level)
            return {}
        finally:
            _yf_logger.setLevel(_prev_level)

        if raw.empty:
            return {}

        result: dict[str, pd.DataFrame] = {}
        failed_tickers: list[str] = []

        if len(tickers) == 1:
            df = raw.copy()
            df = df.dropna(how="all")
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel("Ticker")
            if not df.empty:
                result[tickers[0]] = df
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
                else:
                    failed_tickers.append(ticker)

        return result

    def _cache_path(self, ticker: str, interval: str, years: float) -> Path:
        """Return parquet file path for a ticker+interval+years."""
        return self.cache_dir / f"{ticker}_{interval}_{years}.parquet"

    def _load_cache(
        self, ticker: str, interval: str, years: float
    ) -> pd.DataFrame | None:
        """Load a single ticker from parquet cache.

        Returns None if cache file does not exist.
        """
        path = self._cache_path(ticker, interval, years)
        if not path.exists():
            return None
        try:
            return pd.read_parquet(path)
        except Exception:
            return None

    def _save_cache(
        self, ticker: str, interval: str, years: float, data: pd.DataFrame
    ) -> None:
        """Save a single ticker to parquet cache.

        Silently skips if pyarrow/fastparquet is not installed.
        """
        path = self._cache_path(ticker, interval, years)
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
