import sys
import random
import pytest


class NodeCollector:
    """Pytest plugin that collects test node IDs without running them."""

    def __init__(self):
        self.nodeids = []

    def pytest_collection_finish(self, session):
        self.nodeids = [item.nodeid for item in session.items]


def pick_random_realtest() -> str | None:
    """Collect all realtests and return one random node ID."""
    collector = NodeCollector()
    pytest.main(["realtests/", "--collect-only", "-q", "--tb=short"],
                plugins=[collector])
    if not collector.nodeids:
        return None
    return random.choice(collector.nodeids)


def main():
    node = pick_random_realtest()
    if node is None:
        print("No realtests found to run")
        sys.exit(1)
    print(f"Running random realtest: {node}")
    sys.exit(pytest.main([node, "-v", "--tb=short"]))


if __name__ == "__main__":
    main()
