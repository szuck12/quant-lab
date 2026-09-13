# api/main.py
"""QuantLab FastAPI application."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import GENERIC_BACKTEST_ERROR, router

logger = logging.getLogger(__name__)

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return a friendly message for malformed requests.

    The default FastAPI 422 body exposes internal field/error details;
    users should only ever see a plain-language message.
    """
    logger.warning("Validation error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={
            "detail": (
                "Some of the values you entered were invalid. Please "
                "check the form and try again."
            )
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Return a generic customer-facing message for unhandled errors.

    The real exception (which may contain internal details) is logged
    server-side and never returned to the client.
    """
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": GENERIC_BACKTEST_ERROR},
    )


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
                "detail": "Market data is temporarily unavailable.",
            }
        return {
            "status": "ok",
            "rows": int(len(df)),
            "columns": [str(c) for c in df.columns],
            "index_tz": str(getattr(df.index, "tz", None)),
        }
    except Exception:  # pragma: no cover - defensive
        logger.exception("Data health probe failed")
        return {
            "status": "error",
            "detail": "Market data is temporarily unavailable.",
        }
