
import os
import sys
import json
from datetime import datetime

ENV_FILE_PATH = os.path.join(os.path.dirname(__file__), ".env")

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
except ImportError:
    print("[WARNING] python-dotenv not installed. Reading .env manually...")
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("\n[ERROR] GEMINI_API_KEY not set!")
    print("  1. Create a .env file in the project root")
    print("  2. Add: GEMINI_API_KEY=your_actual_api_key")
    print("  3. Get your key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.text import Text
    from rich import print as rprint
    console = Console()
    USE_RICH = True
except ImportError:
    USE_RICH = False
    console = None


try:
    import google.generativeai as genai
except ImportError:
    print("[ERROR] google-generativeai not installed.")
    print("  Run: pip install google-generativeai")
    sys.exit(1)


sys.path.insert(0, os.path.dirname(__file__))

from models.student import (
    register_student, get_student, get_attendance_summary,
    list_all_students, update_attendance
)
from tools.attendance import mark_attendance, get_attendance, get_attendance_percentage
from tools.calculator import calculate, calculate_cgpa, calculate_percentage, days_to_reach_attendance
from tools.time_analysis import get_current_time, days_until, working_days_between, get_semester_week
from tools.pdf_processor import list_uploaded_pdfs, extract_text_from_pdf, analyze_pdf_for_attendance



TOOL_DECLARATIONS_PATH = os.path.join(os.path.dirname(__file__), "tool_declarations.json")
with open(TOOL_DECLARATIONS_PATH, encoding="utf-8") as tool_declarations_file:
    TOOL_DECLARATIONS = json.load(tool_declarations_file)




TOOL_FUNCTION_MAP = {
    "mark_attendance": mark_attendance,
    "get_attendance": get_attendance,
    "get_attendance_percentage": get_attendance_percentage,
    "calculate": calculate,
    "calculate_cgpa": calculate_cgpa,
    "calculate_percentage": calculate_percentage,
    "days_to_reach_attendance": days_to_reach_attendance,
    "get_current_time": get_current_time,
    "days_until": days_until,
    "working_days_between": working_days_between,
    "get_semester_week": get_semester_week,
    "list_uploaded_pdfs": list_uploaded_pdfs,
    "extract_text_from_pdf": extract_text_from_pdf,
    "analyze_pdf_for_attendance": analyze_pdf_for_attendance,
}


def dispatch_tool(name: str, args: dict) -> str:
    """Call the appropriate tool function with given arguments."""
    func = TOOL_FUNCTION_MAP.get(name)
    if not func:
        return f"Error: Unknown tool '{name}'"
    try:
        return func(**args)
    except TypeError as e:
        return f"Error calling tool '{name}': {str(e)}"
    except Exception as e:
        return f"Tool '{name}' error: {str(e)}"




def print_banner():
    if USE_RICH:
        console.print(Panel.fit(
            "[bold cyan]College AI Assistant[/bold cyan]\n"
            "[dim]Powered by Google Gemini | Tools: Attendance, Calculator, Time, PDF[/dim]",
            border_style="cyan"
        ))
    else:
        print("=" * 60)
        print("        College AI Assistant")
        print("  Powered by Google Gemini")
        print("  Tools: Attendance | Calculator | Time | PDF")
        print("=" * 60)


def print_separator():
    if USE_RICH:
        console.print("[dim]" + "-" * 60 + "[/dim]")
    else:
        print("-" * 60)


def cprint(text, color="white", bold=False):
    if USE_RICH:
        style = ""
        if bold:
            style += "bold "
        style += color
        console.print(f"[{style}]{text}[/{style}]")
    else:
        print(text)


def get_input(prompt_text):
    if USE_RICH:
        return Prompt.ask(f"[bold green]{prompt_text}[/bold green]")
    else:
        return input(f"{prompt_text}: ")




def student_registration_menu() -> str:
    """Interactive menu to register or load a student. Returns the active roll number."""
    cprint("\n=== Student Setup ===", "cyan", bold=True)

    students = list_all_students()

    if students:
        cprint("\nExisting students:", "yellow")
        for s in students:
            print(f"  [{s['roll_number']}] {s['name']} - {s['branch']} Sem {s['semester']} | {s['attendance_percentage']}%")
        print()

    print("Options:")
    print("  1. Register new student")
    print("  2. Continue as existing student")
    if not students:
        print("  (No existing students found - please register first)")

    choice = get_input("Enter choice (1 or 2)")

    if choice.strip() == "2" and students:
        roll = get_input("Enter your roll number")
        student = get_student(roll.strip().upper())
        if student:
            cprint(f"\nWelcome back, {student['name']}!", "green", bold=True)
            return roll.strip().upper()
        else:
            cprint("Student not found. Registering new student...", "yellow")

    cprint("\n--- New Student Registration ---", "cyan")
    name = get_input("Full Name")
    roll = get_input("Roll Number (e.g. CS2023001)").upper()
    branch = get_input("Branch/Department (e.g. CSE, ECE, MECH)")
    semester = get_input("Semester (1-8)")
    total_days = get_input("Total working days this semester (enter 0 if unknown)")

    try:
        semester = int(semester)
    except ValueError:
        semester = 1
    try:
        total_days = int(total_days)
    except ValueError:
        total_days = 0

    student = register_student(
        roll_number=roll,
        name=name,
        branch=branch,
        semester=semester,
        total_working_days=total_days
    )

    cprint(f"\nStudent registered successfully!", "green", bold=True)
    print(f"  Name    : {student['name']}")
    print(f"  Roll No : {student['roll_number']}")
    print(f"  Branch  : {student['branch']}")
    print(f"  Semester: {student['semester']}")

    return roll




def create_gemini_model():
    """Initialize and return the Gemini model with tools."""
    genai.configure(api_key=GEMINI_API_KEY)

    tools = [{"function_declarations": TOOL_DECLARATIONS}]

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=tools,
        system_instruction=(
            "You are a smart College AI Assistant helping college students. "
            "You have access to tools for: attendance tracking (marking and percentage), "
            "mathematical calculations (CGPA, marks percentage, expression evaluation), "
            "time analysis (current time, days until dates, semester weeks), "
            "and PDF document processing.\n\n"
            "IMPORTANT TOOL SELECTION RULES:\n"
            "- If user asks to MARK attendance (present/absent for a day) -> use mark_attendance tool\n"
            "- If user asks for attendance PERCENTAGE or report -> use get_attendance_percentage or get_attendance tool\n"
            "- If user asks to CALCULATE something (CGPA, marks, math) -> use calculator tools\n"
            "- If user asks about TIME, DATE, days remaining -> use time analysis tools\n"
            "- If user mentions a PDF file -> use PDF tools\n"
            "- Always use the student's roll number from context when calling tools\n"
            "- Be friendly, encouraging, and use the student's name in responses\n"
            "- If attendance is below 75%, warn the student\n"
            "- Today's date is: " + datetime.now().strftime("%Y-%m-%d") + "\n"
        )
    )
    return model


