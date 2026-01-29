from duckduckgo_search import DDGS
# Import your new generator entry point
from pdf_generator import generate_course_plan_pdf


# --- Tool 1: Internet Search ---
def search_market_requirements(query):
    """
    Searches for job requirements relevant to the course.
    """
    try:
        results = DDGS().text(f"{query} job requirements skills 2024 2025", max_results=5)
        summary = ""
        for r in results:
            summary += f"- {r['title']}: {r['body']}\n"
        return summary
    except Exception as e:
        return f"Search tool warning: {str(e)}. Using general knowledge."


# --- Tool 2: PDF Parsing & Bridge ---
def create_course_pdf(course_data, plan_text):
    """
    Converts the raw text from AI into the structured dict required by CMASPDFGenerator.
    """

    # 1. Prepare Base Metadata
    content_data = {
        'title': course_data['title'],
        'duration': f"{course_data['duration']} Weeks",
        'weekly_load': f"Lec: {course_data['lec']}h | Lab: {course_data['lab']}h",
        'sections': []
    }

    # 2. Parse the Markdown Text into Sections
    # We look for lines starting with '#' to create sections
    lines = plan_text.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line: continue

        # Main Section Header (e.g., # Lecture Plan)
        if line.startswith('# '):
            clean_title = line.replace('#', '').strip()
            # Save previous section if exists
            if current_section:
                content_data['sections'].append(current_section)

            # Start new section
            current_section = {
                'title': clean_title,
                'content': []
            }
            continue

        # Sub Headers (e.g., ## Week 1)
        if line.startswith('##'):
            clean_sub = line.replace('#', '').strip()
            if current_section:
                current_section['content'].append({
                    'type': 'header',
                    'text': clean_sub
                })
            continue

        # Bullet Points
        if line.startswith('- ') or line.startswith('* '):
            clean_item = line.replace('-', '').replace('*', '').strip()
            if current_section:
                current_section['content'].append({
                    'type': 'bullet',
                    'text': clean_item
                })
            continue

        # Normal Text
        if current_section:
            # Simple bold removal for PDF cleanliness
            clean_text = line.replace('**', '')
            current_section['content'].append({
                'type': 'text',
                'text': clean_text
            })

    # Append the last section
    if current_section:
        content_data['sections'].append(current_section)

    # 3. Generate PDF
    filename = f"{course_data['title']}_Plan.pdf"
    generate_course_plan_pdf(filename, content_data)

    return filename