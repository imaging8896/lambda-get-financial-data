import time

import pytest



@pytest.fixture(autouse=True)
def deplay():
    time.sleep(12.5342)
