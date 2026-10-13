"""
Attendance Tool - handles marking and retrieving attendance.
Used by the LLM as a function-calling tool.
"""
from datetime import datetime
from models.student import update_attendance, get_attendance_summary, get_student


def mark_attendance(roll_number: str, date: str, status: str) -> str:
    """
    Mark attendance for a student on a specific date.

    Args:
        roll_number: Student roll number (e.g. "CS2023001")
        date: Date in YYYY-MM-DD format. Use "today" for current date.
        status: "present" or "absent"

    Returns:
        Confirmation message string.
    """
    if date.lower() in ("today", ""):
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return f"Invalid date format '{date}'. Please use YYYY-MM-DD or 'today'."

    if status.lower() not in ("present", "absent"):
        return "Status must be 'present' or 'absent'."

    present = status.lower() == "present"

    student = get_student(roll_number)
    if not student:
        return f"Student with roll number {roll_number} not found. Please register first."

    update_attendance(roll_number, date, present)
    status_word = "Present" if present else "Absent"
    return (
        f"Attendance marked for {student['name']} ({roll_number})\n"
        f"Date: {date}\n"
        f"Status: {status_word} ?"
    )


def get_attendance(roll_number: str) -> str:
    """
    Get full attendance summary for a student.

    Args:
        roll_number: Student roll number

    Returns:
        Formatted attendance summary string.
    """
    student = get_student(roll_number)
    if not student:
        return f"Student with roll number {roll_number} not found. Please register first."

    summary = get_attendance_summary(roll_number)
    pct = summary["attendance_percentage"]

    if pct >= 75:
        status_icon = "GOOD"
    elif pct >= 60:
        status_icon = "WARNING"
    else:
        status_icon = "CRITICAL - Below 75%!"

    lines = [
        f"=== Attendance Report ===",
        f"Name        : {summary['name']}",
        f"Roll No.    : {summary['roll_number']}",
        f"Branch      : {summary['branch']}",
        f"Semester    : {summary['semester']}",
        f"",
        f"Days Present: {summary['days_attended']}",
        f"Days Absent : {summary['days_absent']}",
        f"Total Days  : {summary['total_working_days']}",
        f"Percentage  : {pct}%  [{status_icon}]",
    ]

    attendance = summary.get("attendance_record", {})
    if attendance:
        lines.append("")
        lines.append("Recent Attendance:")
        sorted_dates = sorted(attendance.keys(), reverse=True)[:10]
        for d in sorted_dates:
            mark = "P" if attendance[d] else "A"
            lines.append(f"  {d}: {mark}")

    return "\n".join(lines)


def get_attendance_percentage(roll_number: str) -> str:
    """
    Get just the attendance percentage for a student.

    Args:
        roll_number: Student roll number

    Returns:
        Attendance percentage as a formatted string.
    """
    student = get_student(roll_number)
    if not student:
        return f"Student with roll number {roll_number} not found. Please register first."

    summary = get_attendance_summary(roll_number)
    pct = summary["attendance_percentage"]

    if pct >= 75:
        advice = "Your attendance is good. Keep it up!"
    elif pct >= 60:
        advice = "Your attendance is borderline. Attend more classes to stay safe."
    else:
        advice = "CRITICAL: Your attendance is below 75%. You may be detained!"

    days_needed = 0
    if pct < 75 and summary["total_working_days"] > 0:
        current_attended = summary["days_attended"]
        current_total = summary["total_working_days"]
        numerator = 0.75 * current_total - current_attended
        if numerator > 0:
            days_needed = int(numerator / 0.25) + 1

    result = (
        f"Attendance for {summary['name']} ({roll_number}):\n"
        f"  Percentage : {pct}%\n"
        f"  Present    : {summary['days_attended']} / {summary['total_working_days']} days\n"
        f"  {advice}"
    )

    if days_needed > 0:
        result += f"\n  You need to attend at least {days_needed} more consecutive days to reach 75%."

    return result
