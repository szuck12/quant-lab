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

    def test_sma_float_window_converted_to_int(self, df):
        """Float window (50.0) must be converted to int for rolling()."""
        from backtester.batch_indicators import compute_indicator
        result = compute_indicator(df, "SMA", (50.0,))
        assert isinstance(result, pd.Series)
        assert not result.isna().all()

    def test_compute_indicator_float_params(self, df):
        """compute_indicator passes int-converted params to functions."""
        from backtester.batch_indicators import compute_indicator
        result = compute_indicator(df, "RSI", (14.0,))
        assert isinstance(result, pd.Series)
        assert not result.isna().all()

    def test_compute_indicator_bb_float_params(self, df):
        """BB keeps num_std as float but converts window to int."""
        from backtester.batch_indicators import compute_bb
        upper, middle, lower = compute_bb(df, 20, 2.0)
        assert isinstance(upper, pd.Series)
        assert isinstance(middle, pd.Series)
        assert isinstance(lower, pd.Series)

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
        return_pct = (exit_price - entry_price) / entry_price
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
        assert result == pytest.approx(0.10, abs=1e-4)

    def test_compute_total_return_loss(self):
        trades = [self._make_trade(100.0, 90.0, 5)]
        result = compute_total_return(trades, 10_000.0)
        assert result == pytest.approx(-0.10, abs=1e-4)

    def test_compute_total_return_no_trades(self):
        result = compute_total_return([], 10_000.0)
        assert result == 0.0

    def test_compute_annualized_return(self):
        # 10% total return over 1 year
        result = compute_annualized_return(0.10, 1.0)
        assert result == pytest.approx(0.10, abs=1e-4)

    def test_compute_annualized_return_multi_year(self):
        # 21% total return over 2 years → ~10% annualized
        result = compute_annualized_return(0.21, 2.0)
        assert result == pytest.approx(0.10, abs=0.01)

    def test_compute_annualized_return_loss(self):
        # -50% total return over 1 year
        result = compute_annualized_return(-0.50, 1.0)
        assert result == pytest.approx(-0.50, abs=1e-4)

    def test_compute_annualized_return_zero_years(self):
        result = compute_annualized_return(0.10, 0.0)
        assert result == 0.0

    def test_compute_annualized_return_total_loss(self):
        # -100% return → 0.0 (can't recover)
        result = compute_annualized_return(-1.0, 1.0)
        assert result == 0.0

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


# ===================================================================
# §11  Operator Alias Tests (shell-safe syntax)
# ===================================================================

class TestOperatorAliases:
    """Tests for word-based operator aliases that avoid shell redirection."""

    def test_below_alias(self):
        c = _parse_single_condition(["RSI", "below", "30", "1d"])
        assert c.operator == "<"
        assert c.value == 30.0

    def test_above_alias(self):
        c = _parse_single_condition(["SMA", "50", "above", "200", "1d"])
        assert c.operator == ">"

    def test_at_or_below_alias(self):
        c = _parse_single_condition(["RSI", "at_or_below", "30", "1d"])
        assert c.operator == "<="

    def test_at_or_above_alias(self):
        c = _parse_single_condition(["RSI", "at_or_above", "70", "1d"])
        assert c.operator == ">="

    def test_equals_alias(self):
        c = _parse_single_condition(["RSI", "equals", "50", "1d"])
        assert c.operator == "=="

    def test_less_than_alias(self):
        c = _parse_single_condition(["RSI", "less_than", "30", "1d"])
        assert c.operator == "<"

    def test_greater_than_alias(self):
        c = _parse_single_condition(["SMA", "greater_than", "200", "1d"])
        assert c.operator == ">"

    def test_under_alias(self):
        c = _parse_single_condition(["RSI", "under", "30", "1d"])
        assert c.operator == "<"

    def test_over_alias(self):
        c = _parse_single_condition(["RSI", "over", "70", "1d"])
        assert c.operator == ">"

    def test_at_most_alias(self):
        c = _parse_single_condition(["RSI", "at_most", "30", "1d"])
        assert c.operator == "<="

    def test_at_least_alias(self):
        c = _parse_single_condition(["RSI", "at_least", "70", "1d"])
        assert c.operator == ">="

    def test_eq_alias(self):
        c = _parse_single_condition(["RSI", "eq", "50", "1d"])
        assert c.operator == "=="

    def test_equal_to_alias(self):
        c = _parse_single_condition(["RSI", "equal_to", "50", "1d"])
        assert c.operator == "=="

    def test_case_insensitive_alias(self):
        c = _parse_single_condition(["RSI", "Below", "30", "1d"])
        assert c.operator == "<"

    def test_full_backtest_with_alias(self):
        config = parse_backtest_command(
            ["AAPL", "RSI", "below", "30", "1d"]
        )
        assert config["conditions"][0].operator == "<"

    def test_multiple_conditions_with_aliases(self):
        config = parse_backtest_command(
            ["AAPL", "RSI", "below", "30", "1d",
             "SMA", "50", "above", "200", "1d"]
        )
        assert len(config["conditions"]) == 2
        assert config["conditions"][0].operator == "<"
        assert config["conditions"][1].operator == ">"