def chat_with_gemini(model, chat_history: list, user_message: str, active_roll: str) -> str:
    """
    Send a message to Gemini with function calling support.
    Handles multi-turn tool calls automatically.
    """

    contextual_message = (
        f"[Active student roll number: {active_roll}]\n"
        f"Student message: {user_message}"
    )

    chat_history.append({
        "role": "user",
        "parts": [contextual_message]
    })


    chat = model.start_chat(history=chat_history[:-1])
    response = chat.send_message(contextual_message)


    max_tool_calls = 5
    tool_call_count = 0

    while response.candidates[0].content.parts:
        parts = response.candidates[0].content.parts
        has_function_call = any(hasattr(p, "function_call") and p.function_call.name for p in parts)

        if not has_function_call:
            break

        if tool_call_count >= max_tool_calls:
            break


        tool_results = []
        for part in parts:
            if hasattr(part, "function_call") and part.function_call.name:
                fc = part.function_call
                tool_name = fc.name
                tool_args = dict(fc.args) if fc.args else {}

                cprint(f"\n[Tool] Calling: {tool_name}({tool_args})", "dim")

                result = dispatch_tool(tool_name, tool_args)
                tool_results.append({
                    "function_response": {
                        "name": tool_name,
                        "response": {"result": result}
                    }
                })


        response = chat.send_message(tool_results)
        tool_call_count += 1


    final_text = ""
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text"):
            final_text += part.text


    chat_history.append({
        "role": "model",
        "parts": [final_text or "[No response]"]
    })

    return final_text or "[No response generated]"


