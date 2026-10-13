"""
Calculator Tool - handles mathematical calculations for college use.
Used by the LLM as a function-calling tool.
"""
import math


def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression string (e.g. "85 + 90 + 78 / 3")

    Returns:
        Result of the calculation as a string.
    """
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("__")
    }
    allowed_names.update({
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float
    })
    try:
        clean_expr = expression.strip()
        result = eval(clean_expr, {"__builtins__": {}}, allowed_names)
        return f"Calculation: {clean_expr}\nResult: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}"


def calculate_cgpa(grades: list, credits: list) -> str:
    """
    Calculate CGPA (Cumulative Grade Point Average).

    Args:
        grades: List of grade points (e.g. [9.0, 8.5, 7.0, 8.0])
        credits: List of credit hours for each subject (e.g. [4, 3, 3, 4])

    Returns:
        CGPA as a formatted string.
    """
    if len(grades) != len(credits):
        return "Error: Number of grades must match number of credits."
    if not grades:
        return "Error: No grades provided."

    total_weight = sum(g * c for g, c in zip(grades, credits))
    total_credits = sum(credits)
    if total_credits == 0:
        return "Error: Total credits cannot be zero."

    cgpa = total_weight / total_credits

    if cgpa >= 9.0:
        grade_class = "Outstanding"
    elif cgpa >= 8.0:
        grade_class = "Excellent"
    elif cgpa >= 7.0:
        grade_class = "Very Good"
    elif cgpa >= 6.0:
        grade_class = "Good"
    elif cgpa >= 5.0:
        grade_class = "Average"
    else:
        grade_class = "Below Average"

    lines = ["=== CGPA Calculation ==="]
    for i, (g, c) in enumerate(zip(grades, credits), 1):
        lines.append(f"  Subject {i}: Grade {g} x Credits {c} = {g*c}")
    lines.append(f"  Total Credits: {total_credits}")
    lines.append(f"  CGPA: {round(cgpa, 2)}  ({grade_class})")

    return "\n".join(lines)


def calculate_percentage(obtained: float, total: float) -> str:
    """
    Calculate percentage score.

    Args:
        obtained: Marks obtained
        total: Total marks

    Returns:
        Percentage as a formatted string.
    """
    if total <= 0:
        return "Error: Total marks must be greater than 0."

    pct = (obtained / total) * 100

    if pct >= 90:
        grade = "A+"
    elif pct >= 80:
        grade = "A"
    elif pct >= 70:
        grade = "B+"
    elif pct >= 60:
        grade = "B"
    elif pct >= 50:
        grade = "C"
    elif pct >= 40:
        grade = "D"
    else:
        grade = "F (Fail)"

    return (
        f"Marks Calculation:\n"
        f"  Obtained : {obtained}\n"
        f"  Total    : {total}\n"
        f"  Percentage: {round(pct, 2)}%\n"
        f"  Grade    : {grade}"
    )


def days_to_reach_attendance(current_attended: int, current_total: int, target_pct: float = 75.0) -> str:
    """
    Calculate how many more days a student needs to attend to reach a target attendance %.

    Args:
        current_attended: Number of days currently attended
        current_total: Total working days so far
        target_pct: Target attendance percentage (default 75)

    Returns:
        Formatted string with analysis.
    """
    if current_total <= 0:
        return "Error: Total days must be greater than 0."

    current_pct = (current_attended / current_total) * 100

    if current_pct >= target_pct:
        max_total = int(current_attended * 100 / target_pct)
        can_skip = max_total - current_total
        return (
            f"Current attendance: {round(current_pct,2)}% ({current_attended}/{current_total} days)\n"
            f"Target: {target_pct}%\n"
            f"Status: Already above target!\n"
            f"You can skip up to {can_skip} more day(s) and still remain above {target_pct}%."
        )
    else:
        t = target_pct / 100
        numerator = t * current_total - current_attended
        denominator = 1 - t
        if denominator <= 0:
            return "Target percentage must be less than 100%."
        days_needed = math.ceil(numerator / denominator)
        return (
            f"Current attendance: {round(current_pct,2)}% ({current_attended}/{current_total} days)\n"
            f"Target: {target_pct}%\n"
            f"Status: Below target!\n"
            f"You need to attend at least {days_needed} more consecutive day(s) to reach {target_pct}%."
        )
