import os
import time
import pytest

REALTESTS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    yield
    if nextitem is not None and not os.environ.get("REALTEST_NO_SLEEP"):
        if str(item.fspath).startswith(REALTESTS_DIR):
            time.sleep(1)
