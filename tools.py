import os
from duckduckgo_search import DDGS
from fpdf import FPDF


# --- Tool 1: Internet Search ---
def search_market_requirements(query):
    """
    Searches for job requirements relevant to the course using DuckDuckGo.
    """
    try:
        # Searching for 'job requirements' specifically
        results = DDGS().text(f"{query} job requirements skills 2025", max_results=5)
        summary = ""
        for r in results:
            summary += f"- {r['title']}: {r['body']}\n"
        return summary
    except Exception as e:
        return f"Search tool warning: {str(e)}. Proceeding with internal knowledge."


# --- Tool 2: PDF Generator ---
class ReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'CMAS - Market-Aligned Course Plan', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def create_course_pdf(course_data, plan_content):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Course Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Course: {course_data['title']} ({course_data['code']})", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 10,
                   f"Duration: {course_data['duration']} weeks | Lec: {course_data['lec']}h | Tut: {course_data['tut']}h | Lab: {course_data['lab']}h")
    pdf.ln(5)

    # Content Body
    # Note: Standard FPDF does not support Arabic characters.
    # For a hackathon, output English, or use a library like 'reportlab' with .ttf fonts for Arabic.
    pdf.set_font("Arial", "", 11)

    # Clean text to prevent latin-1 encoding errors common in PDFs
    clean_content = plan_content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, clean_content)

    filename = f"CMAS_{course_data['code']}_Plan.pdf"
    pdf.output(filename)
    return filename