# ===================================================================
# §12  CLI Edge Case Tests
# ===================================================================

class TestCLIClientCases:
    """Additional CLI edge case coverage."""

    def test_trailing_comma_ticker(self):
        config = parse_backtest_command(["AAPL,", "RSI", "<", "30", "1d"])
        assert config["tickers"] == ["AAPL"]

    def test_spaces_around_comma(self):
        config = parse_backtest_command(["AAPL , MSFT", "RSI", "<", "30", "1d"])
        assert config["tickers"] == ["AAPL", "MSFT"]

    def test_mixed_case_interval(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1D"])
        assert config["conditions"][0].interval == "1d"

    def test_mixed_case_indicator(self):
        config = parse_backtest_command(["AAPL", "rsi", "<", "30", "1d"])
        assert config["conditions"][0].indicator == "RSI"

    def test_option_missing_value(self):
        with pytest.raises(ValueError, match="requires a value"):
            parse_backtest_command(["AAPL", "RSI", "<", "30", "1d", "--hold"])

    def test_stop_loss_option(self):
        config = parse_backtest_command(
            ["AAPL", "RSI", "<", "30", "1d", "--stop-loss", "5"]
        )
        assert config["stop_loss"] == 5.0

    def test_rsi_with_custom_window(self):
        config = parse_backtest_command(["AAPL", "RSI", "14", "<", "30", "1d"])
        assert config["conditions"][0].params == (14.0,)

    def test_rsi_too_many_params(self):
        with pytest.raises(ValueError, match="at most 1"):
            parse_backtest_command(
                ["AAPL", "RSI", "14,20", "<", "30", "1d"]
            )

    def test_sma_no_params_uses_default(self):
        config = parse_backtest_command(["AAPL", "SMA", ">", "200", "1d"])
        assert config["conditions"][0].params == ()

    def test_weekly_interval(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1wk"])
        assert config["conditions"][0].interval == "1wk"

    def test_monthly_interval(self):
        config = parse_backtest_command(["AAPL", "RSI", "<", "30", "1mo"])
        assert config["conditions"][0].interval == "1mo"


# ===================================================================
# §13  Engine Edge Case Tests
# ===================================================================

class TestEngineEdgeCases:
    """Tests for engine edge cases and robustness."""

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
    def test_stop_loss_triggers(self, MockPipeline):
        """Stop-loss should exit trade early when price drops."""
        dates = pd.date_range(start="2025-01-01", periods=200, freq="B")
        # Steep decline: 100 → 50 over 200 bars (0.25/bar)
        # After 5 bars, price drops ~1.25 (1.25%) → triggers 1% stop-loss
        close = np.linspace(100, 50, 200)
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(200, 1_000_000.0)},
            index=dates,
        )
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(stop_loss=1.0, hold=50)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # With steep decline and 1% stop-loss, trades should exit early
        early_exits = [t for t in result.trades if t.hold_bars < 50]
        assert len(early_exits) > 0

    @patch("backtester.engine.DataPipeline")
    def test_hold_period_one_bar(self, MockPipeline):
        """Hold=1 should exit on the very next bar."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(hold=1)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        for trade in result.trades:
            assert trade.hold_bars == 1

    @patch("backtester.engine.DataPipeline")
    def test_trade_near_end_of_data(self, MockPipeline):
        """Trade starting near end should be skipped if hold extends past data."""
        mock_df = _make_df(rows=50)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(hold=60)  # hold > data length
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # No complete trades possible since hold > data
        assert result.trades == []

    @patch("backtester.engine.DataPipeline")
    def test_nan_entry_price_skipped(self, MockPipeline):
        """Trades with NaN entry price should be skipped."""
        dates = pd.date_range(start="2025-01-01", periods=100, freq="B")
        close = np.full(100, 100.0)
        close[5] = np.nan  # NaN price at potential entry
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(100, 1_000_000.0)},
            index=dates,
        )
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(hold=5)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        for trade in result.trades:
            assert not math.isnan(trade.entry_price)

    @patch("backtester.engine.DataPipeline")
    def test_zero_entry_price_skipped(self, MockPipeline):
        """Trades with zero entry price should be skipped."""
        dates = pd.date_range(start="2025-01-01", periods=100, freq="B")
        close = np.full(100, 100.0)
        close[5] = 0.0  # Zero price at potential entry
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(100, 1_000_000.0)},
            index=dates,
        )
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(hold=5)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        for trade in result.trades:
            assert trade.entry_price > 0

    def test_smallest_interval_ordering(self):
        """60m should be considered smaller than 90m."""
        conditions = [
            Condition("RSI", (), None, "<", 30.0, "90m"),
            Condition("RSI", (), None, "<", 30.0, "60m"),
        ]
        config = self._make_config(conditions=conditions)
        engine = BacktestEngine(conditions, config)
        assert engine._smallest_interval() == "60m"

    def test_smallest_interval_single(self):
        conditions = [Condition("RSI", (), None, "<", 30.0, "1wk")]
        config = self._make_config(conditions=conditions)
        engine = BacktestEngine(conditions, config)
        assert engine._smallest_interval() == "1wk"

    def test_check_condition_unknown_operator(self):
        """Unknown operator should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown operator"):
            BacktestEngine._check_condition(50.0, "!=" , 30.0)

    def test_check_condition_all_operators(self):
        assert BacktestEngine._check_condition(50.0, ">", 30.0) is True
        assert BacktestEngine._check_condition(50.0, "<", 30.0) is False
        assert BacktestEngine._check_condition(50.0, ">=", 50.0) is True
        assert BacktestEngine._check_condition(50.0, "<=", 50.0) is True
        assert BacktestEngine._check_condition(50.0, "==", 50.0) is True


