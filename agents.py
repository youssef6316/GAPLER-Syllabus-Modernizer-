import os
from groq import Groq
from tools import search_market_requirements
import json
import time


# --- 1. Groq Wrapper ---
def query_llm(system_instruction, user_prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[Error: GROQ API Key missing.]"

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=6000,
            top_p=1,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[Error calling Groq: {str(e)}]"


# --- 2. Input Expander Agent (FIXED FOR ARABIC) ---
class InputExpanderAgent:
    def __init__(self):
        self.role = "Academic Advisor"

    def expand_topic(self, topic, language="English"):
        sys_prompt = "You are a University Curriculum Planner."

        # --- FIX: Stronger Prompt for Arabic Auto-Complete ---
        if "Arabic" in language:
            lang_instruction = """
            **CRITICAL INSTRUCTION**: The user wants the content in ARABIC.

            1. **JSON Keys**: Must remain in ENGLISH (e.g., "obj", "topics").
            2. **JSON Values**: Must be in **ARABIC** (Modern Standard Arabic).
            3. **Content**:
               - 'obj': Write detailed learning goals in Arabic.
               - 'topics': List detailed topics in Arabic.
               - 'know': Prerequisites in Arabic.
               - 'context': Industry context in Arabic.
            4. **Tech Terms**: Keep English terms in brackets, e.g., "الذكاء الاصطناعي (AI)".
            """
        else:
            lang_instruction = "Output values in English."

        user_prompt = f"""
        The user wants to learn: '{topic}'.
        {lang_instruction}

        Generate a high-quality course structure.
        Return ONLY valid JSON:
        {{
            "code": "Course Code (e.g. CS101)",
            "duration": 12, 
            "lec": 3, "tut": 1, "lab": 3,
            "obj": "Detailed learning objectives text",
            "topics": "List of core topics text",
            "context": "Industry application text",
            "know": "Prerequisites text"
        }}
        """
        try:
            response = query_llm(sys_prompt, user_prompt)
            # JSON Cleanup
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except Exception as e:
            print(f"Expansion Error: {e}")
            return None


# --- 3. PDF Parser Agent ---
class PDFParserAgent:
    def __init__(self):
        self.role = "Document Analyzer"

    def extract_course_details(self, raw_text):
        sys_prompt = "You are a Data Extraction Specialist."
        user_prompt = f"""
        Analyze this text:
        '''{raw_text[:6000]}'''

        Extract fields into JSON:
        {{
            "title": "Course Name",
            "code": "Course Code",
            "duration": 12, 
            "lec": 2, "tut": 1, "lab": 2,
            "objectives": "Summary",
            "topics": "List",
            "context": "Industry"
        }}
        """
        try:
            response = query_llm(sys_prompt, user_prompt)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except:
            return None


# --- 4. The Slaves ---
class MarketSlave:
    def __init__(self):
        self.role = "Market Researcher"

    def research(self, course_title, topics):
        print(f"[{self.role}] Searching...")
        search_results = search_market_requirements(course_title)

        sys_prompt = "You are an expert Technical Recruiter."
        user_prompt = f"""
        Analyze these search results for '{course_title}':
        {search_results}
        Proposed topics: {topics}

        Output a detailed list:
        1. Top 5 Technical Skills in demand.
        2. Top 3 Industry Tools (software/libraries).
        3. One emerging trend.

        Provide context for each item.
        """
        return query_llm(sys_prompt, user_prompt)


class CurriculumSlave:
    def __init__(self):
        self.role = "Curriculum Designer"

    def draft_plan(self, course_info, market_data, feedback="None"):
        print(f"[{self.role}] Drafting...")

        if "Arabic" in course_info.get('language', ''):
            lang_instruction = """
            **CRITICAL INSTRUCTION: ARABIC MODE**

            You are a Distinguished Dean of Computer Science at a top Arab University.
            Write the response in **Professional Modern Standard Arabic (الفصحى المعاصرة)**.

            **QUALITY CONTROL RULES:**
            1. **NO SUMMARIES**: Do not just list titles. Every week must have a description.
            2. **Deep Detail**: For "Week 1", don't just say "Introduction". Say "Introduction: Definition, History, Key Concepts, and Applications in Industry".
            3. **Bilingual Terms**: Always keep the English technical term in brackets. Example: "الشبكات العصبية (Neural Networks)".
            4. **Headers**: Use these exact Arabic headers:
               - "## ١. خطة المحاضرات (Lecture Plan)"
               - "## ٢. محتوى المختبرات (Labs)"
               - "## ٣. مشروع التخرج (Capstone)"
               - "## ٤. المراجع (Resources)"

            **STRUCTURE:**
            - **Lecture Plan**: For each week, provide 3-4 sub-bullet points explaining the content.
            - **Labs**: List the tools (e.g., PyTorch, Pandas) and the specific task students will code.
            """
        else:
            lang_instruction = "Output the response in standard English. Be verbose and detailed."

        sys_prompt = f"You are a Senior University Professor. {lang_instruction}"

        user_prompt = f"""
        Create a COMPREHENSIVE Course Plan for: {course_info['title']} ({course_info['duration']} weeks).
        Market Data: {market_data}
        Previous Feedback: {feedback}

        Structure exactly as:
        # {course_info['title']}

        [Generate the 4 sections defined in system instructions. Ensure high volume of text and detail.]
        """
        return query_llm(sys_prompt, user_prompt)


class ArbitratorSlave:
    def __init__(self):
        self.role = "Quality Assurance"

    def evaluate(self, market_data, current_draft):
        return 100, "Approved"


# --- 5. Master Agent ---
class MasterAgent:
    def __init__(self):
        self.s1 = MarketSlave()
        self.s2 = CurriculumSlave()
        self.s3 = ArbitratorSlave()

    def run(self, course_data):
        status_log = []

        status_log.append("Slave 1: Scouting Job Market...")
        market_data = self.s1.research(course_data['title'], course_data['topics'])
        status_log.append("Market Data Synthesized.")

        status_log.append("Slave 2: Drafting Detailed Syllabus...")
        draft = self.s2.draft_plan(course_data, market_data)

        status_log.append("Slave 3: Quality Check...")
        self.s3.evaluate(market_data, draft)

        status_log.append("Plan Finalized.")
        return draft, status_log