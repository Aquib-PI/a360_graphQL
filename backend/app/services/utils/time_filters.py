# File: backend/app/services/utils/time_filters.py
from typing import Optional, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import text


def get_date_ranges(
    filter_type: str,
    custom: Optional[Tuple[datetime, datetime]] = None
) -> Tuple[datetime, datetime, datetime, datetime]:
    """
    Given a filter name and optional custom (start, end) datetimes,
    returns (start, end, comp_start, comp_end) datetime windows
    for current vs. comparison periods.

    filter_type is case-insensitive (e.g. 'today', 'YTD', 'Custom').
    """
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ft = filter_type.lower()

    if ft == 'today':
        start = today
        end = now
        comp_start = start - timedelta(days=1)
        comp_end = end - timedelta(days=1)

    elif ft == 'yesterday':
        start = today - timedelta(days=1)
        end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
        comp_start = start - timedelta(days=1)
        comp_end = comp_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    elif ft in ('daily', 'daily_previous'):
        # daily refers to full previous day
        end = today - timedelta(days=1)
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        comp_start = start - timedelta(days=1)
        comp_end = end - timedelta(days=1)

    elif ft == 'weekly':
        # last 7 days ending yesterday
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
        comp_start = start - timedelta(days=7)
        comp_end = end - timedelta(days=7)

    elif ft == 'mtd':
        start = today.replace(day=1)
        end = now
        try:
            comp_start = start - relativedelta(months=1)
            comp_end = end - relativedelta(months=1)
        except ValueError:
            # Handle shorter previous month
            last_prev = start - timedelta(days=1)
            comp_start = last_prev.replace(day=1)
            comp_end = last_prev.replace(
                hour=end.hour,
                minute=end.minute,
                second=end.second,
                microsecond=end.microsecond,
            )

    elif ft == 'monthly':
        # full previous calendar month
        first_of_month = today.replace(day=1)
        end = first_of_month - timedelta(days=1)
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        comp_start = start - relativedelta(months=1)
        comp_end = end - relativedelta(months=1)

    elif ft == 'ytd':
        start = today.replace(month=1, day=1)
        end = now
        comp_start = start.replace(year=start.year - 1)
        comp_end = comp_start + (end - start)

    elif ft == 'custom' and custom:
        start, end = custom
        # normalize to full days if date inputs
        if not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time())
        if not isinstance(end, datetime):
            end = datetime.combine(end, datetime.min.time())
        comp_start = start - timedelta(days=1)
        comp_end = end - timedelta(days=1)

    else:
        raise ValueError(f"Unsupported filter: {filter_type}")

    return start, end, comp_start, comp_end


def fetch_one(conn, sql: str, params: dict) -> float:
    """
    Executes a scalar SQL query and returns its single numeric result.
    Falls back to 0.0 if nothing is returned.
    """
    result = conn.execute(text(sql), params).scalar()
    return float(result or 0.0)


def pct_diff(current: float, previous: float) -> float:
    """
    Returns percentage difference: (current - previous)/previous * 100.
    Rounded to 2 decimals; returns 0.0 if previous is zero.
    """
    if previous:
        return round((current - previous) / previous * 100, 2)
    return 0.0
