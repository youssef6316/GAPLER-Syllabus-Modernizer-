import os
from groq import Groq
from tools import search_market_requirements
import json
import re
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


# --- 2. Input Expander Agent ---
class InputExpanderAgent:
    def __init__(self):
        self.role = "Academic Advisor"

    def expand_topic(self, topic, language="English"):
        sys_prompt = "You are a University Curriculum Planner."

        if "Arabic" in language:
            lang_instruction = """
            **CRITICAL INSTRUCTION**: The user wants the content in ARABIC.
            1. **JSON Keys**: Must remain in ENGLISH.
            2. **JSON Values**: Must be in **ARABIC**.
            3. **Tech Terms**: Keep English terms in brackets.
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

    def draft_plan(self, course_info, market_data, feedback=None):
        print(f"[{self.role}] Drafting/Refining...")

        # Determine Language Context
        if "Arabic" in course_info.get('language', ''):
            lang_instruction = """
            **CRITICAL INSTRUCTION: ARABIC MODE**
            You are a Distinguished Dean of Computer Science.
            Write in **Professional Modern Standard Arabic**.

            **Formatting Rules:**
            1. Headers: "## ١. خطة المحاضرات (Lecture Plan)", "## ٢. محتوى المختبرات (Labs)".
            2. Content: Detailed, verbose, no summaries.
            3. Terms: Keep English technical terms in brackets.
            """
        else:
            lang_instruction = "Output the response in standard English. Be verbose and detailed."

        # Determine if this is a First Draft or a Revision
        if feedback and feedback != "None" and feedback != "":
            task_context = f"""
            **TASK: REFINE EXISTING PLAN**
            The previous draft was evaluated.
            **CRITICAL FEEDBACK TO ADDRESS:** {feedback}

            Re-write the course plan to specifically address the gaps identified above while maintaining the original structure.
            """
        else:
            task_context = f"""
            **TASK: CREATE FIRST DRAFT**
            Create a comprehensive course plan based on the market data provided.
            """

        sys_prompt = f"You are a Senior University Professor. {lang_instruction}"

        user_prompt = f"""
        {task_context}

        Course Title: {course_info['title']} ({course_info['duration']} weeks).
        Market Data: {market_data}

        Structure exactly as:
        # {course_info['title']}
        ## 1. Lecture Plan (Week by Week)
        ## 2. Labs Content (Hands-on tasks)
        ## 3. Capstone Project
        ## 4. Resources
        """
        return query_llm(sys_prompt, user_prompt)


class ArbitratorSlave:
    def __init__(self):
        self.role = "Quality Assurance"

    def evaluate(self, market_data, current_draft):
        """
        Evaluates the draft and returns (score, feedback).
        """
        system_instruction = (
            "You are an expert Academic-Industry Arbitrator. "
            "Evaluate the curriculum draft against the market requirements. "
            "Format response: SCORE: [0-100] | FEEDBACK: [Detailed critique]"
        )

        user_prompt = f"""
        ### JOB MARKET DATA:
        {market_data}

        ### PROPOSED DRAFT:
        {current_draft}

        Task:
        1. Compare the Draft against the Market Data.
        2. Are specific tools (from market data) missing in the Labs?
        3. Is the Capstone relevant?
        4. Give a Score (0-100). If < 85, list specific missing topics to fix.
        """

        try:
            # FIX: swapped arguments to correct order (system, user)
            response = query_llm(system_instruction, user_prompt)

            # Extract Score
            score_match = re.search(r"SCORE:\s*(\d+)", response)
            score = int(score_match.group(1)) if score_match else 0

            # Extract Feedback
            if "FEEDBACK:" in response:
                feedback = response.split("FEEDBACK:")[-1].strip()
            elif "|" in response:
                feedback = response.split("|")[-1].strip()
            else:
                feedback = response

            return score, feedback

        except Exception as e:
            return 0, f"Error in evaluation: {str(e)}"


# --- 5. Master Agent ---
class MasterAgent:
    def __init__(self):
        self.s1 = MarketSlave()
        self.s2 = CurriculumSlave()
        self.s3 = ArbitratorSlave()

    def run(self, course_data):
        status_log = []

        # 1. Market Research (Once)
        status_log.append("Slave 1: Scouting Job Market...")
        market_data = self.s1.research(course_data['title'], course_data['topics'])
        status_log.append("Market Data Synthesized.")

        # 2. Iterative Loop
        score = 0
        feedback = None
        iteration = 0
        max_attempts = 3  # Kept to 3 to avoid long wait times
        draft = ""

        while score < 85 and iteration < max_attempts:
            iteration += 1
            status_log.append(f"--- Iteration {iteration} ---")

            if feedback:
                status_log.append("Slave 2: Refining Draft based on Feedback...")
            else:
                status_log.append("Slave 2: Drafting Initial Syllabus...")

            # Pass feedback to the drafter
            draft = self.s2.draft_plan(course_data, market_data, feedback)

            # Evaluate
            status_log.append("Slave 3: Evaluating Quality...")
            score, feedback = self.s3.evaluate(market_data, draft)

            status_log.append(f"Arbitrator Score: {score}/100")

            if score < 85:
                status_log.append("Feedback sent to drafter for improvements.")
            else:
                status_log.append("Quality Target Met!")

        status_log.append("Plan Finalized.")
        return draft, status_log