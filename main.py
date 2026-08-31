# main.py
# QuantLab entry point — starts the web API by default.
# Legacy CLI mode: python main.py backtest <args>

import sys

if __name__ == "__main__":
    # If the first arg is "backtest", run legacy CLI mode
    if len(sys.argv) > 1 and sys.argv[1].upper() == "BACKTEST":
        from backtester.cli import parse_backtest_command, run_backtest
        try:
            config = parse_backtest_command(sys.argv[2:])
            run_backtest(config)
        except ValueError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        # Default: start the web server
        import uvicorn
        from api.main import app

        uvicorn.run(app, host="0.0.0.0", port=8000)
