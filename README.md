# College AI Assistant

A command-line assistant for college students, powered by Google Gemini. It can manage attendance, calculate grades and percentages, answer date-related questions, and read PDFs from the local uploads folder.

## Features

- Register student profiles and track attendance by date.
- View attendance reports and percentage, including the 75% threshold.
- Calculate expressions, CGPA, marks percentages, and days needed to reach an attendance target.
- Check dates, semester weeks, and working days.
- List, read, and analyze PDF files placed in `uploads/`.
- Use natural language to ask questions; Gemini selects the relevant tool.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- Packages listed in `requirements.txt`

## Setup on Windows

1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Open PowerShell in the project folder and run:

   ```powershell
   .\setup.ps1
   ```

3. Edit `.env` and replace the placeholder with your key:

   ```text
   GEMINI_API_KEY=your_actual_api_key
   ```

4. Activate the environment and start the assistant:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python main.py
   ```

The setup script creates the virtual environment, installs dependencies, creates `.env` if needed, and ensures the data and uploads folders exist.

## Setup on macOS or Linux

Run these commands from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder containing:

```text
GEMINI_API_KEY=your_actual_api_key
```

Then run:

```bash
python main.py
```

## Using the Assistant

On the first run, choose the option to register a student and enter their name, roll number, branch, semester, and total working days. Later runs can continue with an existing student profile.

Example questions:

- `Mark me present today`
- `What is my attendance percentage?`
- `Calculate my CGPA: grades [9, 8.5, 7] credits [4, 3, 3]`
- `How many days until 2026-12-20?`
- `Read timetable.pdf`

Built-in commands:

| Command | Description |
| --- | --- |
| `help` | Show available commands |
| `switch` | Switch to another student profile |
| `myinfo` | Show the active student profile and attendance |
| `listpdfs` | List PDFs in the uploads folder |
| `quit`, `exit`, or `bye` | Exit the assistant |

## Project Files

| Path | Purpose |
| --- | --- |
| `main.py` | CLI, Gemini chat, and tool dispatch |
| `tool_declarations.json` | Gemini function declarations |
| `models/student.py` | Student profiles and attendance persistence |
| `tools/attendance.py` | Attendance functions |
| `tools/calculator.py` | Calculation functions |
| `tools/time_analysis.py` | Date and semester functions |
| `tools/pdf_processor.py` | PDF listing and text extraction |
| `data/students.json` | Local student data, created as needed |
| `uploads/` | Folder for PDFs to analyze |
| `setup.ps1` | Windows environment setup script |

Student records are stored locally. Keep `.env` private and do not share your Gemini API key.
