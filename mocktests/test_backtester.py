"""Comprehensive tests for the backtester package.

Covers CLI parsing, batch indicator computation, condition evaluation,
simulation engine, metrics, and reporting. All yfinance calls are
mocked so no network access is required.
"""
from __future__ import annotations

import math
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from backtester.batch_indicators import (
    COMPONENT_MAP,
    INDICATORS,
    compute_adx,
    compute_atr,
    compute_av,
    compute_bb,
    compute_cci,
    compute_ema,
    compute_macd,
    compute_obv,
    compute_roc,
    compute_rsi,
    compute_rvol,
    compute_sma,
    compute_stoch,
    compute_vwap,
)
from backtester.cli import (
    _parse_indicator_args,
    _parse_single_condition,
    parse_backtest_command,
)
from backtester.data_pipeline import DataPipeline
from backtester.engine import BacktestEngine, BacktestResult, Condition
from backtester.metrics import (
    Trade,
    compute_annualized_return,
    compute_max_drawdown,
    compute_metrics,
    compute_sharpe_ratio,
    compute_sortino_ratio,
    compute_total_return,
)
from backtester.reporting import format_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(
    rows: int = 100,
    start: str = "2025-01-01",
    interval: str = "1d",
) -> pd.DataFrame:
    """Create a synthetic OHLCV DataFrame for testing."""
    dates = pd.date_range(start=start, periods=rows, freq="B")
    np.random.seed(42)
    close = 100.0 + np.cumsum(np.random.randn(rows) * 0.5)
    high = close + abs(np.random.randn(rows) * 0.3)
    low = close - abs(np.random.randn(rows) * 0.3)
    opn = close + np.random.randn(rows) * 0.1
    volume = np.random.randint(1_000_000, 5_000_000, size=rows).astype(float)
    return pd.DataFrame(
        {"Open": opn, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


def _make_ticker_data(
    ticker: str = "AAPL",
    rows: int = 100,
    interval: str = "1d",
) -> dict[str, pd.DataFrame]:
    return {ticker: _make_df(rows=rows, interval=interval)}


# ===================================================================
# §1  CLI Parser Tests
# ===================================================================

class TestParseBacktestCommand:
    """Tests for parse_backtest_command."""

    def test_minimal_command(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d"])
        assert config["tickers"] == ["AAPL"]
        assert len(config["conditions"]) == 1
        assert config["hold"] == 10
        assert config["capital"] == 10_000.0
        assert config["benchmark"] == "SPY"
        assert config["years"] == 2

    def test_multi_ticker(self):
        config = parse_backtest_command(["AAPL,MSFT", "SMA", "50", ">", "200", "1d"])
        assert config["tickers"] == ["AAPL", "MSFT"]

    def test_custom_hold(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--hold", "10"])
        assert config["hold"] == 10

    def test_custom_capital(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--capital", "50000"])
        assert config["capital"] == 50_000.0

    def test_custom_benchmark(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--benchmark", "QQQ"])
        assert config["benchmark"] == "QQQ"

    def test_custom_years(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--years", "5"])
        assert config["years"] == 5

    def test_stop_loss(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--stop-loss", "5"])
        assert config["stop_loss"] == 5.0

    def test_no_stop_loss(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1d"])
        assert config["stop_loss"] is None

    def test_multiple_conditions(self):
        config = parse_backtest_command(
            ["AAPL", "RSI", "<", "30", "1d", "SMA", "50", ">", "200", "1d"]
        )
        assert len(config["conditions"]) == 2

    def test_condition_with_params(self):
        config = parse_backtest_command(
            ["AAPL", "STOCH", "14,5,5", "k", ">", "80", "1d"]
        )
        assert config["conditions"][0].indicator == "STOCH"
        assert config["conditions"][0].params == (14.0, 5.0, 5.0)
        assert config["conditions"][0].component == "k"
        assert config["conditions"][0].operator == ">"
        assert config["conditions"][0].value == 80.0

    def test_bb_condition_with_params(self):
        config = parse_backtest_command(
            ["AAPL", "BB", "20,2", "upper", ">", "150", "1d"]
        )
        cond = config["conditions"][0]
        assert cond.indicator == "BB"
        assert cond.params == (20.0, 2.0)
        assert cond.component == "upper"
        assert cond.operator == ">"
        assert cond.value == 150.0

    def test_macd_condition(self):
        config = parse_backtest_command(
            ["AAPL", "MACD", "12,26,9", "signal", ">", "0", "1d"]
        )
        cond = config["conditions"][0]
        assert cond.indicator == "MACD"
        assert cond.params == (12.0, 26.0, 9.0)
        assert cond.component == "signal"
        assert cond.operator == ">"
        assert cond.value == 0.0

    def test_interval_parsing(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1h"])
        assert config["conditions"][0].interval == "1h"

    def test_no_args_error(self):
        with pytest.raises(ValueError, match="No arguments"):
            parse_backtest_command([])

    def test_no_conditions_error(self):
        with pytest.raises(ValueError, match="No conditions"):
            parse_backtest_command(["AAPL"])

    def test_unknown_indicator_error(self):
        with pytest.raises(ValueError, match="Unknown indicator"):
            parse_backtest_command(["AAPL", "FOO", "<", "30", "1d"])

    def test_missing_interval_error(self):
        with pytest.raises(ValueError, match="interval"):
            parse_backtest_command(["AAPL", "RSI", "<", "30"])

    def test_bad_hold_value(self):
        with pytest.raises(ValueError, match="integer"):
            parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--hold", "abc"])

    def test_malformed_condition_error(self):
        with pytest.raises(ValueError, match="interval"):
            parse_backtest_command(["AAPL", "RSI"])


class TestParseSingleCondition:
    """Tests for _parse_single_condition."""

    def test_basic_condition(self):
        c = _parse_single_condition(["RSI", "<", "30", "1d"])
        assert c.indicator == "RSI"
        assert c.params == ()
        assert c.component is None
        assert c.operator == "<"
        assert c.value == 30.0
        assert c.interval == "1d"

    def test_with_params(self):
        c = _parse_single_condition(["SMA", "50", ">", "200", "1d"])
        assert c.indicator == "SMA"
        assert c.params == (50.0,)
        assert c.component is None
        assert c.operator == ">"
        assert c.value == 200.0

    def test_with_component(self):
        c = _parse_single_condition(["BB", "20,2", "upper", ">", "150", "1d"])
        assert c.indicator == "BB"
        assert c.params == (20.0, 2.0)
        assert c.component == "upper"

    def test_equal_op(self):
        c = _parse_single_condition(["RSI", "==", "50", "1d"])
        assert c.operator == "=="
        assert c.value == 50.0

    def test_unsupported_op(self):
        with pytest.raises(ValueError, match="operator"):
            _parse_single_condition(["RSI", "!=", "50", "1d"])

    def test_too_short(self):
        with pytest.raises(ValueError, match="too short"):
            _parse_single_condition(["RSI", "<", "30"])

    def test_bad_value(self):
        with pytest.raises(ValueError, match="number"):
            _parse_single_condition(["RSI", "<", "abc", "1d"])

    def test_bad_operator(self):
        with pytest.raises(ValueError, match="operator"):
            _parse_single_condition(["RSI", "~", "30", "1d"])


class TestParseIndicatorArgs:
    """Tests for _parse_indicator_args."""

    def test_no_args(self):
        assert _parse_indicator_args("RSI", []) == ((), None)

    def test_single_arg(self):
        assert _parse_indicator_args("SMA", ["50"]) == ((50.0,), None)

    def test_comma_separated(self):
        assert _parse_indicator_args("STOCH", ["14,5,5"]) == ((14.0, 5.0, 5.0), None)

    def test_with_spaces(self):
        assert _parse_indicator_args("STOCH", ["14, 5, 5"]) == ((14.0, 5.0, 5.0), None)

    def test_invalid_arg(self):
        with pytest.raises(ValueError, match="numeric"):
            _parse_indicator_args("RSI", ["abc"])

    def test_with_component(self):
        params, comp = _parse_indicator_args("BB", ["20,2", "upper"])
        assert params == (20.0, 2.0)
        assert comp == "upper"


# ===================================================================
# §2  Batch Indicator Tests
# ===================================================================

class TestBatchIndicators:
    """Tests for vectorized indicator computations on DataFrames."""

    @pytest.fixture
    def df(self):
        return _make_df(rows=200)

    # --- SMA ---
    def test_sma_returns_series(self, df):
        result = compute_sma(df, window=20)
        assert isinstance(result, pd.Series)

    def test_sma_length(self, df):
        result = compute_sma(df, window=20)
        assert len(result) == len(df)

    def test_sma_nan_head(self, df):
        result = compute_sma(df, window=20)
        assert pd.isna(result.iloc[0])
        assert not pd.isna(result.iloc[25])

    def test_sma_values(self, df):
        result = compute_sma(df, window=5)
        expected = df["Close"].rolling(5).mean()
        pd.testing.assert_series_equal(result, expected, check_names=False)

    # --- EMA ---
    def test_ema_returns_series(self, df):
        result = compute_ema(df, window=20)
        assert isinstance(result, pd.Series)

    def test_ema_no_nan(self, df):
        result = compute_ema(df, window=20)
        assert not result.isna().any()

    # --- RSI ---
    def test_rsi_returns_series(self, df):
        result = compute_rsi(df, window=14)
        assert isinstance(result, pd.Series)

    def test_rsi_range(self, df):
        result = compute_rsi(df, window=14)
        valid = result.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    # --- Bollinger Bands ---
    def test_bb_returns_tuple(self, df):
        result = compute_bb(df, window=20, num_std=2)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_bb_ordering(self, df):
        upper, mid, lower = compute_bb(df, window=20, num_std=2)
        valid_idx = upper.dropna().index
        assert (upper[valid_idx] >= mid[valid_idx]).all()
        assert (mid[valid_idx] >= lower[valid_idx]).all()

    # --- MACD ---
    def test_macd_returns_tuple(self, df):
        result = compute_macd(df, fast=12, slow=26, signal=9)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_macd_hist_is_diff(self, df):
        line, signal, hist = compute_macd(df, fast=12, slow=26, signal=9)
        valid_idx = hist.dropna().index
        np.testing.assert_allclose(
            hist[valid_idx].values,
            (line[valid_idx] - signal[valid_idx]).values,
            atol=1e-10,
        )

    # --- Stochastic ---
    def test_stoch_returns_tuple(self, df):
        result = compute_stoch(df, window=14, smooth_k=3, smooth_d=3)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_stoch_range(self, df):
        k, d = compute_stoch(df, window=14, smooth_k=3, smooth_d=3)
        valid = k.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    # --- ADX ---
    def test_adx_returns_tuple(self, df):
        result = compute_adx(df, di_len=14, adx_len=14)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_adx_range(self, df):
        plus_di, minus_di, adx = compute_adx(df, di_len=14, adx_len=14)
        valid = adx.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    # --- ATR ---
    def test_atr_returns_series(self, df):
        result = compute_atr(df, window=14)
        assert isinstance(result, pd.Series)

    def test_atr_positive(self, df):
        result = compute_atr(df, window=14)
        valid = result.dropna()
        assert (valid >= 0).all()

    # --- CCI ---
    def test_cci_returns_series(self, df):
        result = compute_cci(df, window=20)
        assert isinstance(result, pd.Series)

    # --- OBV ---
    def test_obv_returns_series(self, df):
        result = compute_obv(df)
        assert isinstance(result, pd.Series)

    def test_obv_length(self, df):
        result = compute_obv(df)
        assert len(result) == len(df)

    # --- ROC ---
    def test_roc_returns_series(self, df):
        result = compute_roc(df, window=10)
        assert isinstance(result, pd.Series)

    # --- RVOL ---
    def test_rvol_returns_series(self, df):
        result = compute_rvol(df, window=20)
        assert isinstance(result, pd.Series)

    def test_rvol_positive(self, df):
        result = compute_rvol(df, window=20)
        valid = result.dropna()
        assert (valid >= 0).all()

    # --- AV ---
    def test_av_returns_series(self, df):
        result = compute_av(df, window=20)
        assert isinstance(result, pd.Series)

    # --- VWAP ---
    def test_vwap_returns_series(self, df):
        result = compute_vwap(df)
        assert isinstance(result, pd.Series)

    def test_vwap_positive(self, df):
        result = compute_vwap(df)
        valid = result.dropna()
        assert (valid >= 0).all()


class TestComponentMap:
    """Tests for COMPONENT_MAP completeness."""

    def test_all_indicators_have_components(self):
        for name in INDICATORS:
            assert name in COMPONENT_MAP, f"{name} missing from COMPONENT_MAP"

    def test_bb_has_upper_mid_lower(self):
        comps = COMPONENT_MAP["BB"]
        assert "upper" in comps
        assert "middle" in comps
        assert "lower" in comps

    def test_macd_has_line_signal_hist(self):
        comps = COMPONENT_MAP["MACD"]
        assert "line" in comps
        assert "signal" in comps
        assert "hist" in comps

    def test_stoch_has_k_d(self):
        comps = COMPONENT_MAP["STOCH"]
        assert "k" in comps
        assert "d" in comps


class TestIndicatorsRegistry:
    """Tests for INDICATORS dispatch dict."""

    def test_all_expected_indicators_registered(self):
        expected = {
            "SMA", "EMA", "RSI", "BB", "MACD", "STOCH",
            "ADX", "ATR", "CCI", "OBV", "ROC", "RVOL",
            "AV", "VWAP",
        }
        assert set(INDICATORS.keys()) == expected

    def test_all_are_strings(self):
        for name, fn in INDICATORS.items():
            assert isinstance(fn, str), f"{name} is not a string"


# ===================================================================
# §3  Data Pipeline Tests
# ===================================================================

class TestDataPipeline:
    """Tests for DataPipeline parquet caching."""

    @pytest.fixture(autouse=True)
    def temp_cache(self, tmp_path):
        self.cache_dir = tmp_path / "cache"
        self.cache_dir.mkdir()
        self.pipeline = DataPipeline(cache_dir=self.cache_dir)

    def test_cache_miss_fetches_data(self):
        mock_df = _make_df(rows=50)
        mock_data = {"AAPL": mock_df}
        with patch.object(self.pipeline, "_download_batch", return_value=mock_data):
            result = self.pipeline.fetch(["AAPL"], "1d", 1)
        assert "AAPL" in result
        assert len(result["AAPL"]) == 50

    def test_cache_hit_uses_parquet(self):
        mock_df = _make_df(rows=50)
        cache_path = self.pipeline._cache_path("AAPL", "1d")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Create a dummy file so path.exists() returns True
        cache_path.touch()
        # Mock the parquet read to return our data
        with patch("backtester.data_pipeline.pd.read_parquet", return_value=mock_df):
            with patch.object(self.pipeline, "_download_batch") as mock_dl:
                result = self.pipeline.fetch(["AAPL"], "1d", 1)
        mock_dl.assert_not_called()
        assert "AAPL" in result

    def test_cache_write_creates_parquet(self):
        mock_df = _make_df(rows=50)
        mock_data = {"AAPL": mock_df}
        # Mock the parquet write
        with patch.object(mock_df, "to_parquet") as mock_to_parquet:
            with patch.object(self.pipeline, "_download_batch", return_value=mock_data):
                self.pipeline.fetch(["AAPL"], "1d", 1)
        mock_to_parquet.assert_called_once()

    def test_empty_download_returns_empty(self):
        with patch.object(self.pipeline, "_download_batch", return_value={}):
            result = self.pipeline.fetch(["AAPL"], "1d", 1)
        assert result == {}

    def test_multiple_tickers(self):
        mock_aapl = _make_df(rows=50)
        mock_msft = _make_df(rows=50)
        mock_data = {"AAPL": mock_aapl, "MSFT": mock_msft}
        with patch.object(self.pipeline, "_download_batch", return_value=mock_data):
            result = self.pipeline.fetch(["AAPL", "MSFT"], "1d", 1)
        assert "AAPL" in result
        assert "MSFT" in result


# ===================================================================
# §4  Condition Evaluation Tests
# ===================================================================

class TestConditionEvaluation:
    """Tests for Condition evaluation logic."""

    def test_condition_creation(self):
        cond = Condition("RSI", (), None, "<", 50.0, "1d")
        assert cond.indicator == "RSI"
        assert cond.params == ()
        assert cond.component is None
        assert cond.operator == "<"
        assert cond.value == 50.0
        assert cond.interval == "1d"

    def test_condition_with_params(self):
        cond = Condition("BB", (20.0, 2.0), "upper", ">", 150.0, "1d")
        assert cond.indicator == "BB"
        assert cond.params == (20.0, 2.0)
        assert cond.component == "upper"


# ===================================================================
# §5  Engine Simulation Tests
# ===================================================================

class TestBacktestEngine:
    """Tests for the simulation engine."""

    def _make_config(self, **overrides):
        config = {
            "tickers": ["AAPL"],
            "conditions": [Condition("RSI", (), None, "<", 50.0, "1d")],
            "hold": 10,
            "capital": 10_000.0,
            "benchmark": "SPY",
            "years": 2,
            "stop_loss": None,
        }
        config.update(overrides)
        return config

    @patch("backtester.engine.DataPipeline")
    def test_run_returns_backtest_result(self, MockPipeline):
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert isinstance(result, BacktestResult)
        assert result.config == config

    @patch("backtester.engine.DataPipeline")
    def test_no_data_returns_empty_result(self, MockPipeline):
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert isinstance(result, BacktestResult)
        assert result.trades == []
        assert result.metrics == {}

    @patch("backtester.engine.DataPipeline")
    def test_hold_period(self, MockPipeline):
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(hold=10)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        for trade in result.trades:
            assert trade.hold_bars == 10

    @patch("backtester.engine.DataPipeline")
    def test_no_signals(self, MockPipeline):
        # Monotonically increasing prices → RSI stays above 50
        dates = pd.date_range(start="2025-01-01", periods=200, freq="B")
        close = np.linspace(100, 200, 200)
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(200, 1_000_000.0)},
            index=dates,
        )
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert result.trades == []


# ===================================================================
# §6  Metrics Tests
# ===================================================================

class TestMetrics:
    """Tests for financial metrics computation."""

    def _make_trade(
        self,
        entry_price: float = 100.0,
        exit_price: float = 110.0,
        hold_bars: int = 5,
    ) -> Trade:
        return_pct = (exit_price - entry_price) / entry_price * 100
        return Trade(
            ticker="AAPL",
            entry_date=pd.Timestamp("2025-01-01"),
            entry_price=entry_price,
            exit_date=pd.Timestamp("2025-01-01") + pd.Timedelta(days=hold_bars),
            exit_price=exit_price,
            hold_bars=hold_bars,
            return_pct=return_pct,
        )

    def test_compute_total_return(self):
        trades = [self._make_trade(100.0, 110.0, 5)]
        result = compute_total_return(trades, 10_000.0)
        assert result == pytest.approx(10.0, abs=1e-2)

    def test_compute_total_return_loss(self):
        trades = [self._make_trade(100.0, 90.0, 5)]
        result = compute_total_return(trades, 10_000.0)
        assert result == pytest.approx(-10.0, abs=1e-2)

    def test_compute_total_return_no_trades(self):
        result = compute_total_return([], 10_000.0)
        assert result == 0.0

    def test_compute_annualized_return(self):
        result = compute_annualized_return(10.0, 1.0)
        assert result > 0

    def test_compute_max_drawdown(self):
        equity = pd.Series([100, 110, 105, 95, 100])
        result = compute_max_drawdown(equity)
        assert result == pytest.approx(0.1364, abs=0.001)

    def test_compute_max_drawdown_no_drawdown(self):
        equity = pd.Series([100, 105, 110, 115])
        result = compute_max_drawdown(equity)
        assert result == 0.0

    def test_compute_sharpe_ratio(self):
        daily_returns = pd.Series([0.01, -0.005, 0.008, 0.002, -0.001])
        result = compute_sharpe_ratio(daily_returns)
        assert math.isfinite(result)

    def test_compute_sortino_ratio(self):
        daily_returns = pd.Series([0.01, -0.005, 0.008, 0.002, -0.001])
        result = compute_sortino_ratio(daily_returns)
        assert math.isfinite(result)

    def test_compute_metrics_structure(self):
        trades = [self._make_trade(100.0, 110.0, 5)]
        result = compute_metrics(trades, 10_000.0)
        assert "total_trades" in result
        assert "winning_trades" in result
        assert "losing_trades" in result
        assert "win_rate" in result
        assert "total_return" in result
        assert "annualized_return" in result
        assert "sharpe_ratio" in result
        assert "sortino_ratio" in result
        assert "max_drawdown" in result
        assert "avg_trade_return" in result
        assert "profit_factor" in result

    def test_compute_metrics_no_trades(self):
        result = compute_metrics([], 10_000.0)
        assert result["total_trades"] == 0
        assert result["total_return"] == 0.0


# ===================================================================
# §7  Reporting Tests
# ===================================================================

class TestReporting:
    """Tests for format_results output."""

    def test_format_results_basic(self):
        result = BacktestResult(
            trades=[],
            metrics={"total_trades": 0, "total_return": 0.0},
            benchmark_metrics={},
            ticker_results={},
            conditions=[],
            config={"tickers": ["AAPL"], "hold": 10, "capital": 10_000.0,
                    "benchmark": "SPY", "years": 2, "stop_loss": None},
        )
        output = format_results(result)
        assert "QuantLab" in output
        assert "0" in output

    def test_format_results_with_trades(self):
        trades = [
            Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-01-06"), 110.0, 5, 10.0),
        ]
        metrics = {
            "total_trades": 1,
            "total_return": 10.0,
            "annualized_return": 50.0,
            "sharpe_ratio": 1.5,
            "sortino_ratio": 2.0,
            "max_drawdown": 5.0,
            "win_rate": 1.0,
            "profit_factor": float("inf"),
        }
        result = BacktestResult(
            trades=trades,
            metrics=metrics,
            benchmark_metrics={},
            ticker_results={"AAPL": trades},
            conditions=[],
            config={"tickers": ["AAPL"], "hold": 10, "capital": 10_000.0,
                    "benchmark": "SPY", "years": 2, "stop_loss": None},
        )
        output = format_results(result)
        assert "AAPL" in output
        assert "1" in output


# ===================================================================
# §8  Multi-Ticker Tests
# ===================================================================

class TestMultiTicker:
    """Tests for multi-ticker backtesting."""

    @patch("backtester.engine.DataPipeline")
    def test_multi_ticker_download(self, MockPipeline):
        mock_aapl = _make_df(rows=200)
        mock_msft = _make_df(rows=200)
        mock_aapl["rsi_14"] = 30.0
        mock_msft["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_aapl, "MSFT": mock_msft}

        conditions = [Condition("RSI", (), None, "<", 50.0, "1d")]
        config = {
            "tickers": ["AAPL", "MSFT"],
            "conditions": conditions,
            "hold": 10,
            "capital": 10_000.0,
            "benchmark": "SPY",
            "years": 2,
            "stop_loss": None,
        }
        engine = BacktestEngine(conditions, config)
        result = engine.run()

        assert len(result.ticker_results) == 2
        assert "AAPL" in result.ticker_results
        assert "MSFT" in result.ticker_results

    @patch("backtester.engine.DataPipeline")
    def test_multi_ticker_partial_data(self, MockPipeline):
        mock_aapl = _make_df(rows=200)
        mock_aapl["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_aapl}

        conditions = [Condition("RSI", (), None, "<", 50.0, "1d")]
        config = {
            "tickers": ["AAPL", "MSFT"],
            "conditions": conditions,
            "hold": 10,
            "capital": 10_000.0,
            "benchmark": "SPY",
            "years": 2,
            "stop_loss": None,
        }
        engine = BacktestEngine(conditions, config)
        result = engine.run()

        assert "AAPL" in result.ticker_results
        assert "MSFT" not in result.ticker_results


# ===================================================================
# §9  Error Handling Tests
# ===================================================================

class TestErrorHandling:
    """Tests for graceful error handling."""

    def test_empty_input(self):
        with pytest.raises(ValueError, match="No arguments"):
            parse_backtest_command([])

    def test_single_word(self):
        with pytest.raises(ValueError, match="No conditions"):
            parse_backtest_command(["AAPL"])

    def test_unknown_indicator(self):
        with pytest.raises(ValueError, match="Unknown indicator"):
            parse_backtest_command(["AAPL", "INVALID", "<", "30", "1d"])

    def test_bad_hold_value(self):
        with pytest.raises(ValueError, match="integer"):
            parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--hold", "abc"])

    def test_missing_interval(self):
        with pytest.raises(ValueError, match="interval"):
            parse_backtest_command(["AAPL", "RSI", "<", "30"])

    def test_unknown_component(self):
        with pytest.raises(ValueError, match="numeric"):
            parse_backtest_command(["AAPL", "BB", "20,2", "foo", ">", "150", "1d"])


# ===================================================================
# §10  Cache Directory Tests
# ===================================================================

class TestCacheDirectory:
    """Tests for parquet cache directory behavior."""

    def test_cache_dir_created(self, tmp_path):
        cache_dir = tmp_path / "test_cache"
        pipeline = DataPipeline(cache_dir=cache_dir)
        assert cache_dir.exists()

    def test_cache_file_naming(self, tmp_path):
        cache_dir = tmp_path / "test_cache2"
        pipeline = DataPipeline(cache_dir=cache_dir)
        assert hasattr(pipeline, "cache_dir")
