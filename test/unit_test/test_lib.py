from datetime import date

from data import lib


def test_last_working_date_generator():
    start_date = date(year=2025, month=2, day=1) # Saturday
    
    g = lib.last_working_date_generator(start_date)

    assert next(g) == date(year=2025, month=1, day=31)
    assert next(g) == date(year=2025, month=1, day=30)
    assert next(g) == date(year=2025, month=1, day=29)
    assert next(g) == date(year=2025, month=1, day=28)
    assert next(g) == date(year=2025, month=1, day=27)

    assert next(g) == date(year=2025, month=1, day=24)
    assert next(g) == date(year=2025, month=1, day=23)
