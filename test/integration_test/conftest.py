import time

import pytest



@pytest.fixture(autouse=True)
def deplay():
    time.sleep(1.5342)
