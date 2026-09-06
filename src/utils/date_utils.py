from datetime import datetime, timedelta, time
from typing import Tuple

def get_last_complete_week(reference_date: datetime = None) -> Tuple[datetime, datetime]:
    """
    Returns the start and end datetime for the last complete week (Monday to Sunday).
    If reference_date is not provided, uses current local time.
    """
    if reference_date is None:
        reference_date = datetime.now()
        
    # Find the most recent Sunday (if today is Monday, it's yesterday)
    # weekday(): Monday is 0, Sunday is 6
    days_since_sunday = reference_date.weekday() + 1
    
    last_sunday = reference_date - timedelta(days=days_since_sunday)
    end_date = datetime.combine(last_sunday.date(), time(23, 59, 59))
    
    last_monday = last_sunday - timedelta(days=6)
    start_date = datetime.combine(last_monday.date(), time(0, 0, 0))
    
    return start_date, end_date

def get_date_range(start: datetime, end: datetime) -> Tuple[datetime, datetime]:
    """
    Returns an explicit date range, ensuring start is before end.
    """
    if start > end:
        return end, start
    return start, end
