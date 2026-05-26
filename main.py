# main.py
# CLI entry point: parse input, dispatch to indicator, format output

import sys

from indicators import calculate_sma, calculate_ema, calculate_rsi, \
    calculate_macd, calculate_bb, calculate_vwap, calculate_av, \
    calculate_rvol
from indicators._data import _VALID_INTERVALS, _DEFAULT_WINDOWS


def main(argv: list[str] | None = None) -> None:
    """Parse user input and dispatch to the requested indicator.

    Expects at least two space-separated values: ticker(s) and
    indicator name (SMA, RSI, EMA, MACD, BB, VWAP, AV, or RVOL).
    Multiple tickers are separated with commas
    (e.g. ``AAPL,MSFT``).
    Optional trailing arguments can appear in any order:

      * A recognised bar size sets the interval ("1d", "1wk", "1mo").
      * A plain positive integer sets the lookback window.
      * "C" followed by a positive integer (e.g. "C10") sets the
        number of most-recent indicator values to return.
      * For MACD, three comma-separated integers set the fast,
        slow, and signal periods (e.g. "12,26,9").
      * For BB, two comma-separated values set the window and
        number of standard deviations (e.g. "20,2.0").

    Defaults are "1d" for interval, indicator-specific windows
    (SMA=50, EMA=20, RSI=14, MACD=(12,26,9), BB=(20,2.0),
    VWAP=20, AV=20, RVOL=10), and count=1.
    """
    if argv:
        user_input = " ".join(argv)
    else:
        user_input = input("Enter ticker(s), indicator"
                           " (SMA/RSI/EMA/MACD/BB/VWAP/AV/RVOL)"
                           " [bar_size] [window] [C<count>]: ")
    parts = user_input.strip().split()

    if len(parts) < 2:
        print("Error: expected at least 2 values"
              " (ticker(s) indicator [bar_size] [window]"
              " [C<count>])")
        sys.exit(1)

    # Rejoin comma-fragment tokens so "AAPL , MSFT" is treated as
    # "AAPL,MSFT" rather than three separate tokens.
    merged = [parts[0]]
    for token in parts[1:]:
        if token == "," or merged[-1].endswith(","):
            merged[-1] += token
        elif token.startswith(","):
            merged[-1] += token
        else:
            merged.append(token)

    raw_tickers, indicator, *rest = merged
    tickers = [t.strip() for t in raw_tickers.split(",") if t.strip()]
    if not tickers:
        print("Error: no valid tickers provided")
        sys.exit(1)

    indicator = indicator.upper()
    if indicator not in ("SMA", "RSI", "EMA", "MACD", "BB",
                         "VWAP", "AV", "RVOL"):
        print("Error: indicator must be SMA, RSI, EMA, MACD,"
              " BB, VWAP, AV, or RVOL")
        sys.exit(1)

    interval = "1d"
    count = 1
    seen_interval = False
    seen_window = False
    seen_count = False
    macd_params: tuple[int, int, int] | None = None
    bb_params: tuple[int, float] | None = None
    default = _DEFAULT_WINDOWS[indicator]
    window: int
    if isinstance(default, tuple):
        if indicator == "BB":
            bb_w, bb_s = default
            bb_params = (bb_w, float(bb_s))
        else:
            macd_params = default
        window = 0  # unused for multi-param indicators
    else:
        window = default

    for arg in rest:
        lowered = arg.lower()
        if lowered in _VALID_INTERVALS:
            if seen_interval:
                print(f"Error: duplicate bar size '{arg}'")
                sys.exit(1)
            interval = lowered
            seen_interval = True
        elif lowered.startswith("c"):
            if seen_count:
                print(f"Error: duplicate count '{arg}'")
                sys.exit(1)
            try:
                count = int(lowered[1:])
            except ValueError:
                print(f"Error: invalid count '{arg}'"
                      " (use C<number>, e.g. C10)")
                sys.exit(1)
            if count <= 0:
                print("Error: count must be positive")
                sys.exit(1)
            seen_count = True
        elif indicator == "MACD" and "," in arg:
            if seen_window:
                print("Error: duplicate MACD parameters"
                      f" '{arg}'")
                sys.exit(1)
            try:
                ft_str, sl_str, sg_str = arg.split(",")
                ft, sl, sg = (int(ft_str), int(sl_str),
                              int(sg_str))
            except ValueError:
                print("Error: invalid MACD parameters"
                      f" '{arg}'"
                      " (use fast,slow,signal,"
                      " e.g. 12,26,9)")
                sys.exit(1)
            if ft <= 0 or sl <= 0 or sg <= 0:
                print("Error: MACD parameters must be"
                      " positive")
                sys.exit(1)
            if ft >= sl:
                print(f"Error: fast period ({ft}) must be"
                      f" less than slow period ({sl})")
                sys.exit(1)
            macd_params = (ft, sl, sg)
            seen_window = True
        elif indicator == "BB" and "," in arg:
            if seen_window:
                print(f"Error: duplicate BB parameters"
                      f" '{arg}'")
                sys.exit(1)
            try:
                w_str, s_str = arg.split(",")
                bb_window = int(w_str)
                bb_std = float(s_str)
            except ValueError:
                print("Error: invalid BB parameters"
                      f" '{arg}'"
                      " (use window,num_std,"
                      " e.g. 20,2.5)")
                sys.exit(1)
            if bb_window <= 0 or bb_std <= 0:
                print("Error: BB parameters must be"
                      " positive")
                sys.exit(1)
            bb_params = (bb_window, bb_std)
            seen_window = True
        elif indicator == "MACD":
            print("Error: MACD requires comma-separated"
                  " parameters (e.g. 12,26,9)")
            sys.exit(1)
        elif indicator == "BB":
            print("Error: BB requires comma-separated"
                  " parameters (e.g. 20,2.5)")
            sys.exit(1)
        else:
            try:
                w = int(arg)
            except ValueError:
                print(f"Error: unrecognised argument '{arg}'")
                sys.exit(1)
            if w <= 0:
                print("Error: window must be positive")
                sys.exit(1)
            if seen_window:
                print(f"Error: duplicate window '{arg}'")
                sys.exit(1)
            window = w
            seen_window = True

    for ticker in tickers:
        try:
            match indicator:
                case "SMA":
                    result = calculate_sma(ticker, window,
                                           interval=interval, count=count)
                case "EMA":
                    result = calculate_ema(ticker, window,
                                           interval=interval, count=count)
                case "RSI":
                    result = calculate_rsi(ticker, window,
                                           interval=interval, count=count)
                case "MACD":
                    fast, slow, signal = macd_params
                    m_line, s_line, hist = calculate_macd(
                        ticker, fast=fast, slow=slow,
                        signal=signal,
                        interval=interval, count=count
                    )
                case "BB":
                    bb_window, bb_std = bb_params
                    u, m, l = calculate_bb(
                        ticker, window=bb_window,
                        num_std=bb_std,
                        interval=interval, count=count
                    )
                case "VWAP":
                    result = calculate_vwap(ticker, window,
                                            interval=interval,
                                            count=count)
                case "AV":
                    result = calculate_av(ticker, window,
                                          interval=interval,
                                          count=count)
                case "RVOL":
                    result = calculate_rvol(ticker, window,
                                            interval=interval,
                                            count=count)
        except IndexError as e:
            print(f"Error: {e}")
            continue
        except Exception as e:
            print(f"Error: {ticker} failed — {e}")
            continue

        if indicator == "BB":
            if count == 1:
                print(f"{ticker} BB({bb_window},{bb_std}):"
                      f" Upper={u.iloc[-1]:.2f}"
                      f" Middle={m.iloc[-1]:.2f}"
                      f" Lower={l.iloc[-1]:.2f}")
            else:
                print(f"{ticker} BB({bb_window},{bb_std})"
                      f" (last {count}):")
                for i in range(count):
                    print(f"  Upper={u.iloc[i]:.2f}"
                          f" Middle={m.iloc[i]:.2f}"
                          f" Lower={l.iloc[i]:.2f}")
        elif indicator == "MACD":
            if count == 1:
                print(f"{ticker} MACD({fast},{slow},{signal}):"
                      f" MACD={m_line.iloc[-1]:.2f}"
                      f" Signal={s_line.iloc[-1]:.2f}"
                      f" Hist={hist.iloc[-1]:.2f}")
            else:
                print(f"{ticker} MACD({fast},{slow},{signal})"
                      f" (last {count}):")
                for i in range(count):
                    print(f"  MACD={m_line.iloc[i]:.2f}"
                          f" Signal={s_line.iloc[i]:.2f}"
                          f" Hist={hist.iloc[i]:.2f}")
        elif count == 1:
            print(f"{ticker} {window}-{indicator}:"
                  f" {result.iloc[-1]:.2f}")
        else:
            print(f"{ticker} {window}-{indicator}"
                  f" (last {count}):")
            for val in result:
                print(f"  {val:.2f}")


if __name__ == "__main__":
    main(sys.argv[1:])