# ===================================================================
# §14  Metrics Edge Case Tests
# ===================================================================

class TestMetricsEdgeCases:
    """Additional metrics edge case coverage."""

    def _make_trade(self, entry=100.0, exit=110.0, hold=5):
        return_pct = (exit - entry) / entry
        return Trade(
            ticker="AAPL",
            entry_date=pd.Timestamp("2025-01-01"),
            entry_price=entry,
            exit_date=pd.Timestamp("2025-01-01") + pd.Timedelta(days=hold),
            exit_price=exit,
            hold_bars=hold,
            return_pct=return_pct,
        )

    def test_max_drawdown_all_same(self):
        equity = pd.Series([100, 100, 100, 100])
        assert compute_max_drawdown(equity) == 0.0

    def test_max_drawdown_empty(self):
        assert compute_max_drawdown(pd.Series(dtype=float)) == 0.0

    def test_max_drawdown_single_point(self):
        assert compute_max_drawdown(pd.Series([100])) == 0.0

    def test_sharpe_empty(self):
        assert compute_sharpe_ratio(pd.Series(dtype=float)) == 0.0

    def test_sharpe_single_return(self):
        # Single return → std with ddof=1 is NaN → returns 0.0
        result = compute_sharpe_ratio(pd.Series([0.01]))
        assert result == 0.0

    def test_sharpe_zero_std(self):
        assert compute_sharpe_ratio(pd.Series([0.01, 0.01, 0.01])) == 0.0

    def test_sortino_empty(self):
        assert compute_sortino_ratio(pd.Series(dtype=float)) == 0.0

    def test_sortino_all_positive(self):
        # No downside → returns 0.0
        result = compute_sortino_ratio(pd.Series([0.01, 0.02, 0.03]))
        assert result == 0.0

    def test_total_return_compounding(self):
        """Two 10% wins compound to 21%."""
        trades = [
            self._make_trade(100.0, 110.0, 5),
            self._make_trade(110.0, 121.0, 5),
        ]
        result = compute_total_return(trades, 10_000.0)
        assert result == pytest.approx(0.21, abs=1e-3)

    def test_total_return_mixed(self):
        """Win + loss should compound correctly."""
        trades = [
            self._make_trade(100.0, 110.0, 5),  # +10%
            self._make_trade(110.0, 99.0, 5),    # -10%
        ]
        result = compute_total_return(trades, 10_000.0)

    def test_equity_curve_includes_daily_values(self):
        """Equity curve should have entries for every business day,
        not just trade exit dates."""
        from backtester.metrics import compute_equity_curve
        trades = [
            Trade("AAPL", pd.Timestamp("2025-01-06"), 100.0,
                  pd.Timestamp("2025-01-17"), 110.0, 10, 0.10),
            Trade("AAPL", pd.Timestamp("2025-02-03"), 110.0,
                  pd.Timestamp("2025-02-14"), 121.0, 10, 0.10),
        ]
        equity = compute_equity_curve(trades, 10_000.0)
        # Should have business days between entry and exit, not just 3 points
        assert len(equity) > 3
        # First value should be capital
        assert equity.iloc[0] == 10_000.0
        # Last value should reflect both compounding wins
        assert equity.iloc[-1] == pytest.approx(12_100.0, abs=1.0)

    def test_equity_curve_empty_trades(self):
        from backtester.metrics import compute_equity_curve
        equity = compute_equity_curve([], 10_000.0)
        assert equity.empty

    def test_sharpe_with_realistic_daily_returns(self):
        """Sharpe ratio with actual daily returns should be reasonable
        (not inflated by treating multi-day returns as daily)."""
        # 200 days of consistent ~0.05% daily returns (12.5% annual)
        daily = pd.Series(np.full(200, 0.0005))
        sharpe = compute_sharpe_ratio(daily)
        # With zero std (all same), Sharpe returns 0.0
        assert sharpe == 0.0

    def test_sharpe_with_varying_returns(self):
        """Sharpe with varying daily returns should be finite and
        not absurdly high (no longer inflated by sparse equity curve)."""
        np.random.seed(42)
        daily = pd.Series(np.random.normal(0.001, 0.01, 200))
        sharpe = compute_sharpe_ratio(daily)
        # 25% annual return, ~16% annual vol → Sharpe ~ 1.5
        assert 0.5 < sharpe < 3.0

    def test_sharpe_no_negative_returns(self):
        """All positive daily returns → Sortino should be 0 (no downside)."""
        daily = pd.Series([0.01, 0.02, 0.015, 0.005])
        assert compute_sortino_ratio(daily) == 0.0

    def test_sortino_with_mixed_returns(self):
        daily = pd.Series([0.01, -0.005, 0.008, -0.002, 0.003])
        result = compute_sortino_ratio(daily)
        assert math.isfinite(result)
        assert result > 0  # Positive mean, negative downside dev → positive

    def test_benchmark_metrics_empty_data(self):
        from backtester.metrics import compute_benchmark_metrics
        dates = pd.date_range("2025-01-01", periods=5, freq="B")
        df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=dates)
        # Request dates outside the data range → empty slice
        result = compute_benchmark_metrics(
            df, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")
        )
        assert result["total_return"] == 0.0

    def test_benchmark_metrics_single_point(self):
        from backtester.metrics import compute_benchmark_metrics
        dates = pd.date_range("2025-01-01", periods=1, freq="B")
        df = pd.DataFrame({"Close": [100.0]}, index=dates)
        result = compute_benchmark_metrics(
            df, pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-01")
        )
        assert result["total_return"] == 0.0

    def test_benchmark_metrics_valid(self):
        from backtester.metrics import compute_benchmark_metrics
        dates = pd.date_range("2025-01-01", periods=100, freq="B")
        close = np.linspace(100, 110, 100)
        df = pd.DataFrame({"Close": close}, index=dates)
        result = compute_benchmark_metrics(
            df, pd.Timestamp("2025-01-01"), pd.Timestamp("2025-05-20")
        )
        assert result["total_return"] > 0
        assert result["annualized_return"] > 0
        assert result["sharpe_ratio"] > 0


