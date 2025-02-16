import calendar

from datetime import date, timedelta


def last_working_date_generator(start_date: date):
    cur_date = start_date
    while True:
        if cur_date.weekday() == calendar.SATURDAY:
            cur_date -= timedelta(days=1)
        elif cur_date.weekday() == calendar.SUNDAY:
            cur_date -= timedelta(days=1)
            cur_date -= timedelta(days=1)

        yield cur_date
        cur_date -= timedelta(days=1)
