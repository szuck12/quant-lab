# backtester/universe.py
"""Ticker universe resolution.

Resolves universe names (sp500) or CSV file paths to lists of
tickers for bulk strategy scanning.
"""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

CACHE_DIR = Path(__file__).parent / "cache"
SP500_CACHE_TTL_HOURS = 24


def resolve_universe(source: str) -> list[str]:
    """Resolve a universe source to a list of tickers.

    Args:
        source: "sp500" for S&P 500, or a path to a CSV file.

    Returns:
        List of ticker strings.

    Raises:
        ValueError: If source is unknown or file not found.
    """
    if source.lower() == "sp500":
        return get_sp500_tickers()

    path = Path(source)
    if not path.exists():
        raise ValueError(
            f"Universe file not found: {source}"
        )
    return load_csv_tickers(str(path))


def get_sp500_tickers() -> list[str]:
    """Fetch S&P 500 constituents from Wikipedia.

    Caches result to backtester/cache/sp500.csv.
    Re-scrapes if cache is older than 24 hours.

    Returns:
        List of ~500 ticker strings.
    """
    cache = _cache_path()
    if cache.exists() and _is_cache_fresh(cache):
        return _read_cache(cache)

    tickers = _scrape_sp500()
    _write_cache(cache, tickers)
    return tickers


def load_csv_tickers(path: str) -> list[str]:
    """Load tickers from a CSV file.

    Auto-detects ticker column by looking for headers named:
    Symbol, Ticker, symbol, ticker, sym. Falls back to first
    column if no match found.

    Args:
        path: Path to CSV file.

    Returns:
        List of ticker strings (uppercased, stripped).

    Raises:
        ValueError: If file is empty or has no parseable tickers.
    """
    try:
        df = pd.read_csv(path)
    except Exception:
        raise ValueError(f"CSV file is empty or unreadable: {path}")
    if df.empty:
        raise ValueError(f"CSV file is empty: {path}")

    # Auto-detect ticker column
    col = _detect_ticker_column(df)
    if col is None:
        # Fall back to first column
        col = df.columns[0]

    tickers = [
        str(v).strip().upper()
        for v in df[col].dropna()
        if str(v).strip()
    ]
    if not tickers:
        raise ValueError(
            f"No tickers found in column '{col}' of {path}"
        )
    return tickers


def _detect_ticker_column(df: pd.DataFrame) -> str | None:
    """Find a column whose name matches common ticker headers."""
    candidates = {
        "symbol", "ticker", "sym", "stock", "code",
        "Symbol", "Ticker", "Sym", "Stock", "Code",
    }
    for col in df.columns:
        if col.strip() in candidates:
            return col
    return None


def _scrape_sp500() -> list[str]:
    """Scrape S&P 500 tickers from Wikipedia.

    Returns:
        List of ticker strings with BRK.B → BRK-B conversion.
    """
    url = (
        "https://en.wikipedia.org/wiki/"
        "List_of_S%26P_500_companies"
    )
    tables = pd.read_html(url)
    df = tables[0]
    tickers = df["Symbol"].tolist()

    # yfinance uses BRK-B not BRK.B; BHGE → BHGE (already correct)
    cleaned = []
    for t in tickers:
        t = str(t).strip()
        # Convert dots to dashes for yfinance compatibility
        t = t.replace(".", "-")
        cleaned.append(t)
    return cleaned


def _cache_path() -> Path:
    """Return path to sp500 cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / "sp500.csv"


def _is_cache_fresh(
    path: Path, max_age_hours: int = SP500_CACHE_TTL_HOURS
) -> bool:
    """Check if cache file is newer than max_age_hours."""
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime < timedelta(hours=max_age_hours)


def _read_cache(path: Path) -> list[str]:
    """Read tickers from cache CSV (one ticker per line)."""
    tickers = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                tickers.append(row[0].strip())
    return tickers


def _write_cache(path: Path, tickers: list[str]) -> None:
    """Write tickers to cache CSV (one ticker per line)."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        for t in tickers:
            writer.writerow([t])
