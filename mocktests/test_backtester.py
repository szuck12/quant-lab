"""Comprehensive tests for the backtester package.

Covers batch indicator computation, condition evaluation,
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
        # Clear in-memory cache between tests
        import backtester.data_pipeline as dp
        dp._memory_cache.clear()

    def test_cache_miss_fetches_data(self):
        mock_df = _make_df(rows=50)
        mock_data = {"AAPL": mock_df}
        with patch.object(self.pipeline, "_download_batch", return_value=mock_data):
            result = self.pipeline.fetch(["AAPL"], "1d", 1)
        assert "AAPL" in result
        assert len(result["AAPL"]) == 50

    def test_cache_hit_uses_parquet(self):
        mock_df = _make_df(rows=50)
        cache_path = self.pipeline._cache_path("AAPL", "1d", 1)
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
    def test_on_progress_receives_monotonic_values(self, MockPipeline):
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value

        def mock_fetch(tickers, interval, years, on_progress=None, **kwargs):
            if on_progress:
                for p in range(0, 101, 10):
                    on_progress(p)
            return {"AAPL": mock_df}

        mock_pipeline.fetch.side_effect = mock_fetch

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)

        progress_values: list[int] = []
        engine.run(on_progress=lambda p: progress_values.append(p))

        assert len(progress_values) > 0
        # Must be monotonically non-decreasing
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i - 1]
        # Must reach 100
        assert progress_values[-1] == 100

    @patch("backtester.engine.DataPipeline")
    def test_on_progress_no_jumps_over_10(self, MockPipeline):
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value

        def mock_fetch(tickers, interval, years, on_progress=None, **kwargs):
            if on_progress:
                for p in range(0, 101, 10):
                    on_progress(p)
            # Return enough tickers so each ticker is ≤5% of range
            return {f"T{i}": mock_df for i in range(10)}

        mock_pipeline.fetch.side_effect = mock_fetch

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)

        progress_values: list[int] = []
        engine.run(on_progress=lambda p: progress_values.append(p))

        # No single jump should exceed 10%
        for i in range(1, len(progress_values)):
            jump = progress_values[i] - progress_values[i - 1]
            assert jump <= 10, (
                f"Jump of {jump}% at index {i}: "
                f"{progress_values[i-1]} -> {progress_values[i]}"
            )

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
    def test_cooldown_after_exit(self, MockPipeline):
        """After a trade exits, the next entry must be at least
        hold bars later (cooldown prevents re-entry on next bar)."""
        # All RSI values below 30 → every bar is an entry signal
        dates = pd.date_range(start="2025-01-01", periods=50, freq="B")
        close = np.full(50, 100.0)
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(50, 1_000_000.0)},
            index=dates,
        )
        mock_df["rsi_14"] = 25.0  # Always triggers
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(hold=5)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # With cooldown, trades should not overlap or be back-to-back
        for i in range(len(result.trades) - 1):
            current_exit = result.trades[i].exit_date
            next_entry = result.trades[i + 1].entry_date
            gap = (next_entry - current_exit).days
            # Cooldown = hold bars (5 business days ≈ 7 calendar days)
            assert gap >= 5, (
                f"Trade {i+1} entered {gap} days after trade {i} "
                f"exited — expected >= 5 day gap"
            )

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
        assert result == pytest.approx(-0.1364, abs=0.001)

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
        """Equal-weight model: two 10% wins = 20% total."""
        trades = [
            self._make_trade(100.0, 110.0, 5),
            self._make_trade(110.0, 121.0, 5),
        ]
        result = compute_total_return(trades, 10_000.0)
        # Equal-weight: avg(0.10, 0.10) * 2 = 0.20
        assert result == pytest.approx(0.20, abs=1e-3)

    def test_total_return_mixed(self):
        """Win + loss: equal-weight model."""
        trades = [
            self._make_trade(100.0, 110.0, 5),  # +10%
            self._make_trade(110.0, 99.0, 5),    # -10%
        ]
        result = compute_total_return(trades, 10_000.0)
        # Equal-weight: avg(0.10, -0.10) * 2 = 0.0
        assert result == pytest.approx(0.0, abs=1e-3)

    def test_total_return_many_trades_no_overflow(self):
        """2528 trades at 6.7% average should not overflow."""
        # Simulate 2528 trades with 6.7% average return
        trades = [
            self._make_trade(100.0, 106.7, 10)
            for _ in range(2528)
        ]
        result = compute_total_return(trades, 10_000.0)
        # Equal-weight: 0.067 * 2528 = 169.4 (16,940%)
        # NOT (1.067)^2528 = 9.9e15
        assert result == pytest.approx(169.376, abs=0.1)
        assert result < 1000  # Sanity: should be < 100,000%

    def test_total_return_single_trade(self):
        """Single trade: equal-weight = raw return."""
        trades = [self._make_trade(100.0, 115.0, 10)]
        result = compute_total_return(trades, 10_000.0)
        assert result == pytest.approx(0.15, abs=1e-3)

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

class TestDataPipelineEdgeCases:
    """Additional data pipeline edge case coverage."""

    @pytest.fixture(autouse=True)
    def temp_cache(self, tmp_path):
        self.cache_dir = tmp_path / "cache"
        self.cache_dir.mkdir()
        self.pipeline = DataPipeline(cache_dir=self.cache_dir)
        # Clear in-memory cache between tests
        import backtester.data_pipeline as dp
        dp._memory_cache.clear()

    def test_clear_cache(self):
        cache_path = self.pipeline._cache_path("AAPL", "1d", 2)
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
        cache_path = self.pipeline._cache_path("AAPL", "1d", 2)
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


class TestEngineErrorHandling:
    """Tests for engine error paths when tickers fail."""

    def _make_config(self, **overrides):
        from backtester.engine import Condition
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
    def test_all_tickers_fail_shows_error(self, MockPipeline):
        """All tickers fail → returns empty BacktestResult."""
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {}

        config = self._make_config(tickers=["APPL", "MSFTT"])
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert result.trades == []
        assert result.metrics == {}
        assert result.ticker_results == {}


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
        pipeline._save_cache("AAPL", "1d", 2, mock_df)
        captured = capsys.readouterr()
        assert "Warning" not in captured.out
        assert "pyarrow" not in captured.out


# ==========================================================================
# §20 — Universe / Scanner integration tests
# ==========================================================================


class TestUniverseEngine:
    """Tests for universe resolution in the engine."""

    def _make_config(self, **overrides):
        from backtester.engine import Condition
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


class TestPositionSizing:
    """Tests for portfolio position sizing."""

    def _make_config(self, **overrides):
        config = {
            "tickers": ["AAPL"],
            "conditions": [Condition("RSI", (), None, "<", 50.0, "1d")],
            "hold": 10,
            "capital": 10_000.0,
            "benchmark": "SPY",
            "years": 2,
            "stop_loss": None,
            "position_size": 100,
            "position_size_base": "total",
        }
        config.update(overrides)
        return config

    @patch("backtester.engine.DataPipeline")
    def test_position_size_total_mode(self, MockPipeline):
        """10% of $10,000 = $1,000 per buy in total mode."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(position_size=10)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        for trade in result.trades:
            assert trade.invested == pytest.approx(1000.0, rel=0.01)

    @patch("backtester.engine.DataPipeline")
    def test_position_size_unallocated_mode(self, MockPipeline):
        """10% of unallocated cash per buy."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(
            position_size=10, position_size_base="unallocated"
        )
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        if result.trades:
            # First buy: 10% of $10,000 = $1,000
            assert result.trades[0].invested == pytest.approx(
                1000.0, rel=0.01
            )

    @patch("backtester.engine.DataPipeline")
    def test_repeat_ticker_skipped_when_at_target(self, MockPipeline):
        """If position >= target, no buy."""
        dates = pd.date_range(start="2025-01-01", periods=200, freq="B")
        close = np.full(200, 100.0)
        mock_df = pd.DataFrame(
            {"Open": close, "High": close + 1, "Low": close - 1,
             "Close": close, "Volume": np.full(200, 1_000_000.0)},
            index=dates,
        )
        mock_df["rsi_14"] = 30.0  # Always triggers
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        # 10% position size, 5-day hold, cooldown means trades are spaced
        config = self._make_config(
            position_size=10, hold=5
        )
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # With 10% position size on $10k, first buy = $1,000
        # After cooldown, second buy: target still $1,000,
        # but position already has $1,000 → skip
        # So only ~1 trade should execute
        assert len(result.trades) <= 3

    @patch("backtester.engine.DataPipeline")
    def test_cash_constraint(self, MockPipeline):
        """Buy only what cash allows."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        # $100 capital, 100% position size → first buy uses all $100
        config = self._make_config(capital=100, position_size=100)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        if result.trades:
            assert result.trades[0].invested <= 100.01

    @patch("backtester.engine.DataPipeline")
    def test_zero_position_size_no_trades(self, MockPipeline):
        """position_size=0 → no trades."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(position_size=0)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        assert result.trades == []

    @patch("backtester.engine.DataPipeline")
    def test_hundred_percent_uses_all_cash(self, MockPipeline):
        """position_size=100 → all cash per buy."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(position_size=100, capital=5000)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        if result.trades:
            assert result.trades[0].invested == pytest.approx(
                5000.0, rel=0.01
            )

    @patch("backtester.engine.DataPipeline")
    def test_multiple_tickers_share_cash(self, MockPipeline):
        """Cash pool shared across tickers, never goes negative."""
        mock_aapl = _make_df(rows=200)
        mock_aapl["rsi_14"] = 30.0
        mock_msft = _make_df(rows=200)
        mock_msft["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {
            "AAPL": mock_aapl, "MSFT": mock_msft
        }

        config = self._make_config(
            tickers=["AAPL", "MSFT"],
            position_size=50,
        )
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # Portfolio should never go negative
        assert result.metrics.get("cash_remaining", 0) >= 0
        assert result.metrics.get("positions_value", 0) >= 0

    @patch("backtester.engine.DataPipeline")
    def test_portfolio_tracks_positions(self, MockPipeline):
        """Portfolio state reflects buys and sells."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(position_size=10)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # After all trades, cash should be close to initial capital
        # (minus small floating point from shares * price rounding)
        assert result.metrics.get("cash_remaining", 0) >= 0

    @patch("backtester.engine.DataPipeline")
    def test_position_weighted_return(self, MockPipeline):
        """Return calculation with position sizing."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config(position_size=50)
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # Total return should be finite and reasonable
        assert math.isfinite(result.metrics.get("total_return", 0))

    @patch("backtester.engine.DataPipeline")
    def test_default_values_backward_compatible(self, MockPipeline):
        """Default position_size=100 preserves existing behavior."""
        mock_df = _make_df(rows=200)
        mock_df["rsi_14"] = 30.0
        mock_pipeline = MockPipeline.return_value
        mock_pipeline.fetch.return_value = {"AAPL": mock_df}

        config = self._make_config()
        engine = BacktestEngine(config["conditions"], config)
        result = engine.run()

        # Should produce valid results
        assert isinstance(result, BacktestResult)
        assert result.metrics.get("total_trades", 0) >= 0

    def test_portfolio_buy_basic(self):
        """Portfolio.buy adds shares and deducts cash."""
        from backtester.engine import Portfolio
        p = Portfolio(10000, 10, "total")
        success = p.buy("AAPL", 10, 100.0)
        assert success is True
        assert p.cash == pytest.approx(9000.0)
        assert p.get_invested("AAPL") == pytest.approx(1000.0)
        assert p.positions["AAPL"].shares == 10

    def test_portfolio_sell(self):
        """Portfolio.sell removes position and adds cash."""
        from backtester.engine import Portfolio
        p = Portfolio(10000, 10, "total")
        p.buy("AAPL", 10, 100.0)
        proceeds = p.sell("AAPL", 110.0)
        assert proceeds == pytest.approx(1100.0)
        assert p.cash == pytest.approx(10100.0)
        assert "AAPL" not in p.positions

    def test_portfolio_calculate_buy_at_target(self):
        """No buy when position equals target."""
        from backtester.engine import Portfolio
        p = Portfolio(10000, 10, "total")
        p.buy("AAPL", 10, 100.0)  # invested = $1000
        shares = p.calculate_buy_amount("AAPL", 100.0)
        assert shares == 0.0

    def test_portfolio_calculate_buy_below_target(self):
        """Buy up to target when below."""
        from backtester.engine import Portfolio
        p = Portfolio(10000, 10, "total")
        p.buy("AAPL", 5, 100.0)  # invested = $500, target = $1000
        shares = p.calculate_buy_amount("AAPL", 100.0)
        assert shares == pytest.approx(5.0)

    def test_portfolio_zero_position_size(self):
        """Zero position size → no buy."""
        from backtester.engine import Portfolio
        p = Portfolio(10000, 0, "total")
        shares = p.calculate_buy_amount("AAPL", 100.0)
        assert shares == 0.0