# ===================================================================
# §15  Reporting Edge Case Tests
# ===================================================================

class TestReportingEdgeCases:
    """Additional reporting edge case coverage."""

    def test_format_results_no_trades_per_ticker(self):
        result = BacktestResult(
            trades=[],
            metrics={"total_trades": 0, "total_return": 0.0},
            benchmark_metrics={},
            ticker_results={"AAPL": [], "MSFT": []},
            conditions=[],
            config={"tickers": ["AAPL", "MSFT"], "hold": 10,
                    "capital": 10_000.0, "benchmark": "SPY",
                    "years": 2, "stop_loss": None},
        )
        output = format_results(result)
        assert "AAPL" in output
        assert "MSFT" in output
        assert "No trades" in output

    def test_format_results_with_benchmark(self):
        result = BacktestResult(
            trades=[
                Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                      pd.Timestamp("2025-01-06"), 110.0, 5, 0.10),
            ],
            metrics={
                "total_trades": 1, "total_return": 0.10,
                "annualized_return": 0.50, "sharpe_ratio": 1.5,
                "sortino_ratio": 2.0, "max_drawdown": 0.05,
                "win_rate": 1.0, "profit_factor": float("inf"),
            },
            benchmark_metrics={
                "total_return": 0.05, "annualized_return": 0.25,
                "sharpe_ratio": 1.0, "max_drawdown": 0.03,
            },
            ticker_results={"AAPL": [
                Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                      pd.Timestamp("2025-01-06"), 110.0, 5, 0.10),
            ]},
            conditions=[Condition("RSI", (), None, "<", 30.0, "1d")],
            config={"tickers": ["AAPL"], "hold": 10, "capital": 10_000.0,
                    "benchmark": "SPY", "years": 2, "stop_loss": None},
        )
        output = format_results(result)
        assert "Benchmark" in output
        assert "vs Benchmark" in output
        assert "Return delta" in output
        assert "Sharpe delta" in output

    def test_sharpe_delta_sign_independent(self):
        """Sharpe delta sign should not depend on return delta sign."""
        result = BacktestResult(
            trades=[
                Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                      pd.Timestamp("2025-01-06"), 110.0, 5, 0.10),
            ],
            metrics={
                "total_trades": 1, "total_return": 0.10,
                "annualized_return": 0.50, "sharpe_ratio": 0.5,
                "sortino_ratio": 2.0, "max_drawdown": 0.05,
                "win_rate": 1.0, "profit_factor": float("inf"),
            },
            benchmark_metrics={
                "total_return": 0.05, "annualized_return": 0.25,
                "sharpe_ratio": 1.5, "max_drawdown": 0.03,
            },
            ticker_results={"AAPL": [
                Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                      pd.Timestamp("2025-01-06"), 110.0, 5, 0.10),
            ]},
            conditions=[],
            config={"tickers": ["AAPL"], "hold": 10, "capital": 10_000.0,
                    "benchmark": "SPY", "years": 2, "stop_loss": None},
        )
        output = format_results(result)
        # Return delta is positive (+5.0%) but Sharpe delta is negative (-1.00)
        assert "Return delta: +5.0%" in output
        assert "Sharpe delta: -1.00" in output

    def test_fmt_val_integer(self):
        from backtester.reporting import _fmt_val
        assert _fmt_val(100.0) == "100"

    def test_fmt_val_decimal(self):
        from backtester.reporting import _fmt_val
        assert _fmt_val(1.5) == "1.50"

    def test_ticker_total_return(self):
        from backtester.reporting import _ticker_total_return
        trades = [
            Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-01-06"), 110.0, 5, 0.10),
            Trade("AAPL", pd.Timestamp("2025-01-07"), 110.0,
                  pd.Timestamp("2025-01-12"), 121.0, 5, 0.10),
        ]
        result = _ticker_total_return(trades)
        # 1.10 * 1.10 = 1.21 → 21%
        assert result == pytest.approx(0.21, abs=1e-3)


