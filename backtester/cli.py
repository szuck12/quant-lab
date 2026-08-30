# backtester/cli.py
"""BACKTEST command parser and runner.

Parses the BACKTEST command from the CLI, validates input,
and orchestrates the backtesting engine.
"""

from __future__ import annotations

from backtester.batch_indicators import COMPONENT_MAP, INDICATORS
from backtester.engine import BacktestEngine, Condition
from backtester.reporting import format_results
from indicators._data import _DEFAULT_WINDOWS, _VALID_INTERVALS


# Supported comparison operators
_OPERATORS = {">", "<", ">=", "<=", "=="}

# Word-based aliases so users don't need to quote shell-special chars
_OPERATOR_ALIASES: dict[str, str] = {
    "below": "<",
    "less_than": "<",
    "under": "<",
    "above": ">",
    "greater_than": ">",
    "over": ">",
    "at_or_below": "<=",
    "less_than_or_equal": "<=",
    "at_most": "<=",
    "at_or_above": ">=",
    "greater_than_or_equal": ">=",
    "at_least": ">=",
    "equals": "==",
    "equal_to": "==",
    "eq": "==",
}

# Default config values
_DEFAULTS = {
    "years": 2,
    "hold": 10,
    "capital": 10000,
    "benchmark": "SPY",
    "stop_loss": None,
}


def parse_backtest_command(tokens: list[str]) -> dict:
    """Parse BACKTEST command tokens into structured config.

    Args:
        tokens: Raw tokens from the CLI input after BACKTEST.

    Returns:
        Dict with tickers, conditions, and options.

    Raises:
        ValueError: If the command is malformed.
    """
    if not tokens:
        raise ValueError(
            "No arguments specified. "
            "Usage: BACKTEST <tickers> <conditions> [options]"
        )

    # Split tokens into positional (tickers + conditions) and
    # named (--option value) parts
    positional: list[str] = []
    options: dict[str, str] = {}
    i = 0
    while i < len(tokens):
        if tokens[i].startswith("--"):
            key = tokens[i][2:]
            if key == "stop-loss":
                key = "stop_loss"
            if i + 1 < len(tokens):
                options[key] = tokens[i + 1]
                i += 2
            else:
                raise ValueError(
                    f"Option '{tokens[i]}' requires a value"
                )
        else:
            positional.append(tokens[i])
            i += 1

    if not positional:
        raise ValueError(
            "No tickers or conditions specified. "
            "Usage: BACKTEST <tickers> <conditions>"
        )

    # First token is tickers (comma-separated)
    tickers_raw = positional[0]
    tickers = [t.strip().upper() for t in tickers_raw.split(",")]
    tickers = [t for t in tickers if t]
    if not tickers:
        raise ValueError("No valid tickers specified")

    # Remaining positional tokens are conditions
    cond_tokens = positional[1:]
    if not cond_tokens:
        raise ValueError(
            "No conditions specified. "
            "Usage: BACKTEST <tickers> <INDICATOR OP VALUE INTERVAL> ..."
        )

    # Parse conditions: group tokens into individual conditions
    # Each condition is: INDICATOR [params] [component] OP VALUE INTERVAL
    conditions = _parse_conditions(cond_tokens)

    # Parse options with defaults
    config: dict = {
        "tickers": tickers,
        "conditions": conditions,
    }
    for key, default in _DEFAULTS.items():
        val = options.get(key, default)
        if val is not None and key in ("years", "hold", "capital"):
            try:
                val = int(val)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Option '{key}' must be an integer, got '{val}'"
                )
        elif val is not None and key == "stop_loss":
            try:
                val = float(val)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Option 'stop-loss' must be a number, got '{val}'"
                )
        config[key] = val

    return config


def _parse_conditions(tokens: list[str]) -> list[Condition]:
    """Parse condition tokens into Condition objects.

    Conditions are separated by being non-overlapping.
    Each condition ends with an INTERVAL token.

    Args:
        tokens: List of condition tokens.

    Returns:
        List of parsed Condition objects.

    Raises:
        ValueError: If a condition is malformed.
    """
    conditions: list[Condition] = []
    current: list[str] = []

    for token in tokens:
        current.append(token)
        # Check if this token could be an interval
        if _is_interval(token):
            cond = _parse_single_condition(current)
            conditions.append(cond)
            current = []

    if current:
        raise ValueError(
            f"Incomplete condition: {' '.join(current)}. "
            f"Each condition must end with an interval "
            f"(e.g. 1d, 1wk, 1mo)."
        )

    return conditions