def main():
    print_banner()

    if not os.path.exists(ENV_FILE_PATH):
        cprint("\n[NOTICE] No .env file found. Create one with your GEMINI_API_KEY.", "yellow")

    print_separator()
    active_roll = student_registration_menu()
    student = get_student(active_roll)

    print_separator()
    cprint("\nCollege AI Assistant is ready!", "green", bold=True)
    print("Type your questions naturally. Examples:")
    print("  - 'Mark me present today'")
    print("  - 'What is my attendance percentage?'")
    print("  - 'Calculate my CGPA: grades [9, 8.5, 7] credits [4, 3, 3]'")
    print("  - 'How many days until 2024-12-15?'")
    print("  - 'Analyze timetable.pdf'")
    print("  - 'help' for more options | 'quit' to exit")
    print_separator()

    try:
        model = create_gemini_model()
    except Exception as e:
        cprint(f"\n[ERROR] Failed to initialize Gemini: {e}", "red")
        sys.exit(1)

    chat_history = []

    while True:
        try:
            if USE_RICH:
                user_input = Prompt.ask(f"\n[bold green]{student['name']}[/bold green]")
            else:
                user_input = input(f"\n{student['name']} > ")
        except (KeyboardInterrupt, EOFError):
            cprint("\n\nGoodbye! Keep attending classes! ??", "cyan")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            cprint("\nGoodbye! Keep attending classes! ??", "cyan")
            break

        elif user_input.lower() == "help":
            print("\nBuilt-in commands:")
            print("  help          - Show this help")
            print("  switch        - Switch to another student")
            print("  myinfo        - Show my student profile")
            print("  listpdfs      - List uploaded PDF files")
            print("  quit/exit     - Exit the assistant")
            print("\nOr just type naturally and the AI will help you!")
            continue

        elif user_input.lower() == "switch":
            active_roll = student_registration_menu()
            student = get_student(active_roll)
            chat_history = []
            continue

        elif user_input.lower() == "myinfo":
            s = get_student(active_roll)
            summary = get_attendance_summary(active_roll)
            print(f"\n  Name    : {s['name']}")
            print(f"  Roll No : {s['roll_number']}")
            print(f"  Branch  : {s['branch']}")
            print(f"  Semester: {s['semester']}")
            print(f"  Attendance: {summary['attendance_percentage']}%")
            continue

        elif user_input.lower() == "listpdfs":
            print(list_uploaded_pdfs())
            continue

        try:
            if USE_RICH:
                with console.status("[bold cyan]Thinking...[/bold cyan]"):
                    response = chat_with_gemini(model, chat_history, user_input, active_roll)
            else:
                print("Thinking...")
                response = chat_with_gemini(model, chat_history, user_input, active_roll)

            print_separator()
            if USE_RICH:
                console.print(f"\n[bold blue]Assistant:[/bold blue] {response}")
            else:
                print(f"\nAssistant: {response}")
            print_separator()

        except Exception as e:
            cprint(f"\n[ERROR] {str(e)}", "red")
            if "API_KEY" in str(e).upper():
                cprint("Please check your GEMINI_API_KEY in the .env file.", "yellow")


if __name__ == "__main__":
    main()