# ===================================================================
# §16  Data Pipeline Edge Case Tests
# ===================================================================

class TestDataPipelineEdgeCases:
    """Additional data pipeline edge case coverage."""

    @pytest.fixture(autouse=True)
    def temp_cache(self, tmp_path):
        self.cache_dir = tmp_path / "cache"
        self.cache_dir.mkdir()
        self.pipeline = DataPipeline(cache_dir=self.cache_dir)

    def test_clear_cache(self):
        cache_path = self.pipeline._cache_path("AAPL", "1d")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.touch()
        assert cache_path.exists()
        count = self.pipeline.clear_cache()
        assert count == 1
        assert not cache_path.exists()

    def test_clear_cache_empty(self):
        count = self.pipeline.clear_cache()
        assert count == 0

    def test_corrupted_cache_falls_through(self):
        """Corrupted parquet should trigger re-download."""
        cache_path = self.pipeline._cache_path("AAPL", "1d")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("not a parquet file")
        mock_df = _make_df(rows=50)
        with patch.object(self.pipeline, "_download_batch",
                          return_value={"AAPL": mock_df}):
            result = self.pipeline.fetch(["AAPL"], "1d", 1)
        assert "AAPL" in result


# ==========================================================================
# §17 — Ticker validation in CLI parser
# ==========================================================================


