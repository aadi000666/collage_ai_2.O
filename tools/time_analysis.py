"""
Time Analysis Tool - handles time-related queries for college schedule.
Used by the LLM as a function-calling tool.
"""
from datetime import datetime, timedelta


def get_current_time() -> str:
    """
    Get the current date and time.

    Returns:
        Formatted current datetime string.
    """
    now = datetime.now()
    day_name = now.strftime("%A")
    return (
        f"Current Date & Time:\n"
        f"  Date      : {now.strftime('%Y-%m-%d')} ({day_name})\n"
        f"  Time      : {now.strftime('%I:%M %p')}\n"
        f"  Full      : {now.strftime('%d %B %Y, %I:%M %p')}"
    )


def days_until(target_date: str) -> str:
    """
    Calculate how many days until a target date (e.g., exam date, submission deadline).

    Args:
        target_date: Date string in YYYY-MM-DD format

    Returns:
        Number of days until that date as a formatted string.
    """
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        return f"Invalid date format '{target_date}'. Use YYYY-MM-DD."

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (target - today).days

    if delta < 0:
        return f"{target_date} was {abs(delta)} day(s) ago."
    elif delta == 0:
        return f"{target_date} is TODAY!"
    else:
        return (
            f"Days until {target_date}:\n"
            f"  {delta} day(s) remaining\n"
            f"  That's approximately {delta // 7} week(s) and {delta % 7} day(s)."
        )


def working_days_between(start_date: str, end_date: str, exclude_weekends: bool = True) -> str:
    """
    Count working days between two dates (useful for calculating total class days).

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        exclude_weekends: Whether to exclude Saturdays and Sundays (default True)

    Returns:
        Number of working days as a formatted string.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

    if start > end:
        return "Start date must be before end date."

    total_days = (end - start).days + 1
    working = 0
    current = start
    while current <= end:
        if exclude_weekends:
            if current.weekday() < 5:
                working += 1
        else:
            working += 1
        current += timedelta(days=1)

    return (
        f"Working Days Analysis:\n"
        f"  From  : {start_date}\n"
        f"  To    : {end_date}\n"
        f"  Total Calendar Days: {total_days}\n"
        f"  Working Days (excl. weekends): {working}"
    )


def get_semester_week(semester_start: str) -> str:
    """
    Get which week of the semester we are currently in.

    Args:
        semester_start: Semester start date in YYYY-MM-DD format

    Returns:
        Current semester week as a formatted string.
    """
    try:
        start = datetime.strptime(semester_start, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (today - start).days

    if delta < 0:
        return f"Semester hasn't started yet. Starts in {abs(delta)} days."

    week_number = delta // 7 + 1
    day_of_week = today.strftime("%A")

    return (
        f"Semester Progress:\n"
        f"  Semester Start: {semester_start}\n"
        f"  Today         : {today.strftime('%Y-%m-%d')} ({day_of_week})\n"
        f"  Current Week  : Week {week_number}\n"
        f"  Days Elapsed  : {delta}"
    )
