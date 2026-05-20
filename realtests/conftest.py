import os
import time
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    yield
    if nextitem is not None and not os.environ.get("REALTEST_NO_SLEEP"):
        time.sleep(1)