class TestTickerValidation:
    """Tests for ticker format validation in parse_backtest_command."""

    def test_valid_single_ticker(self):
        cfg = parse_backtest_command(["AAPL", "RSI", "below", "30", "1d"])
        assert cfg["tickers"] == ["AAPL"]

    def test_valid_multi_ticker(self):
        cfg = parse_backtest_command(
            ["AAPL,MSFT,GOOG", "RSI", "below", "30", "1d"]
        )
        assert cfg["tickers"] == ["AAPL", "MSFT", "GOOG"]

    def test_valid_ticker_with_dot(self):
        """BRK.B is a valid ticker with a dot."""
        cfg = parse_backtest_command(
            ["BRK.B", "RSI", "below", "30", "1d"]
        )
        assert cfg["tickers"] == ["BRK.B"]

    def test_valid_ticker_with_hyphen(self):
        """BF-B is a valid ticker with a hyphen."""
        cfg = parse_backtest_command(
            ["BF-B", "RSI", "below", "30", "1d"]
        )
        assert cfg["tickers"] == ["BF-B"]

    def test_invalid_ticker_all_digits(self):
        with pytest.raises(ValueError, match="at least one letter"):
            parse_backtest_command(["123", "RSI", "below", "30", "1d"])

    def test_invalid_ticker_too_long(self):
        with pytest.raises(ValueError, match="Invalid ticker format"):
            parse_backtest_command(
                ["TOOLONGTICKER", "RSI", "below", "30", "1d"]
            )

    def test_invalid_ticker_special_chars(self):
        with pytest.raises(ValueError, match="Invalid ticker format"):
            parse_backtest_command(
                ["AA@L", "RSI", "below", "30", "1d"]
            )

    def test_invalid_ticker_empty_segment(self):
        """Trailing comma should be stripped, not create empty ticker."""
        cfg = parse_backtest_command(
            ["AAPL,", "RSI", "below", "30", "1d"]
        )
        assert cfg["tickers"] == ["AAPL"]

    def test_ticker_uppercased(self):
        """Tickers are uppercased automatically."""
        cfg = parse_backtest_command(
            ["aapl", "RSI", "below", "30", "1d"]
        )
        assert cfg["tickers"] == ["AAPL"]


# ==========================================================================
# §18 — Engine error handling
# ==========================================================================


class TestEngineErrorHandling:
    """Tests for engine error paths when tickers fail."""

    def _make_config(self, **overrides):
        from backtester.cli import Condition
        cond = Condition("RSI", (), None, "<", 30.0, "1d")
        cfg = {
            "conditions": [cond],
            "tickers": ["AAPL"],
            "years": 2,
            "hold": 10,
            "capital": 10000,
            "benchmark": "SPY",
            "stop_loss": None,
        }
        cfg.update(overrides)
        return cfg

    @patch("backtester.engine.DataPipeline")
    def test_empty_data_returns_empty_result(self, MockPipeline):
        """All tickers fail → returns empty BacktestResult."""
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert result.trades == []
        assert result.metrics == {}
        assert result.ticker_results == {}

    @patch("backtester.engine.DataPipeline")
    def test_partial_ticker_failure(self, MockPipeline):
        """Some tickers fail, some succeed → only valid ones traded."""
        dates = pd.date_range(start="2025-01-01", periods=200, freq="B")
        close = np.linspace(100, 110, 200)
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(200, 1_000_000.0)},
            index=dates,
        )
        mock_pipeline = MockPipeline.return_value
        # Only AAPL returns data, INVALID fails
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(tickers=["AAPL", "INVALID"])
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert "AAPL" in result.ticker_results
        assert "INVALID" not in result.ticker_results

    @patch("backtester.engine.DataPipeline")
    def test_all_tickers_fail_shows_error(self, MockPipeline, capsys):
        """All tickers fail → error message is printed."""
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config(tickers=["APPL", "MSFTT"])
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        captured = capsys.readouterr()
        assert "APPL" in captured.out
        assert "MSFTT" in captured.out
        assert "misspelled" in captured.out.lower()


# ==========================================================================
# §19 — DataPipeline error paths
# ==========================================================================


