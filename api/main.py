# api/main.py
"""QuantLab FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="QuantLab API",
    description="Backtesting API for technical indicator strategies",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://szuck12.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/health/data")
def health_data() -> dict:
    """Probe market-data connectivity and report the frame shape.

    Fetches a small SPY slice and reports row/column/tz info. Useful
    for diagnosing production data issues (rate limits, MultiIndex
    column shapes) without running a full backtest.
    """
    from backtester.data_pipeline import DataPipeline

    try:
        data = DataPipeline().fetch(["SPY"], "1d", 0.1)
        df = data.get("SPY")
        if df is None or df.empty:
            return {
                "status": "error",
                "detail": "No data returned for SPY.",
            }
        return {
            "status": "ok",
            "rows": int(len(df)),
            "columns": [str(c) for c in df.columns],
            "index_tz": str(getattr(df.index, "tz", None)),
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {"status": "error", "detail": str(exc)}
