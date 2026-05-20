# run_real_tests.py
# Runs all integration tests sequentially with 1-second spacing
# to avoid yfinance rate limits

import sys
import time
import pytest


class NodeCollector:
    """Pytest plugin that collects test node IDs without running them."""

    def __init__(self):
        self.nodeids = []

    def pytest_collection_finish(self, session):
        self.nodeids = [item.nodeid for item in session.items]


def main() -> None:
    """Collect all realtests and run each one with a 1-second pause."""
    collector = NodeCollector()
    pytest.main(["realtests/", "--collect-only", "-q", "--tb=short"],
                plugins=[collector])

    if not collector.nodeids:
        print("No realtests found to run")
        sys.exit(1)

    total = len(collector.nodeids)
    print(f"Running {total} real test(s) with 1s spacing"
          " to avoid yfinance rate limits")

    for i, nodeid in enumerate(collector.nodeids):
        if i > 0:
            time.sleep(1)
        print(f"\n--- {i + 1}/{total}: {nodeid} ---")
        ret = pytest.main([nodeid, "-v", "--tb=short"])
        if ret != 0:
            sys.exit(ret)

    print(f"\nAll {total} real test(s) passed")


if __name__ == "__main__":
    main()