class TestDataPipelineErrors:
    """Tests for data pipeline error handling."""

    @patch("backtester.data_pipeline.yf.download")
    def test_download_batch_empty_raw(self, mock_download):
        """yf.download returns empty DataFrame → empty dict."""
        mock_download.return_value = pd.DataFrame()
        pipeline = DataPipeline()
        result = pipeline._download_batch(["AAPL"], "1d", 2)
        assert result == {}

    @patch("backtester.data_pipeline.yf.download")
    def test_download_batch_single_ticker_empty_after_dropna(
        self, mock_download
    ):
        """Single ticker with all-NaN rows → empty dict."""
        dates = pd.date_range(start="2025-01-01", periods=5, freq="B")
        raw = pd.DataFrame(
            {"Open": [np.nan] * 5, "High": [np.nan] * 5,
             "Low": [np.nan] * 5, "Close": [np.nan] * 5,
             "Volume": [np.nan] * 5},
            index=dates,
        )
        # yf.download returns MultiIndex columns
        raw.columns = pd.MultiIndex.from_product(
            [["AAPL"], raw.columns], names=["Ticker", "Price"]
        )
        mock_download.return_value = raw
        pipeline = DataPipeline()
        result = pipeline._download_batch(["AAPL"], "1d", 2)
        assert result == {}

    @patch("backtester.data_pipeline.yf.download")
    def test_download_batch_multi_ticker_partial_failure(
        self, mock_download
    ):
        """Multi-ticker: one succeeds, one has no data."""
        dates = pd.date_range(start="2025-01-01", periods=5, freq="B")
        cols = ["Open", "High", "Low", "Close", "Volume"]
        aapl_data = np.array([
            [100, 101, 99, 100, 1_000_000],
            [100, 101, 99, 100, 1_000_000],
            [100, 101, 99, 100, 1_000_000],
            [100, 101, 99, 100, 1_000_000],
            [100, 101, 99, 100, 1_000_000],
        ], dtype=float)
        bad_data = np.full((5, 5), np.nan)
        idx = pd.MultiIndex.from_product(
            [["AAPL", "BAD"], cols],
            names=["Ticker", "Price"],
        )
        raw = pd.DataFrame(
            np.hstack([aapl_data, bad_data]),
            columns=idx,
            index=dates,
        )
        mock_download.return_value = raw
        pipeline = DataPipeline()
        result = pipeline._download_batch(["AAPL", "BAD"], "1d", 2)
        assert "AAPL" in result
        assert "BAD" not in result

    @patch("backtester.data_pipeline.yf.download")
    def test_download_batch_exception_returns_empty(self, mock_download):
        """yf.download raises exception → empty dict."""
        mock_download.side_effect = Exception("network error")
        pipeline = DataPipeline()
        result = pipeline._download_batch(["AAPL"], "1d", 2)
        assert result == {}

    def test_save_cache_silently_skips_without_pyarrow(self, capsys):
        """_save_cache should not print a warning when pyarrow is
        missing — caching is optional."""
        pipeline = DataPipeline()
        mock_df = _make_df(rows=5)
        # This will fail (no pyarrow) but should be silent
        pipeline._save_cache("AAPL", "1d", mock_df)
        captured = capsys.readouterr()
        assert "Warning" not in captured.out
        assert "pyarrow" not in captured.out


# ==========================================================================
# §20 — Universe / Scanner integration tests
# ==========================================================================


class TestUniverseCLI:
    """Tests for --universe and --max-tickers CLI parsing."""

    def test_universe_option(self):
        cfg = parse_backtest_command(
            ["--universe", "sp500", "RSI", "below", "30", "1d"]
        )
        assert cfg["universe"] == "sp500"
        assert cfg["tickers"] == []

    def test_max_tickers_option(self):
        cfg = parse_backtest_command(
            ["--universe", "sp500", "--max-tickers", "50",
             "RSI", "below", "30", "1d"]
        )
        assert cfg["universe"] == "sp500"
        assert cfg["max_tickers"] == 50

    def test_universe_with_conditions_only(self):
        """--universe allows omitting explicit tickers."""
        cfg = parse_backtest_command(
            ["--universe", "sp500", "SMA", "50", "above",
             "200", "1d"]
        )
        assert cfg["universe"] == "sp500"
        assert cfg["tickers"] == []
        assert len(cfg["conditions"]) == 1

    def test_max_tickers_must_be_positive(self):
        with pytest.raises(ValueError, match="at least 1"):
            parse_backtest_command(
                ["--universe", "sp500", "--max-tickers", "0",
                 "RSI", "below", "30", "1d"]
            )

    def test_max_tickers_without_universe_still_parses(self):
        """max-tickers is stored but only used when --universe is set."""
        cfg = parse_backtest_command(
            ["AAPL", "RSI", "below", "30", "1d",
             "--max-tickers", "50"]
        )
        assert cfg["max_tickers"] == 50
        assert cfg["tickers"] == ["AAPL"]


