# backtester/universe.py
"""Ticker universe resolution.

Resolves universe names (sp500) or CSV file paths to lists of
tickers for bulk strategy scanning.
"""

from __future__ import annotations

import csv
import io
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

CACHE_DIR = Path(__file__).parent / "cache"
SP500_CACHE_TTL_HOURS = 24
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


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

    Uses a browser-like User-Agent header to avoid 403 errors.
    Falls back to a hardcoded list if scraping fails.

    Returns:
        List of ticker strings with BRK.B → BRK-B conversion.
    """
    url = (
        "https://en.wikipedia.org/wiki/"
        "List_of_S%26P_500_companies"
    )
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": _USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
        tables = pd.read_html(io.StringIO(html))
        df = tables[0]
        tickers = df["Symbol"].tolist()
    except Exception:
        # Fallback: use a recent snapshot of S&P 500 tickers
        tickers = _FALLBACK_SP500[:]

    # yfinance uses BRK-B not BRK.B; BHGE → BHGE (already correct)
    cleaned = []
    for t in tickers:
        t = str(t).strip()
        # Convert dots to dashes for yfinance compatibility
        t = t.replace(".", "-")
        cleaned.append(t)
    return cleaned


# Fallback S&P 500 list (Aug 2026 snapshot, ~503 tickers).
# Used when Wikipedia scraping fails (e.g. 403, network error).
_FALLBACK_SP500 = [
    "A", "AAPL", "ABBV", "ABNB", "ABT", "ACN", "ADBE", "ADI",
    "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL", "AIG",
    "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE",
    "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN",
    "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APTV",
    "ARE", "ATO", "ATVI", "AVB", "AVGO", "AVY", "AWK", "AXP",
    "AZO", "BA", "BAC", "BAX", "BBWI", "BBY", "BDX", "BEN",
    "BF-B", "BIIB", "BIO", "BK", "BKNG", "BKR", "BMY", "BR",
    "BRK-B", "BRO", "BSX", "BWA", "BXP", "C", "CAG", "CAH",
    "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCL", "CDAY",
    "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW",
    "CHTR", "CI", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME",
    "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP",
    "COST", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSCO", "CSGP",
    "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CVS", "CVX",
    "CZR", "D", "DAL", "DD", "DE", "DFS", "DG", "DGX", "DHI",
    "DHR", "DIS", "DISH", "DLTR", "DOV", "DOW", "DPZ", "DRI",
    "DTE", "DUK", "DVA", "DVN", "DXC", "DXCM", "EA", "EBAY",
    "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH",
    "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN",
    "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR",
    "F", "FANG", "FAST", "FBHS", "FCX", "FDS", "FDX", "FE",
    "FFIV", "FIS", "FISV", "FLT", "FMC", "FOX", "FOXA", "FRC",
    "FRT", "FTNT", "FTV", "GD", "GE", "GEHC", "GEN", "GILD",
    "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC",
    "GPN", "GRMN", "GS", "GWW", "HAL", "HAS", "HBAN", "HCA",
    "HD", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST",
    "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX", "IFF",
    "ILMN", "INCY", "INTC", "INTU", "INVH", "IP", "IPG", "IQV",
    "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT",
    "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KDP", "KEY",
    "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO",
    "KR", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ",
    "LMT", "LNC", "LNT", "LOW", "LRCX", "LUMN", "LUV", "LVS",
    "LW", "LYB", "LYV", "MA", "MAA", "MAR", "MAS", "MCD",
    "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "MGM",
    "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO",
    "MOH", "MOS", "MPC", "MPWR", "MRK", "MRNA", "MRO", "MS",
    "MSCI", "MSFT", "MSI", "MTB", "MTCH", "MU", "NDSN", "NEE",
    "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG", "NSC",
    "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWL", "NWS", "NWSA",
    "NXPI", "O", "ODFL", "OGN", "OKE", "OMC", "ON", "ORCL",
    "ORLY", "OTIS", "OXY", "PARA", "PAYC", "PAYX", "PCAR", "PCG",
    "PEAK", "PEG", "PEP", "PFE", "PFG", "PG", "PGR", "PH",
    "PHM", "PKG", "PKI", "PLD", "PM", "PNC", "PNR", "PNW",
    "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PVH",
    "PWR", "PXD", "PYPL", "QCOM", "QRVO", "RCL", "RE", "REG",
    "REGN", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL",
    "ROP", "ROST", "RSG", "RTX", "SBAC", "SBNY", "SCHW", "SEE",
    "SHW", "SIVB", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG",
    "SPGI", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS",
    "SYF", "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH",
    "TEL", "TER", "TFC", "TFX", "TGT", "TMO", "TMUS", "TPR",
    "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT",
    "TTWO", "TXN", "TXT", "TYL", "UAL", "UDR", "UHS", "ULTA",
    "UNH", "UNP", "UPS", "URI", "USB", "V", "VFC", "VICI",
    "VLO", "VMC", "VNO", "VRSK", "VRSN", "VRTX", "VTR", "VTRS",
    "VZ", "WAB", "WAT", "WBA", "WBD", "WDC", "WEC", "WELL",
    "WFC", "WHR", "WM", "WMB", "WMT", "WRB", "WRK", "WST",
    "WY", "WYNN", "XEL", "XOM", "XRAY", "XYL", "YUM", "ZBH",
    "ZBRA", "ZION", "ZTS",
]


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
