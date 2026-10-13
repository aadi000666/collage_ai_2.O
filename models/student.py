"""
Student data model - stores and manages student information and attendance records.
"""
import json
import os
from datetime import datetime
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "students.json")


def _load_data() -> dict:
    """Load all student data from the JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_data(data: dict):
    """Save all student data to the JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def register_student(
    roll_number: str,
    name: str,
    branch: str,
    semester: int,
    total_working_days: int = 0
) -> dict:
    """
    Register a new student or update existing student info.
    Returns the student record.
    """
    data = _load_data()
    if roll_number in data:
        student = data[roll_number]
        student["name"] = name
        student["branch"] = branch
        student["semester"] = semester
        if total_working_days:
            student["total_working_days"] = total_working_days
    else:
        student = {
            "roll_number": roll_number,
            "name": name,
            "branch": branch,
            "semester": semester,
            "total_working_days": total_working_days,
            "attendance": {},
            "registered_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    data[roll_number] = student
    _save_data(data)
    return student


def get_student(roll_number: str) -> Optional[dict]:
    """Retrieve a student record by roll number."""
    data = _load_data()
    return data.get(roll_number)


def update_attendance(roll_number: str, date: str, present: bool) -> dict:
    """
    Mark a student present or absent on a given date.
    date format: YYYY-MM-DD
    Returns updated student record.
    """
    data = _load_data()
    if roll_number not in data:
        raise ValueError(f"Student {roll_number} not found. Please register first.")
    data[roll_number]["attendance"][date] = present
    _save_data(data)
    return data[roll_number]


def get_attendance_summary(roll_number: str) -> dict:
    """
    Returns a summary dict with attended_days, total_marked, percentage, etc.
    """
    data = _load_data()
    if roll_number not in data:
        raise ValueError(f"Student {roll_number} not found.")
    student = data[roll_number]
    attendance = student.get("attendance", {})
    total_marked = len(attendance)
    attended = sum(1 for v in attendance.values() if v)
    absent = total_marked - attended
    total_working = student.get("total_working_days", total_marked)
    percentage = (attended / total_working * 100) if total_working > 0 else 0.0
    return {
        "roll_number": roll_number,
        "name": student["name"],
        "branch": student["branch"],
        "semester": student["semester"],
        "total_working_days": total_working,
        "days_attended": attended,
        "days_absent": absent,
        "total_marked": total_marked,
        "attendance_percentage": round(percentage, 2),
        "attendance_record": attendance
    }


def list_all_students() -> list:
    """List all registered students (basic info)."""
    data = _load_data()
    result = []
    for roll, s in data.items():
        att = s.get("attendance", {})
        attended = sum(1 for v in att.values() if v)
        total = s.get("total_working_days", len(att))
        pct = round(attended / total * 100, 2) if total > 0 else 0.0
        result.append({
            "roll_number": roll,
            "name": s["name"],
            "branch": s["branch"],
            "semester": s["semester"],
            "attendance_percentage": pct
        })
    return result
