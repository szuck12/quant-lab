# mocktests/test_api.py
"""Tests for the QuantLab FastAPI endpoints.

All yfinance calls are mocked — no network access in these tests.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture()
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


def _make_ohlcv(rows: int = 200, start_price: float = 50.0) -> pd.DataFrame:
    """Create a mock OHLCV DataFrame with trending prices."""
    dates = pd.date_range(start="2025-01-01", periods=rows, freq="B")
    np.random.seed(42)
    close = start_price + np.cumsum(np.random.randn(rows) * 3)
    close = np.maximum(close, 10)
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1,
            "Low": close - 1,
            "Close": close,
            "Volume": np.full(rows, 1_000_000.0),
        },
        index=dates,
    )


def _mock_pipeline_fetch(tickers, interval, years):
    """Return mock data for DataPipeline.fetch."""
    df = _make_ohlcv(200)
    return {t: df.copy() for t in tickers}


# -- GET /api/indicators tests --


class TestListIndicators:
    def test_returns_all_14_indicators(self, client):
        resp = client.get("/api/indicators")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 14
        names = [ind["name"] for ind in data]
        assert "RSI" in names
        assert "SMA" in names
        assert "MACD" in names
        assert "BB" in names

    def test_indicator_has_params(self, client):
        resp = client.get("/api/indicators")
        data = resp.json()
        rsi = next(i for i in data if i["name"] == "RSI")
        assert len(rsi["params"]) == 1
        assert rsi["params"][0]["name"] == "window"
        assert rsi["params"][0]["default"] == 14

    def test_indicator_has_hint(self, client):
        resp = client.get("/api/indicators")
        data = resp.json()
        rsi = next(i for i in data if i["name"] == "RSI")
        assert "value_hint" in rsi
        assert "0" in rsi["value_hint"]

    def test_param_has_hint(self, client):
        resp = client.get("/api/indicators")
        data = resp.json()
        rsi = next(i for i in data if i["name"] == "RSI")
        assert "hint" in rsi["params"][0]

    def test_multi_param_indicator(self, client):
        resp = client.get("/api/indicators")
        data = resp.json()
        macd = next(i for i in data if i["name"] == "MACD")
        assert len(macd["params"]) == 3
        param_names = [p["name"] for p in macd["params"]]
        assert "fast" in param_names
        assert "slow" in param_names
        assert "signal" in param_names

    def test_components_present(self, client):
        resp = client.get("/api/indicators")
        data = resp.json()
        bb = next(i for i in data if i["name"] == "BB")
        assert "upper" in bb["components"]
        assert "middle" in bb["components"]
        assert "lower" in bb["components"]

    def test_single_component_indicator(self, client):
        resp = client.get("/api/indicators")
        data = resp.json()
        rsi = next(i for i in data if i["name"] == "RSI")
        assert rsi["components"] == ["value"]


# -- GET /api/config tests --


class TestGetConfig:
    def test_returns_config(self, client):
        resp = client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "max_years" in data
        assert "default_years" in data
        assert "default_capital" in data

    def test_max_years_reasonable(self, client):
        resp = client.get("/api/config")
        data = resp.json()
        assert data["max_years"] >= 5
        assert data["max_years"] <= 100


# -- POST /api/backtest tests --


class TestRunBacktest:
    @patch("backtester.engine.DataPipeline")
    def test_basic_backtest(self, MockPipeline, client):
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = _mock_pipeline_fetch(
            ["AAPL"], "1d", 2
        )

        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "params": {"window": 14},
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
                "capital": 10000,
                "years": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "trades" in data
        assert "metrics" in data
        assert "equity_curve" in data
        assert "benchmark_metrics" in data

    @patch("backtester.engine.DataPipeline")
    def test_response_structure(self, MockPipeline, client):
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = _mock_pipeline_fetch(
            ["AAPL"], "1d", 2
        )

        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "params": {"window": 14},
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
            },
        )
        data = resp.json()

        if data["trades"]:
            trade = data["trades"][0]
            assert "ticker" in trade
            assert "entry_date" in trade
            assert "entry_price" in trade
            assert "exit_date" in trade
            assert "exit_price" in trade
            assert "hold_bars" in trade
            assert "return_pct" in trade

        m = data["metrics"]
        assert "total_trades" in m
        assert "win_rate" in m
        assert "total_return" in m
        assert "sharpe_ratio" in m
        assert "max_drawdown" in m

        assert isinstance(data["equity_curve"], list)
        if data["equity_curve"]:
            pt = data["equity_curve"][0]
            assert "date" in pt
            assert "strategy" in pt
            assert "benchmark" in pt

    @patch("backtester.engine.DataPipeline")
    def test_multi_condition(self, MockPipeline, client):
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = _mock_pipeline_fetch(
            ["AAPL"], "1d", 2
        )

        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "params": {"window": 14},
                        "operator": "<",
                        "value": 70,
                        "interval": "1d",
                    },
                    {
                        "indicator": "SMA",
                        "params": {"window": 50},
                        "operator": ">",
                        "value": 10,
                        "interval": "1d",
                    },
                ],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["conditions"]) == 2

    @patch("backtester.engine.DataPipeline")
    def test_custom_capital(self, MockPipeline, client):
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = _mock_pipeline_fetch(
            ["AAPL"], "1d", 2
        )

        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "params": {"window": 14},
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
                "capital": 50000,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["config"]["capital"] == 50000

    def test_invalid_indicator(self, client):
        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "FAKE",
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
            },
        )
        assert resp.status_code == 422

    def test_invalid_operator(self, client):
        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "operator": "!=",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
            },
        )
        assert resp.status_code == 422

    def test_empty_conditions(self, client):
        resp = client.post(
            "/api/backtest",
            json={"conditions": []},
        )
        assert resp.status_code == 422

    def test_invalid_years_zero(self, client):
        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
                "years": 0,
            },
        )
        assert resp.status_code == 422

    def test_invalid_years_negative(self, client):
        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
                "years": -1,
            },
        )
        assert resp.status_code == 422

    def test_invalid_capital_zero(self, client):
        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
                "capital": 0,
            },
        )
        assert resp.status_code == 422

    def test_invalid_capital_negative(self, client):
        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
                "capital": -1000,
            },
        )
        assert resp.status_code == 422

    @patch("backtester.engine.DataPipeline")
    def test_equity_curve_dates_are_strings(self, MockPipeline, client):
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = _mock_pipeline_fetch(
            ["AAPL"], "1d", 2
        )

        resp = client.post(
            "/api/backtest",
            json={
                "conditions": [
                    {
                        "indicator": "RSI",
                        "params": {"window": 14},
                        "operator": "<",
                        "value": 30,
                        "interval": "1d",
                    }
                ],
            },
        )
        data = resp.json()
        for pt in data["equity_curve"]:
            assert isinstance(pt["date"], str)
            assert isinstance(pt["strategy"], (int, float))
            assert isinstance(pt["benchmark"], (int, float))


# -- Health check --


class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# -- Frontend integration tests --


class TestFrontendIntegration:
    def test_indicators_match_frontend_types(self, client):
        """Verify indicator response matches TypeScript IndicatorInfo interface."""
        resp = client.get("/api/indicators")
        data = resp.json()
        for ind in data:
            # Required fields
            assert "name" in ind
            assert "params" in ind
            assert "components" in ind
            # params structure
            for param in ind["params"]:
                assert "name" in param
                assert "type" in param
                assert "default" in param
                # Optional fields
                if "hint" in param:
                    assert isinstance(param["hint"], str)
                if "min" in param:
                    assert isinstance(param["min"], (int, float))
                if "max" in param:
                    assert isinstance(param["max"], (int, float))

    def test_config_matches_frontend_types(self, client):
        """Verify config response matches TypeScript AppConfig interface."""
        resp = client.get("/api/config")
        data = resp.json()
        assert "max_years" in data
        assert isinstance(data["max_years"], int)
        assert data["max_years"] > 0
