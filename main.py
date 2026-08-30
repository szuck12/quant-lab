# main.py
# CLI entry point: parse input, dispatch to indicator, format output

import sys

from indicators import calculate_adx, calculate_atr, \
    calculate_av, calculate_bb, calculate_cci, calculate_ema, \
    calculate_macd, calculate_obv, calculate_roc, calculate_rsi, \
    calculate_rvol, calculate_sma, calculate_stoch, calculate_vwap
from indicators._data import _VALID_INTERVALS, _DEFAULT_WINDOWS, \
    _sanitize_display


def main(argv: list[str] | None = None) -> None:
    """Parse user input and dispatch to the requested indicator.

    Expects at least two space-separated values: ticker(s) and
    indicator name (ADX, ATR, AV, BB, CCI, EMA, MACD, OBV, ROC,
    RSI, RVOL, SMA, STOCH, or VWAP).
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
      * For STOCH, three comma-separated integers set the window,
        %K smoothing, and %D smoothing (e.g. "14,3,3").
      * For ADX, two comma-separated integers set the DI
        smoothing length and the ADX smoothing length
        (e.g. "14,14").

    Defaults are "1d" for interval, indicator-specific windows
    (ADX=(14,14), ATR=14, AV=20, BB=(20,2.0), CCI=20, EMA=20,
    MACD=(12,26,9), OBV=30, ROC=9, RSI=14, RVOL=10, SMA=50,
    STOCH=(14,3,3), VWAP=20), and count=1.
    """
    if argv:
        user_input = " ".join(argv)
    else:
        user_input = input("Enter ticker(s), indicator"
                           " (ADX/ATR/AV/BB/CCI/EMA/MACD/OBV/"
                           "ROC/RSI/RVOL/SMA/STOCH/VWAP)"
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
    tickers = [_sanitize_display(t.strip())
               for t in raw_tickers.split(",") if t.strip()]
    if not tickers:
        print("Error: no valid tickers provided")
        sys.exit(1)

    indicator = indicator.upper()
    if indicator not in ("ADX", "ATR", "AV", "BB", "CCI", "EMA",
                         "MACD", "OBV", "ROC", "RSI", "RVOL",
                         "SMA", "STOCH", "VWAP"):
        print("Error: indicator must be ADX, ATR, AV, BB, CCI,"
              " EMA, MACD, OBV, ROC, RSI, RVOL, SMA, STOCH, or"
              " VWAP")
        sys.exit(1)

    interval = "1d"
    count = 1
    seen_interval = False
    seen_window = False
    seen_count = False
    macd_params: tuple[int, int, int] | None = None
    bb_params: tuple[int, float] | None = None
    stoch_params: tuple[int, int, int] | None = None
    adx_params: tuple[int, int] | None = None
    default = _DEFAULT_WINDOWS[indicator]
    window: int
    if isinstance(default, tuple):
        if indicator == "ADX":
            adx_params = default
        elif indicator == "BB":
            bb_w, bb_s = default
            bb_params = (bb_w, float(bb_s))
        elif indicator == "STOCH":
            stoch_params = default
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
        elif indicator == "ADX" and "," in arg:
            if seen_window:
                print(f"Error: duplicate ADX parameters"
                      f" '{arg}'")
                sys.exit(1)
            try:
                w_str, aw_str = arg.split(",")
                adx_w, adx_aw = int(w_str), int(aw_str)
            except ValueError:
                print("Error: invalid ADX parameters"
                      f" '{arg}'"
                      " (use window,adx_window,"
                      " e.g. 14,14)")
                sys.exit(1)
            if adx_w <= 0 or adx_aw <= 0:
                print("Error: ADX parameters must be"
                      " positive")
                sys.exit(1)
            adx_params = (adx_w, adx_aw)
            seen_window = True
        elif indicator == "ADX":
            print("Error: ADX requires comma-separated"
                  " parameters (e.g. 14,14)")
            sys.exit(1)
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
        elif indicator == "STOCH" and "," in arg:
            if seen_window:
                print("Error: duplicate STOCH parameters"
                      f" '{arg}'")
                sys.exit(1)
            try:
                w_str, sk_str, sd_str = arg.split(",")
                w, sk, sd = (int(w_str), int(sk_str),
                             int(sd_str))
            except ValueError:
                print("Error: invalid STOCH parameters"
                      f" '{arg}'"
                      " (use window,smooth_k,smooth_d,"
                      " e.g. 14,3,3)")
                sys.exit(1)
            if w <= 0 or sk <= 0 or sd <= 0:
                print("Error: STOCH parameters must be"
                      " positive")
                sys.exit(1)
            stoch_params = (w, sk, sd)
            seen_window = True
        elif indicator == "STOCH":
            print("Error: STOCH requires comma-separated"
                  " parameters (e.g. 14,3,3)")
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
                case "ADX":
                    di_len, adx_len = adx_params
                    plus_di, minus_di, adx_val = calculate_adx(
                        ticker, window=di_len,
                        adx_window=adx_len,
                        interval=interval, count=count
                    )
                case "ATR":
                    result = calculate_atr(ticker, window,
                                           interval=interval,
                                           count=count)
                case "AV":
                    result = calculate_av(ticker, window,
                                          interval=interval,
                                          count=count)
                case "BB":
                    bb_window, bb_std = bb_params
                    upper, mid, lower = calculate_bb(
                        ticker, window=bb_window,
                        num_std=bb_std,
                        interval=interval, count=count
                    )
                case "CCI":
                    result = calculate_cci(ticker, window,
                                           interval=interval,
                                           count=count)
                case "EMA":
                    result = calculate_ema(ticker, window,
                                           interval=interval, count=count)
                case "MACD":
                    fast, slow, signal = macd_params
                    m_line, s_line, hist = calculate_macd(
                        ticker, fast=fast, slow=slow,
                        signal=signal,
                        interval=interval, count=count
                    )
                case "OBV":
                    result = calculate_obv(ticker, window,
                                           interval=interval,
                                           count=count)
                case "ROC":
                    result = calculate_roc(ticker, window,
                                           interval=interval,
                                           count=count)
                case "RSI":
                    result = calculate_rsi(ticker, window,
                                           interval=interval, count=count)
                case "RVOL":
                    result = calculate_rvol(ticker, window,
                                            interval=interval,
                                            count=count)
                case "SMA":
                    result = calculate_sma(ticker, window,
                                           interval=interval, count=count)
                case "STOCH":
                    stoch_w, stoch_sk, stoch_sd = stoch_params
                    k, d = calculate_stoch(
                        ticker, window=stoch_w,
                        smooth_k=stoch_sk, smooth_d=stoch_sd,
                        interval=interval, count=count
                    )
                case "VWAP":
                    result = calculate_vwap(ticker, window,
                                            interval=interval,
                                            count=count)
        except IndexError as e:
            print(f"Error: {e}")
            continue
        except Exception as e:
            print(f"Error: {ticker} failed — {e}")
            continue

        if indicator == "ADX":
            if count == 1:
                print(f"{ticker} ADX({di_len},{adx_len}):"
                      f" +DI={plus_di.iloc[-1]:.2f}"
                      f" -DI={minus_di.iloc[-1]:.2f}"
                      f" ADX={adx_val.iloc[-1]:.2f}")
            else:
                print(f"{ticker} ADX({di_len},{adx_len})"
                      f" (last {count}):")
                for i in range(count):
                    print(f"  +DI={plus_di.iloc[i]:.2f}"
                          f" -DI={minus_di.iloc[i]:.2f}"
                          f" ADX={adx_val.iloc[i]:.2f}")
        elif indicator == "BB":
            if count == 1:
                print(f"{ticker} BB({bb_window},{bb_std}):"
                      f" Upper={upper.iloc[-1]:.2f}"
                      f" Middle={mid.iloc[-1]:.2f}"
                      f" Lower={lower.iloc[-1]:.2f}")
            else:
                print(f"{ticker} BB({bb_window},{bb_std})"
                      f" (last {count}):")
                for i in range(count):
                    print(f"  Upper={upper.iloc[i]:.2f}"
                          f" Middle={mid.iloc[i]:.2f}"
                          f" Lower={lower.iloc[i]:.2f}")
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
        elif indicator == "STOCH":
            if count == 1:
                print(f"{ticker} STOCH({stoch_w},{stoch_sk},"
                      f"{stoch_sd}):"
                      f" %K={k.iloc[-1]:.2f}"
                      f" %D={d.iloc[-1]:.2f}")
            else:
                print(f"{ticker} STOCH({stoch_w},{stoch_sk},"
                      f"{stoch_sd}) (last {count}):")
                for i in range(count):
                    print(f"  %K={k.iloc[i]:.2f}"
                          f" %D={d.iloc[i]:.2f}")
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