class TestUniverseEngine:
    """Tests for universe resolution in the engine."""

    def _make_config(self, **overrides):
        from backtester.cli import Condition
        cond = Condition("RSI", (), None, "<", 30.0, "1d")
        cfg = {
            "conditions": [cond],
            "tickers": [],
            "years": 2,
            "hold": 10,
            "capital": 10000,
            "benchmark": "SPY",
            "stop_loss": None,
            "universe": None,
            "max_tickers": None,
        }
        cfg.update(overrides)
        return cfg

    @patch("backtester.engine.DataPipeline")
    @patch("backtester.universe.get_sp500_tickers")
    def test_universe_resolves_before_download(
        self, mock_sp500, MockPipeline
    ):
        """Engine resolves universe tickers before downloading."""
        mock_sp500.return_value = ["AAPL", "MSFT", "GOOG"]
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config(universe="sp500")
        engine = BacktestEngine(config["conditions"], config)
        engine.run()

        mock_sp500.assert_called_once()
        # fetch was called with resolved tickers
        call_args = mock_pipeline.fetch.call_args
        assert call_args[0][0] == ["AAPL", "MSFT", "GOOG"]

    @patch("backtester.engine.DataPipeline")
    @patch("backtester.universe.get_sp500_tickers")
    def test_max_tickers_limits_universe(
        self, mock_sp500, MockPipeline
    ):
        """max_tickers truncates the resolved universe."""
        mock_sp500.return_value = [
            "A", "B", "C", "D", "E", "F", "G", "H"
        ]
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config(
            universe="sp500", max_tickers=3
        )
        engine = BacktestEngine(config["conditions"], config)
        engine.run()

        call_args = mock_pipeline.fetch.call_args
        assert call_args[0][0] == ["A", "B", "C"]

    @patch("backtester.engine.DataPipeline")
    def test_no_universe_uses_explicit_tickers(self, MockPipeline):
        """Without --universe, explicit tickers are used."""
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config(tickers=["AAPL", "MSFT"])
        engine = BacktestEngine(config["conditions"], config)
        engine.run()

        call_args = mock_pipeline.fetch.call_args
        assert call_args[0][0] == ["AAPL", "MSFT"]


class TestReportingSummary:
    """Tests for summary mode in reporting."""

    def test_summary_mode_for_many_tickers(self):
        """20+ tickers with trades triggers summary mode."""
        from backtester.reporting import format_results
        trades = [
            Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-01-10"), 110.0, 10, 0.10),
        ]
        # Build 25 tickers with trades
        ticker_results = {}
        for i in range(25):
            ticker = f"T{i:03d}"
            ticker_results[ticker] = trades

        result = BacktestResult(
            trades=trades * 25,
            metrics={
                "total_trades": 25, "win_rate": 0.6,
                "total_return": 0.15, "annualized_return": 0.10,
                "sharpe_ratio": 1.2, "sortino_ratio": 1.8,
                "max_drawdown": 0.05, "profit_factor": 2.0,
            },
            benchmark_metrics={},
            ticker_results=ticker_results,
            conditions=[Condition("RSI", (), None, "<", 30.0, "1d")],
            config={"tickers": [], "hold": 10, "capital": 10_000.0,
                    "benchmark": "SPY", "years": 2,
                    "stop_loss": None, "universe": "sp500"},
        )
        output = format_results(result)
        assert "Universe Summary" in output
        assert "Top 5" in output
        assert "Bottom 5" in output

    def test_detail_mode_for_few_tickers(self):
        """< 20 tickers uses detail mode."""
        from backtester.reporting import format_results
        trades = [
            Trade("AAPL", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-01-10"), 110.0, 10, 0.10),
        ]
        result = BacktestResult(
            trades=trades,
            metrics={"total_trades": 1, "win_rate": 1.0,
                     "total_return": 0.10, "total_trades": 1},
            benchmark_metrics={},
            ticker_results={"AAPL": trades},
            conditions=[Condition("RSI", (), None, "<", 30.0, "1d")],
            config={"tickers": ["AAPL"], "hold": 10,
                    "capital": 10_000.0, "benchmark": "SPY",
                    "years": 2, "stop_loss": None},
        )
        output = format_results(result)
        assert "--- AAPL ---" in output
        assert "Universe Summary" not in output