# ===================================================================
# §17  Comprehensive Output & Performance Tests
# ===================================================================


class TestMetricsAccuracy:
    """Tests for correct metric calculations."""

    def test_annualized_return_from_equity_curve(self):
        """Annualized return should match CAGR from equity curve final value."""
        from backtester.metrics import compute_metrics, compute_equity_curve
        # Two trades: 100% return each, 1 year apart
        trades = [
            Trade("A", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-06-30"), 200.0, 126, 1.0, 10, 1000),
            Trade("A", pd.Timestamp("2025-07-01"), 200.0,
                  pd.Timestamp("2025-12-31"), 400.0, 126, 1.0, 5, 1000),
        ]
        result = compute_metrics(trades, 1000.0)
        equity = compute_equity_curve(trades, 1000.0)
        expected_total = (equity.iloc[-1] / 1000.0) - 1.0
        assert result["total_return"] == pytest.approx(expected_total, abs=0.001)
        # Annualized should be ~300% (quadrupled in 1 year)
        assert result["annualized_return"] > 2.0

    def test_max_drawdown_is_negative(self):
        """Max drawdown should be a negative number."""
        from backtester.metrics import compute_max_drawdown
        equity = pd.Series([100, 110, 105, 90, 100])
        dd = compute_max_drawdown(equity)
        assert dd < 0
        assert dd == pytest.approx(-0.1818, abs=0.001)

    def test_max_drawdown_no_decline(self):
        """Max drawdown should be 0 for monotonic increase."""
        from backtester.metrics import compute_max_drawdown
        equity = pd.Series([100, 110, 120, 130])
        assert compute_max_drawdown(equity) == 0.0

    def test_total_return_matches_equity_curve(self):
        """Total return from metrics should match equity curve final value."""
        from backtester.metrics import compute_metrics, compute_equity_curve
        trades = [
            Trade("A", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-03-01"), 110.0, 42, 0.1, 10, 1000),
            Trade("B", pd.Timestamp("2025-02-01"), 50.0,
                  pd.Timestamp("2025-04-01"), 55.0, 42, 0.1, 10, 500),
        ]
        result = compute_metrics(trades, 1000.0)
        equity = compute_equity_curve(trades, 1000.0)
        expected = (equity.iloc[-1] / 1000.0) - 1.0
        assert result["total_return"] == pytest.approx(expected, abs=0.001)

    def test_years_uses_calendar_time(self):
        """Annualization should use calendar days, not sum of hold bars."""
        from backtester.metrics import compute_metrics
        # 3 trades, each held 10 bars, but spread over 2 years
        trades = [
            Trade("A", pd.Timestamp("2025-01-01"), 100.0,
                  pd.Timestamp("2025-01-10"), 110.0, 10, 0.1, 10, 1000),
            Trade("A", pd.Timestamp("2025-06-01"), 110.0,
                  pd.Timestamp("2025-06-10"), 121.0, 10, 0.1, 10, 1100),
            Trade("A", pd.Timestamp("2025-12-01"), 121.0,
                  pd.Timestamp("2025-12-10"), 133.1, 10, 0.1, 10, 1210),
        ]
        result = compute_metrics(trades, 1000.0)
        # ~33% total return over ~1 year (Jan 1 to Dec 10)
        # Annualized should be ~30%+, not deflated by summing 30 hold bars
        assert result["annualized_return"] > 0.2


class TestTradeOrdering:
    """Tests for trade log ordering by entry date."""

    def test_trades_sorted_by_entry_date(self):
        """All trades should be sorted by entry_date globally."""
        from backtester.engine import BacktestEngine, Condition, BacktestResult
        from unittest.mock import patch

        with patch("backtester.engine.DataPipeline") as MockPipeline:
            mock_pipeline = MockPipeline.return_value
            # Create data where tickers have trades at different times
            dates_a = pd.date_range("2025-03-01", periods=100, freq="B")
            dates_b = pd.date_range("2025-01-01", periods=100, freq="B")
            np.random.seed(42)
            close_a = 100 + np.cumsum(np.random.randn(100) * 2)
            close_b = 100 + np.cumsum(np.random.randn(100) * 2)

            df_a = pd.DataFrame({
                "Open": close_a - 1, "High": close_a + 1,
                "Low": close_a - 2, "Close": close_a,
                "Volume": [1_000_000] * 100,
            }, index=dates_a)
            df_a["RSI_14"] = 30.0  # trigger signal

            df_b = pd.DataFrame({
                "Open": close_b - 1, "High": close_b + 1,
                "Low": close_b - 2, "Close": close_b,
                "Volume": [1_000_000] * 100,
            }, index=dates_b)
            df_b["RSI_14"] = 30.0  # trigger signal

            mock_pipeline.fetch.return_value = {"BBB": df_b, "AAA": df_a}

            conditions = [Condition("RSI", (14,), None, "<", 50.0, "1d")]
            config = {
                "tickers": ["AAA", "BBB"], "hold": 5, "capital": 10000,
                "benchmark": "SPY", "years": 2, "stop_loss": None,
                "universe": None, "max_tickers": None,
                "position_size": 100, "position_size_base": "total",
            }
            engine = BacktestEngine(conditions, config)
            result = engine.run()

            # Trades should be sorted by entry_date, not by ticker
            if len(result.trades) > 1:
                for i in range(1, len(result.trades)):
                    assert result.trades[i].entry_date >= result.trades[i-1].entry_date


class TestVectorizedCCI:
    """Tests for vectorized CCI computation."""

    def test_cci_vectorized_matches_expected(self):
        """CCI should produce reasonable values."""
        from backtester.batch_indicators import compute_cci
        dates = pd.date_range("2025-01-01", periods=100, freq="B")
        np.random.seed(42)
        close = 100 + np.cumsum(np.random.randn(100) * 2)
        df = pd.DataFrame({
            "High": close + 1, "Low": close - 1, "Close": close,
        }, index=dates)
        cci = compute_cci(df, window=20)
        assert len(cci) == 100
        # CCI should have some non-NaN values after window period
        valid = cci.dropna()
        assert len(valid) > 50
        # CCI values should be finite
        assert all(np.isfinite(v) for v in valid)


class TestInMemoryCache:
    """Tests for in-memory caching."""

    def test_memory_cache_returns_same_data(self):
        """Second fetch should use memory cache."""
        import backtester.data_pipeline as dp
        dp._memory_cache.clear()

        mock_df = _make_df(rows=50)
        with patch.object(
            DataPipeline, "_download_batch", return_value={"AAPL": mock_df}
        ):
            pipeline = DataPipeline(cache_dir=Path("/tmp/test_cache"))
            result1 = pipeline.fetch(["AAPL"], "1d", 2)
            result2 = pipeline.fetch(["AAPL"], "1d", 2)

        # Both should return the same data
        assert "AAPL" in result1
        assert "AAPL" in result2
        pd.testing.assert_frame_equal(result1["AAPL"], result2["AAPL"])
        dp._memory_cache.clear()


class TestCacheKeyIncludesYears:
    """Tests for cache key including years parameter."""

    def test_cache_files_include_years(self):
        """Cache files should include years in filename."""
        pipeline = DataPipeline(cache_dir=Path("/tmp/test_cache2"))
        path_2yr = pipeline._cache_path("AAPL", "1d", 2)
        path_5yr = pipeline._cache_path("AAPL", "1d", 5)
        assert "2" in path_2yr.name
        assert "5" in path_5yr.name
        assert path_2yr != path_5yr


# ===================================================================
# §21  Equity Curve Weighting & Portfolio Cash Safety
# ===================================================================


def _weighted_trade(
    entry: float,
    exit_price: float,
    invested: float,
    entry_date: str = "2025-01-01",
    hold: int = 10,
    ticker: str = "AAPL",
) -> Trade:
    """Build a Trade with position-sizing data (shares + invested)."""
    return Trade(
        ticker=ticker,
        entry_date=pd.Timestamp(entry_date),
        entry_price=entry,
        exit_date=pd.Timestamp(entry_date) + pd.Timedelta(days=hold),
        exit_price=exit_price,
        hold_bars=hold,
        return_pct=(exit_price - entry) / entry,
        shares=invested / entry,
        invested=invested,
    )


class TestEquityCurveWeighting:
    """Equity curve must weight returns by capital actually invested.

    Regression tests for the bug where the equity curve compounded
    each trade's full return on total equity, inflating returns when
    trades used only part of the capital or overlapped.
    """

    def test_partial_investment_not_inflated(self):
        """A trade using 50% of capital with +10% gains 5% of equity."""
        from backtester.metrics import compute_equity_curve
        trades = [_weighted_trade(100.0, 110.0, invested=5000.0)]
        equity = compute_equity_curve(trades, 10_000.0)
        assert equity.iloc[-1] == pytest.approx(10_500.0, abs=0.01)

    def test_full_investment_applies_full_return(self):
        """A trade using 100% of capital applies its full return."""
        from backtester.metrics import compute_equity_curve
        trades = [_weighted_trade(100.0, 110.0, invested=10_000.0)]
        equity = compute_equity_curve(trades, 10_000.0)
        assert equity.iloc[-1] == pytest.approx(11_000.0, abs=0.01)

    def test_overlapping_trades_not_double_counted(self):
        """Two overlapping trades each using 50% must total 10%, not 21%."""
        from backtester.metrics import compute_equity_curve
        trades = [
            _weighted_trade(
                100.0, 110.0, invested=5000.0, entry_date="2025-01-01"
            ),
            _weighted_trade(
                100.0, 110.0, invested=5000.0, entry_date="2025-01-06"
            ),
        ]
        equity = compute_equity_curve(trades, 10_000.0)
        # 10000 + 500 + 500 = 11000, NOT 12100
        assert equity.iloc[-1] == pytest.approx(11_000.0, abs=0.01)

    def test_many_partial_trades_linear_growth(self):
        """50 trades each investing 20% at +10% → +100%, not compounded."""
        from backtester.metrics import compute_equity_curve
        trades = [
            _weighted_trade(
                100.0,
                110.0,
                invested=2000.0,
                entry_date=f"2025-{1 + (i // 28):02d}-"
                f"{1 + (i % 28):02d}",
                hold=3,
            )
            for i in range(50)
        ]
        equity = compute_equity_curve(trades, 10_000.0)
        # Each trade gains $200; 50 trades → $10,000 gain → $20,000
        assert equity.iloc[-1] == pytest.approx(20_000.0, abs=5.0)

    def test_losing_partial_trade_reduces_correctly(self):
        """A trade using 50% of capital with -10% loses 5% of equity."""
        from backtester.metrics import compute_equity_curve
        trades = [_weighted_trade(100.0, 90.0, invested=5000.0)]
        equity = compute_equity_curve(trades, 10_000.0)
        assert equity.iloc[-1] == pytest.approx(9_500.0, abs=0.01)

    def test_final_value_exact_with_out_of_order_exits(self):
        """Final equity must include every trade even if exits are out
        of entry order."""
        from backtester.metrics import compute_equity_curve
        # Trade A enters first but exits last
        trade_a = _weighted_trade(
            100.0, 110.0, invested=5000.0, entry_date="2025-01-01", hold=120
        )
        # Trade B enters later but exits earlier
        trade_b = _weighted_trade(
            100.0, 110.0, invested=5000.0, entry_date="2025-01-02", hold=3
        )
        equity = compute_equity_curve([trade_a, trade_b], 10_000.0)
        assert equity.iloc[-1] == pytest.approx(11_000.0, abs=0.01)

    def test_legacy_trades_still_compound(self):
        """Trades without position data keep the previous behavior."""
        from backtester.metrics import compute_equity_curve
        trades = [
            Trade("AAPL", pd.Timestamp("2025-01-06"), 100.0,
                  pd.Timestamp("2025-01-17"), 110.0, 10, 0.10),
            Trade("AAPL", pd.Timestamp("2025-02-03"), 110.0,
                  pd.Timestamp("2025-02-14"), 121.0, 10, 0.10),
        ]
        equity = compute_equity_curve(trades, 10_000.0)
        assert equity.iloc[-1] == pytest.approx(12_100.0, abs=1.0)

    def test_equity_starts_at_capital(self):
        """The curve begins flat at the starting capital."""
        from backtester.metrics import compute_equity_curve
        trades = [_weighted_trade(100.0, 110.0, invested=5000.0)]
        equity = compute_equity_curve(trades, 10_000.0)
        assert equity.iloc[0] == 10_000.0

    def test_total_return_matches_weighted_equity(self):
        """compute_metrics total_return must match the weighted curve."""
        from backtester.metrics import compute_metrics, compute_equity_curve
        trades = [
            _weighted_trade(100.0, 110.0, invested=5000.0),
            _weighted_trade(100.0, 110.0, invested=5000.0,
                            entry_date="2025-01-06"),
        ]
        metrics = compute_metrics(trades, 10_000.0)
        equity = compute_equity_curve(trades, 10_000.0)
        expected = (equity.iloc[-1] / 10_000.0) - 1.0
        assert metrics["total_return"] == pytest.approx(expected, abs=1e-6)
        assert metrics["total_return"] == pytest.approx(0.10, abs=1e-6)

    def test_total_return_matches_dollar_gains(self):
        """total_return must equal summed dollar gains over capital."""
        from backtester.metrics import compute_metrics
        trades = [
            _weighted_trade(100.0, 110.0, invested=4000.0),
            _weighted_trade(50.0, 45.0, invested=3000.0,
                            entry_date="2025-01-06"),
        ]
        metrics = compute_metrics(trades, 10_000.0)
        expected = (400.0 - 300.0) / 10_000.0
        assert metrics["total_return"] == pytest.approx(expected, abs=1e-6)


class TestPortfolioCashSafety:
    """The portfolio must never spend more cash than it has."""

    def test_buy_beyond_cash_is_rejected(self):
        from backtester.engine import Portfolio
        p = Portfolio(capital=10_000.0, position_size=100,
                      position_size_base="total")
        # Try to buy $15,000 worth with only $10,000 cash
        ok = p.buy("AAPL", shares=150, price=100.0)
        assert ok is False
        assert p.cash == 10_000.0
        assert "AAPL" not in p.positions

    def test_calculate_buy_amount_capped_by_cash(self):
        from backtester.engine import Portfolio
        p = Portfolio(capital=10_000.0, position_size=100,
                      position_size_base="total")
        # Deploy $9,000 first
        p.buy("AAPL", shares=90, price=100.0)
        assert p.cash == pytest.approx(1_000.0)
        # Second ticker wants $10,000 but only $1,000 remains
        shares = p.calculate_buy_amount("MSFT", 100.0)
        assert shares == pytest.approx(10.0)  # $1,000 / $100

    def test_no_buy_when_cash_exhausted(self):
        from backtester.engine import Portfolio
        p = Portfolio(capital=10_000.0, position_size=100,
                      position_size_base="total")
        p.buy("AAPL", shares=100, price=100.0)  # all cash used
        assert p.cash == pytest.approx(0.0)
        shares = p.calculate_buy_amount("MSFT", 100.0)
        assert shares == 0.0

    def test_cash_restored_on_sell(self):
        from backtester.engine import Portfolio
        p = Portfolio(capital=10_000.0, position_size=100,
                      position_size_base="total")
        p.buy("AAPL", shares=50, price=100.0)  # spend $5,000
        assert p.cash == pytest.approx(5_000.0)
        proceeds = p.sell("AAPL", 110.0)  # regain $5,500
        assert proceeds == pytest.approx(5_500.0)
        assert p.cash == pytest.approx(10_500.0)

    def test_accounting_identity(self):
        """cash + invested + realized P&L == initial capital."""
        from backtester.engine import Portfolio
        p = Portfolio(capital=10_000.0, position_size=50,
                      position_size_base="total")
        p.buy("AAPL", shares=50, price=100.0)  # invest $5,000
        p.sell("AAPL", 110.0)                  # +$500 realized
        p.buy("MSFT", shares=25, price=100.0)  # invest $2,500
        invested_now = p.positions["MSFT"].shares * 100.0
        total = p.cash + invested_now
        # cash should reflect the $500 realized gain
        assert total == pytest.approx(10_500.0, abs=0.01)

    def test_engine_never_overspends(self):
        """End-to-end: engine portfolio cash never goes negative."""
        with patch("backtester.engine.DataPipeline") as MockPipeline:
            dates = pd.date_range("2025-01-01", periods=100, freq="B")
            close = np.linspace(100, 120, 100)
            df = pd.DataFrame(
                {"Open": close, "High": close + 1, "Low": close - 1,
                 "Close": close, "Volume": np.full(100, 1_000_000.0)},
                index=dates,
            )
            df["RSI_14"] = 30.0  # always signals
            MockPipeline.return_value.fetch.return_value = {
                "AAA": df, "BBB": df.copy(), "CCC": df.copy(),
            }

            conditions = [Condition("RSI", (14,), None, "<", 50.0, "1d")]
            config = {
                "tickers": ["AAA", "BBB", "CCC"], "hold": 5,
                "capital": 10_000.0, "benchmark": "SPY", "years": 2,
                "stop_loss": None, "universe": None, "max_tickers": None,
                "position_size": 100, "position_size_base": "total",
            }
            engine = BacktestEngine(conditions, config)
            result = engine.run()

            cash = result.metrics["cash_remaining"]
            positions = result.metrics["positions_value"]
            assert cash >= 0.0
            # Total deployed value can never exceed capital + gains,
            # but at minimum cash + open positions must be sane
            assert cash + positions >= 0.0


class TestEquityCurveAdditivePnl:
    """Equity must track realized dollar P&L exactly, even when
    cumulative losses push equity below the amount later invested
    (the case that broke the capped-fraction formulation)."""

    def test_large_loss_then_large_investment(self):
        from backtester.metrics import compute_equity_curve
        # Trade A: invests full $10,000 and loses 50% → equity $5,000
        trade_a = _weighted_trade(
            100.0, 50.0, invested=10_000.0, entry_date="2025-01-01", hold=10
        )
        # Trade B: invests $10,000 and gains 10% → +$1,000
        trade_b = _weighted_trade(
            100.0, 110.0, invested=10_000.0, entry_date="2025-02-01", hold=10
        )
        equity = compute_equity_curve([trade_a, trade_b], 10_000.0)
        # 10,000 - 5,000 + 1,000 = 6,000 (not 5,500)
        assert equity.iloc[-1] == pytest.approx(6_000.0, abs=0.01)

    def test_final_equity_equals_cash_for_closed_trades(self):
        """When all positions are closed, the equity curve's final
        value equals capital plus summed dollar gains."""
        from backtester.metrics import compute_equity_curve
        trades = [
            _weighted_trade(100.0, 120.0, invested=3_000.0),
            _weighted_trade(50.0, 40.0, invested=2_000.0,
                            entry_date="2025-01-05"),
            _weighted_trade(200.0, 210.0, invested=5_000.0,
                            entry_date="2025-01-10"),
        ]
        equity = compute_equity_curve(trades, 10_000.0)
        dollar_gains = sum(
            t.shares * (t.exit_price - t.entry_price) for t in trades
        )
        assert equity.iloc[-1] == pytest.approx(
            10_000.0 + dollar_gains, abs=0.01
        )


# ===================================================================
# §22  Chronological Portfolio Simulation (day-by-day, cash-limited)
# ===================================================================

from unittest.mock import patch as _patch  # noqa: E402


def _sim_df(dates, prices):
    prices = np.asarray(prices, dtype=float)
    return pd.DataFrame(
        {
            "Open": prices,
            "High": prices + 1.0,
            "Low": prices - 1.0,
            "Close": prices,
            "Volume": np.full(len(prices), 1_000_000.0),
        },
        index=dates,
    )


def _run_sim(
    tickers=("AAA",),
    position_size=100,
    base="total",
    hold=5,
    stop_loss=None,
    n=120,
    prices=None,
    benchmark_prices=None,
    capital=10_000.0,
    condition=None,
):
    """Run a deterministic backtest with a mocked pipeline."""
    dates = pd.date_range("2023-01-02", periods=n, freq="B")
    if prices is None:
        prices = np.linspace(100.0, 110.0, n)
    strategy_df = _sim_df(dates, prices)
    if benchmark_prices is None:
        benchmark_prices = np.linspace(100.0, 105.0, n)
    bench_df = _sim_df(dates, benchmark_prices)
    tickers = list(tickers)

    def fetch(req_tickers, interval, years, on_progress=None, **kwargs):
        if list(req_tickers) == ["SPY"]:
            return {"SPY": bench_df}
        return {t: strategy_df.copy() for t in req_tickers}

    with _patch("backtester.engine.DataPipeline") as MockPipeline:
        MockPipeline.return_value.fetch.side_effect = fetch
        conds = [
            condition
            or Condition("SMA", (2,), None, ">", 0.0, "1d")
        ]
        config = {
            "tickers": tickers,
            "hold": hold,
            "capital": capital,
            "benchmark": "SPY",
            "years": 1,
            "stop_loss": stop_loss,
            "universe": None,
            "max_tickers": None,
            "position_size": position_size,
            "position_size_base": base,
        }
        return BacktestEngine(conds, config).run()


def _max_concurrent_invested(trades):
    """Peak dollars deployed across simultaneously open positions."""
    events = []
    for t in trades:
        events.append((t.entry_date, 1, t.invested))
        events.append((t.exit_date, -1, t.invested))
    # Process exits before entries on the same date
    events.sort(key=lambda e: (e[0], e[1]))
    cur = 0.0
    peak = 0.0
    for _, sign, inv in events:
        cur += sign * inv
        peak = max(peak, cur)
    return peak


class TestChronologicalSimulation:
    """The engine must simulate all tickers on one shared timeline."""

    def test_never_over_allocates_capital(self):
        result = _run_sim(
            tickers=["AAA", "BBB", "CCC", "DDD"],
            position_size=50,
            base="total",
        )
        peak = _max_concurrent_invested(result.trades)
        assert peak <= 10_000.0 + 1e-6

    def test_cash_never_negative(self):
        result = _run_sim(
            tickers=["AAA", "BBB", "CCC"], position_size=100
        )
        assert result.metrics["cash_remaining"] >= 0.0

    def test_no_cross_ticker_time_reuse(self):
        """Many tickers must not multiply returns via duplicated time."""
        result = _run_sim(
            tickers=["AAA", "BBB", "CCC", "DDD", "EEE"],
            position_size=100,
            base="total",
        )
        # Concurrent invested capital can never exceed portfolio equity
        peak = _max_concurrent_invested(result.trades)
        assert peak <= result.equity_curve.max() + 1e-6
        # Total return must equal the final equity-based return
        eq = result.equity_curve
        expected = (eq.iloc[-1] / 10_000.0) - 1.0
        assert result.metrics["total_return"] == pytest.approx(
            expected, abs=1e-9
        )

    def test_alphabetical_allocation_priority(self):
        """On the first signal day, only the first alphabetical ticker
        is funded when position_size is 100%."""
        result = _run_sim(
            tickers=["ZZZ", "AAA", "MMM"],
            position_size=100,
            base="total",
        )
        assert result.trades
        first_date = min(t.entry_date for t in result.trades)
        first_day = {
            t.ticker
            for t in result.trades
            if t.entry_date == first_date and t.invested > 0
        }
        assert first_day == {"AAA"}

    def test_same_day_entries_stop_when_cash_exhausted(self):
        result = _run_sim(
            tickers=["AAA", "BBB"],
            position_size=100,
            base="total",
        )
        if result.trades:
            first_date = min(t.entry_date for t in result.trades)
            same_day = [
                t for t in result.trades if t.entry_date == first_date
            ]
            assert sum(t.invested for t in same_day) <= 10_000.0 + 1e-6

    def test_one_position_per_ticker(self):
        """A ticker is not pyramided — only one open position at a time."""
        result = _run_sim(tickers=["AAA"], position_size=100)
        peak = _max_concurrent_invested(result.trades)
        per_position = 10_000.0
        assert peak <= per_position + 1e-6

    def test_open_positions_marked_to_market(self):
        result = _run_sim(tickers=["AAA"], position_size=50)
        eq = result.equity_curve
        end_value = result.metrics["cash_remaining"] + result.metrics[
            "positions_value"
        ]
        assert eq.iloc[-1] == pytest.approx(end_value, abs=0.02)

    def test_equity_starts_at_capital(self):
        result = _run_sim(tickers=["AAA", "BBB"])
        assert result.equity_curve.iloc[0] == pytest.approx(
            10_000.0, abs=0.01
        )

    def test_mark_to_market_updates_between_trades(self):
        """Equity must change on days a position is open, not only on
        exit dates (true mark-to-market)."""
        result = _run_sim(tickers=["AAA"], hold=20)
        equity = result.equity_curve
        nonzero_changes = int((equity.diff().abs() > 1e-9).sum())
        assert nonzero_changes > len(result.trades)
        assert result.metrics["positions_value"] == 0.0
        total = (
            result.metrics["cash_remaining"]
            + result.metrics["positions_value"]
        )
        assert total == pytest.approx(equity.iloc[-1], abs=0.02)

    def test_hold_period_respected(self):
        result = _run_sim(tickers=["AAA"], hold=5)
        for t in result.trades:
            assert t.hold_bars >= 1
            assert t.hold_bars <= 5

    def test_stop_loss_triggers_early_exit(self):
        # Price collapses from bar 6 onward → stop-loss should exit early
        n = 60
        prices = np.concatenate(
            [np.linspace(100, 101, 6), np.linspace(100, 50, n - 6)]
        )
        result = _run_sim(
            tickers=["AAA"],
            hold=30,
            stop_loss=5.0,
            n=n,
            prices=prices,
        )
        assert result.trades
        early = [t for t in result.trades if t.hold_bars < 30]
        assert early, "stop-loss should have exited before hold period"
        for t in early:
            assert t.return_pct <= -0.05 + 0.01

    def test_cooldown_prevents_immediate_reentry(self):
        result = _run_sim(tickers=["AAA"], hold=5)
        trades = sorted(result.trades, key=lambda t: t.entry_date)
        for prev, nxt in zip(trades, trades[1:]):
            gap = nxt.entry_date - prev.exit_date
            assert gap.days > 0

    def test_benchmark_fetched_at_daily_interval(self):
        with _patch("backtester.engine.DataPipeline") as MockPipeline:
            seen = {}

            def fetch(req_tickers, interval, years,
                      on_progress=None, **kwargs):
                seen["bench_interval"] = interval
                return {t: _sim_df(
                    pd.date_range("2023-01-02", periods=60, freq="B"),
                    np.linspace(100, 105, 60),
                ) for t in req_tickers}

            MockPipeline.return_value.fetch.side_effect = fetch
            conds = [Condition("SMA", (2,), None, ">", 0.0, "1d")]
            config = {
                "tickers": ["AAA"], "hold": 5, "capital": 10_000.0,
                "benchmark": "SPY", "years": 1, "stop_loss": None,
                "universe": None, "max_tickers": None,
                "position_size": 100, "position_size_base": "total",
            }
            BacktestEngine(conds, config).run()
            assert seen["bench_interval"] == "1d"

    def test_metrics_cash_positions_identity(self):
        result = _run_sim(
            tickers=["AAA", "BBB", "CCC"],
            position_size=30,
            hold=10,
        )
        total = (
            result.metrics["cash_remaining"]
            + result.metrics["positions_value"]
        )
        assert total == pytest.approx(
            result.equity_curve.iloc[-1], abs=0.02
        )


# ===================================================================
# §23  Metric correctness (Sharpe, Sortino, profit factor, drawdown)
# ===================================================================


def _mk_trade(entry, exit_price, invested=1000.0, shares=None,
              entry_date="2023-01-02", hold=10, ret=None):
    shares = invested / entry if shares is None else shares
    return Trade(
        ticker="T",
        entry_date=pd.Timestamp(entry_date),
        entry_price=entry,
        exit_date=pd.Timestamp(entry_date) + pd.Timedelta(days=hold),
        exit_price=exit_price,
        hold_bars=hold,
        return_pct=(exit_price - entry) / entry if ret is None else ret,
        shares=shares,
        invested=invested,
    )


class TestMetricCorrectness:
    def test_sharpe_matches_formula(self):
        r = pd.Series([0.01, -0.005, 0.008, 0.002, -0.001])
        expected = r.mean() / r.std() * np.sqrt(252)
        assert compute_sharpe_ratio(r) == pytest.approx(expected)

    def test_sharpe_zero_variance_returns_zero(self):
        r = pd.Series([0.001, 0.001, 0.001, 0.001])
        assert compute_sharpe_ratio(r) == 0.0

    def test_sortino_uses_downside_deviation(self):
        r = pd.Series([0.01, -0.02, 0.03, -0.01])
        downside = np.sqrt(np.mean(np.minimum(r, 0.0) ** 2))
        expected = r.mean() / downside * np.sqrt(252)
        assert compute_sortino_ratio(r) == pytest.approx(expected)

    def test_sortino_all_positive_returns_zero(self):
        r = pd.Series([0.01, 0.02, 0.03])
        assert compute_sortino_ratio(r) == 0.0

    def test_profit_factor_is_dollar_weighted(self):
        trades = [
            _mk_trade(100.0, 110.0, invested=1000.0),   # +100
            _mk_trade(100.0, 90.0, invested=100.0),     # -10
            _mk_trade(100.0, 105.0, invested=2000.0),   # +100
        ]
        m = compute_metrics(trades, 10_000.0)
        assert m["profit_factor"] == pytest.approx(200.0 / 10.0)

    def test_profit_factor_no_losses(self):
        trades = [_mk_trade(100.0, 110.0, invested=1000.0)]
        m = compute_metrics(trades, 10_000.0)
        assert m["profit_factor"] == 0.0

    def test_win_rate_excludes_zero_return_trades(self):
        trades = [
            _mk_trade(100.0, 110.0, invested=1000.0),
            _mk_trade(100.0, 100.0, invested=1000.0, ret=0.0),
            _mk_trade(100.0, 90.0, invested=1000.0),
        ]
        m = compute_metrics(trades, 10_000.0)
        assert m["winning_trades"] == 1
        assert m["losing_trades"] == 1
        assert m["win_rate"] == pytest.approx(1.0 / 3.0)

    def test_max_drawdown_uses_supplied_curve(self):
        idx = pd.date_range("2023-01-02", periods=4, freq="B")
        equity = pd.Series([10_000.0, 11_000.0, 9_000.0, 9_500.0],
                           index=idx)
        trades = [_mk_trade(100.0, 110.0)]
        m = compute_metrics(trades, 10_000.0, equity)
        assert m["max_drawdown"] == pytest.approx(
            (9_000.0 - 11_000.0) / 11_000.0
        )

    def test_total_return_from_supplied_curve(self):
        idx = pd.date_range("2023-01-02", periods=3, freq="B")
        equity = pd.Series([10_000.0, 10_500.0, 12_000.0], index=idx)
        trades = [_mk_trade(100.0, 120.0)]
        m = compute_metrics(trades, 10_000.0, equity)
        assert m["total_return"] == pytest.approx(0.20)

    def test_annualized_floored_at_one_month(self):
        idx = pd.date_range("2023-01-02", periods=2, freq="B")
        equity = pd.Series([10_000.0, 10_100.0], index=idx)
        trades = [_mk_trade(100.0, 101.0)]
        m = compute_metrics(trades, 10_000.0, equity)
        # 1% over one day, floored to 1/12 year → 1.01^12 - 1
        assert m["annualized_return"] == pytest.approx(
            1.01 ** 12 - 1.0, rel=1e-3
        )

    def test_metrics_accepts_equity_curve(self):
        idx = pd.date_range("2023-01-02", periods=10, freq="B")
        equity = pd.Series(
            np.linspace(10_000.0, 11_000.0, 10), index=idx
        )
        trades = [_mk_trade(100.0, 110.0)]
        m = compute_metrics(trades, 10_000.0, equity)
        assert m["total_return"] == pytest.approx(0.10)

    def test_empty_trades_zero_metrics(self):
        m = compute_metrics([], 10_000.0)
        assert m["total_return"] == 0.0
        assert m["sharpe_ratio"] == 0.0
        assert m["profit_factor"] == 0.0

    def test_benchmark_metrics_include_sortino(self):
        from backtester.metrics import compute_benchmark_metrics
        idx = pd.date_range("2023-01-02", periods=60, freq="B")
        prices = 100 + np.cumsum(np.random.RandomState(0).randn(60) * 0.5)
        df = pd.DataFrame({"Close": prices}, index=idx)
        bm = compute_benchmark_metrics(df, idx[0], idx[-1])
        assert "sortino_ratio" in bm
        assert np.isfinite(bm["sortino_ratio"])

    def test_benchmark_uses_adjusted_close(self):
        from backtester.metrics import compute_benchmark_metrics
        idx = pd.date_range("2023-01-02", periods=3, freq="B")
        df = pd.DataFrame({"Close": [100.0, 110.0, 120.0]}, index=idx)
        bm = compute_benchmark_metrics(df, idx[0], idx[-1])
        assert bm["total_return"] == pytest.approx(0.20)


# ===================================================================
# §24  Equity curve API: alignment and downsampling
# ===================================================================


class TestEquityCurveAPI:
    def _result(self, n=500):
        from backtester.engine import BacktestResult
        idx = pd.date_range("2020-01-01", periods=n, freq="B")
        strat = pd.Series(np.linspace(10_000, 12_000, n), index=idx)
        bench = pd.DataFrame(
            {"Close": np.linspace(100.0, 130.0, n)}, index=idx
        )
        return BacktestResult(
            trades=[],
            metrics={},
            benchmark_metrics={},
            ticker_results={},
            conditions=[],
            config={},
            equity_curve=strat,
            benchmark_df=bench,
        )

    def _req(self):
        from api.schemas import BacktestRequest
        return BacktestRequest(
            conditions=[
                {
                    "indicator": "SMA",
                    "operator": ">",
                    "value": 0.0,
                    "interval": "1d",
                }
            ]
        )

    def test_downsampled_to_max_points(self):
        from api.routes import MAX_EQUITY_POINTS, _build_equity_curve
        points = _build_equity_curve(self._result(500), self._req())
        assert 0 < len(points) <= MAX_EQUITY_POINTS

    def test_starts_at_capital_for_both(self):
        from api.routes import _build_equity_curve
        points = _build_equity_curve(self._result(500), self._req())
        assert points[0].strategy == pytest.approx(10_000.0, abs=0.5)
        assert points[0].benchmark == pytest.approx(10_000.0, abs=0.5)

    def test_benchmark_baseline_aligned(self):
        from api.routes import _build_equity_curve
        points = _build_equity_curve(self._result(200), self._req())
        assert points[-1].benchmark > points[0].benchmark
        # benchmark moves in step with its underlying price series
        assert points[-1].benchmark == pytest.approx(13_000.0, rel=0.05)

    def test_empty_strategy_returns_empty(self):
        from api.routes import _build_equity_curve
        from backtester.engine import BacktestResult
        result = BacktestResult(
            trades=[], metrics={}, benchmark_metrics={},
            ticker_results={}, conditions=[], config={},
            equity_curve=pd.Series(dtype=float),
            benchmark_df=pd.DataFrame(),
        )
        assert _build_equity_curve(result, self._req()) == []

    def test_short_series_not_padded(self):
        from api.routes import _build_equity_curve
        points = _build_equity_curve(self._result(20), self._req())
        assert len(points) == 20
