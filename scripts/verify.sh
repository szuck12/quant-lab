#!/usr/bin/env bash
# verify.sh — Pre-handoff verification for QuantLab
# Usage: bash scripts/verify.sh [--full]
#   --full: also run real tests (requires network)

set -euo pipefail

PASS=0
FAIL=0

run_check() {
    local label="$1"
    shift
    printf "  %-45s" "$label"
    if "$@" >/dev/null 2>&1; then
        echo "PASS"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== QuantLab Pre-Handoff Verification ==="
echo ""

echo "Lint..."
run_check "ruff check main.py" ruff check main.py
run_check "ruff check indicators/" ruff check indicators/
run_check "ruff check backtester/" ruff check backtester/
run_check "ruff check api/" ruff check api/

echo ""
echo "Smoke test..."
run_check "python3 main.py backtest (legacy CLI)" python3 main.py backtest AAPL RSI '<' 30 1d --hold 5

echo ""
echo "Mock tests..."
run_check "python3 run_mock_tests.py" python3 run_mock_tests.py

echo ""
echo "API tests..."
run_check "pytest mocktests/test_api.py" python3 -m pytest mocktests/test_api.py -q

echo ""
echo "Frontend build..."
run_check "npm run build (web/)" bash -c 'cd web && npm run build'

echo ""
echo "Deployment files..."
run_check "Dockerfile exists" test -f Dockerfile
run_check "GitHub Actions deploy-frontend exists" test -f .github/workflows/deploy-frontend.yml
run_check "GitHub Actions keep-alive exists" test -f .github/workflows/keep-alive.yml

if [[ "${1:-}" == "--full" ]]; then
    echo ""
    echo "Real tests..."
    run_check "python3 run_real_tests.py" python3 run_real_tests.py
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
