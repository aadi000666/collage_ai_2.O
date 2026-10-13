"""
PDF Processor Tool - extracts and analyzes text from uploaded PDF files.
Used by the LLM as a function-calling tool.
"""
import os
import sys

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")


def list_uploaded_pdfs() -> str:
    """
    List all PDF files that have been uploaded.

    Returns:
        A formatted list of available PDF filenames.
    """
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    pdfs = [f for f in os.listdir(UPLOADS_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        return "No PDF files found in the uploads folder. Please add a PDF to the 'uploads/' directory."
    lines = ["Available PDFs:"]
    for i, p in enumerate(pdfs, 1):
        size = os.path.getsize(os.path.join(UPLOADS_DIR, p))
        lines.append(f"  {i}. {p} ({size // 1024} KB)")
    return "\n".join(lines)


def extract_text_from_pdf(filename: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        filename: Name of the PDF file (must be in the uploads/ folder)

    Returns:
        Extracted text content as a string.
    """
    try:
        import pypdf
    except ImportError:
        try:
            import PyPDF2 as pypdf
        except ImportError:
            return "Error: PDF library not installed. Run: pip install pypdf"

    if os.path.sep in filename or "/" in filename or ".." in filename:
        return "Error: Invalid filename. Please provide just the filename, not a path."

    filepath = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return (
            f"Error: '{filename}' not found in uploads/ folder.\n"
            f"Available files:\n" + list_uploaded_pdfs()
        )

    try:
        text_pages = []
        with open(filepath, "rb") as f:
            try:
                reader = pypdf.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    text_pages.append(f"--- Page {i+1} ---\n{page_text}")
            except Exception:
                import PyPDF2
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    text_pages.append(f"--- Page {i+1} ---\n{page_text}")

        full_text = "\n\n".join(text_pages)
        if not full_text.strip():
            return f"Warning: No text could be extracted from '{filename}'. The PDF may be scanned/image-based."

        MAX_CHARS = 8000
        if len(full_text) > MAX_CHARS:
            full_text = full_text[:MAX_CHARS] + f"\n\n[... Truncated. Total characters: {len(full_text)}]"

        return f"Content extracted from '{filename}':\n\n{full_text}"

    except Exception as e:
        return f"Error reading PDF '{filename}': {str(e)}"


def analyze_pdf_for_attendance(filename: str) -> str:
    """
    Extract attendance or schedule data from a PDF.
    Looks for common patterns like dates, student names, and present/absent marks.

    Args:
        filename: Name of the PDF file in uploads/ folder

    Returns:
        Extracted and formatted attendance-related information.
    """
    raw = extract_text_from_pdf(filename)
    if raw.startswith("Error") or raw.startswith("Warning"):
        return raw

    return (
        f"PDF Analysis for '{filename}':\n\n"
        f"{raw}\n\n"
        f"[The LLM will process this content and extract relevant attendance information.]"
    )
