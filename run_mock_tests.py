# run_mock_tests.py
# Runs all mock tests with a summary report of pass/fail results

import sys
import pytest


class ResultCollector:
    """Pytest plugin that records test results for a summary report."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1
                self.failures.append(report)


def run_tests(args: list[str], label: str = "") -> int:
    """Run pytest with the given args and print a summary block.

    Args:
        args: Command-line arguments forwarded to pytest.
        label: Optional heading printed above the summary.

    Returns:
        Exit code 0 if all tests passed, 1 otherwise.
    """
    collector = ResultCollector()
    pytest.main(args, plugins=[collector])
    total = collector.passed + collector.failed
    print()
    print("=" * 60)
    if label:
        print(f"  {label}")
    if collector.failed == 0:
        print(f"  {collector.passed} out of {total} tests passed")
    else:
        print(f"  {collector.passed} out of {total} tests passed")
        print()
        print("FAILED TESTS:")
        for f in collector.failures:
            print(f"    {f.nodeid}")
            lines = str(f.longrepr).split("\n")
            for line in lines:
                print(f"      {line}")
            print()
    print("=" * 60)
    return 0 if collector.failed == 0 else 1


def main() -> int:
    """Run mock tests under mocktests/ with verbose output."""
    return run_tests(["mocktests/", "-v", "--tb=short"], "MOCKTESTS")


if __name__ == "__main__":
    sys.exit(main())