def _parse_single_condition(tokens: list[str]) -> Condition:
    """Parse a single condition from tokens.

    Format: INDICATOR [params] [component] OP VALUE INTERVAL

    Args:
        tokens: Tokens for one condition.

    Returns:
        Parsed Condition object.

    Raises:
        ValueError: If the condition is malformed.
    """
    if len(tokens) < 4:
        raise ValueError(
            f"Condition too short: {' '.join(tokens)}. "
            f"Need: INDICATOR [params] [component] OP VALUE INTERVAL"
        )

    # Last token is interval
    interval = tokens[-1].lower()
    if interval not in _VALID_INTERVALS:
        raise ValueError(
            f"Invalid interval '{interval}'. "
            f"Supported: {', '.join(sorted(_VALID_INTERVALS))}"
        )

    # Second to last is value
    try:
        value = float(tokens[-2])
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid value '{tokens[-2]}'. Must be a number."
        )

    # Third to last is operator (supports word aliases)
    raw_operator = tokens[-3]
    operator = _OPERATOR_ALIASES.get(raw_operator.lower(), raw_operator)
    if operator not in _OPERATORS:
        raise ValueError(
            f"Invalid operator '{operator}'. "
            f"Supported: {', '.join(sorted(_OPERATORS))}"
        )

    # Everything before operator is: INDICATOR [params] [component]
    prefix = tokens[:-3]
    if not prefix:
        raise ValueError("Missing indicator name")

    indicator = prefix[0].upper()
    if indicator not in INDICATORS:
        raise ValueError(
            f"Unknown indicator '{indicator}'. "
            f"Supported: {', '.join(sorted(INDICATORS))}"
        )

    # Parse optional params and component
    params, component = _parse_indicator_args(indicator, prefix[1:])

    return Condition(
        indicator=indicator,
        params=params,
        component=component,
        operator=operator,
        value=value,
        interval=interval,
    )


def _parse_indicator_args(
    indicator: str, args: list[str]
) -> tuple[tuple, str | None]:
    """Parse optional parameters and component for an indicator.

    Args:
        indicator: Indicator name.
        args: Additional arguments after indicator name.

    Returns:
        (params_tuple, component_or_None)

    Raises:
        ValueError: If arguments are invalid.
    """
    valid_components = COMPONENT_MAP.get(indicator, [])

    params_list: list[float] = []
    component: str | None = None

    for arg in args:
        # Check if it's a component name
        if arg.lower() in valid_components:
            component = arg.lower()
            continue
        # Try to parse as parameter
        try:
            params_list.append(float(arg))
        except (ValueError, TypeError):
            # Could be comma-separated params
            parts = arg.split(",")
            for part in parts:
                try:
                    params_list.append(float(part))
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Invalid parameter '{arg}' for {indicator}. "
                        f"Parameters must be numeric."
                    )

    # Validate parameter count for multi-param indicators
    expected = _expected_param_count(indicator)
    if expected is not None and len(params_list) != expected:
        raise ValueError(
            f"{indicator} requires {expected} parameter(s), "
            f"got {len(params_list)}."
        )

    # For single-default indicators, if params are provided, must be 0 or 1
    if len(params_list) > 1:
        defaults = _DEFAULT_WINDOWS.get(indicator)
        if defaults is not None and not isinstance(defaults, tuple):
            raise ValueError(
                f"{indicator} takes at most 1 parameter, "
                f"got {len(params_list)}."
            )

    return tuple(params_list), component


def _expected_param_count(indicator: str) -> int | None:
    """Return expected parameter count for an indicator.

    Returns None if the indicator accepts variable params or has a
    single default (params are optional).
    Returns the tuple length for multi-param indicators (e.g. MACD).
    """
    defaults = _DEFAULT_WINDOWS.get(indicator)
    if defaults is None:
        return None
    if isinstance(defaults, tuple):
        return len(defaults)
    # Single default value — params are optional (0 or 1 allowed)
    return None


def _is_interval(token: str) -> bool:
    """Check if a token looks like an interval."""
    return token.lower() in _VALID_INTERVALS


def run_backtest(config: dict) -> None:
    """Run a backtest with the given configuration.

    This is the entry point called from main.py.

    Args:
        config: Parsed backtest configuration.
    """
    conditions = config["conditions"]
    tickers = config["tickers"]

    # Print header
    print("\n=== QuantLab Backtester ===")
    cond_strs = []
    for c in conditions:
        parts = [c.indicator]
        if c.component:
            parts.append(c.component)
        parts.append(f"{c.operator}{c.value}")
        parts.append(c.interval)
        cond_strs.append(" ".join(parts))
    print(f"\nStrategy: {' AND '.join(cond_strs)}")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Period: {config['years']} years")
    print(
        f"Hold: {config['hold']} bars | "
        f"Capital: ${config['capital']:,} | "
        f"Benchmark: {config['benchmark']}"
    )

    # Run engine
    engine = BacktestEngine(conditions, config)
    result = engine.run()

    # Format and print results
    report = format_results(result)
    print(report)
