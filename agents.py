import os
from groq import Groq
from tools import search_market_requirements
import time


# --- 1. Groq Wrapper (Fast & High Quality) ---

def query_llm(system_instruction, user_prompt):
    # 1. Setup
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[Error: GROQ API Key missing. Please check sidebar.]"

    try:
        client = Groq(api_key=api_key)

        # We use Llama 3.3 70B for maximum quality (Smart like GPT-4)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,  # Allows for long, detailed syllabi
            top_p=1,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"[Error calling Groq: {str(e)}]"


# --- 2. Slaves (Restored to High Detail Mode) ---

class MarketSlave:
    def __init__(self):
        self.role = "Market Researcher"

    def research(self, course_title, topics):
        print(f"[{self.role}] Searching...")
        search_results = search_market_requirements(course_title)

        sys_prompt = "You are an expert Technical Recruiter and Market Analyst."
        # Detailed Prompt restored
        user_prompt = f"""
        Analyze these search results for the course topic '{course_title}':
        {search_results}

        Also consider these proposed topics: {topics}

        Output a detailed list of:
        1. Top 5 Technical Skills currently in demand.
        2. Top 3 Industry Tools (libraries, software) used in 2024/2025.
        3. One emerging trend relevant to this field.
        """
        return query_llm(sys_prompt, user_prompt)


class CurriculumSlave:
    def __init__(self):
        self.role = "Curriculum Designer"

    def draft_plan(self, course_info, market_data, feedback="None"):
        print(f"[{self.role}] Drafting...")

        lang_instruction = ""
        if course_info.get('language') == "Arabic (Egyptian Style)":
            lang_instruction = "Output the response in Arabic, using a professional yet accessible Egyptian Academic style."

        sys_prompt = f"You are a Senior University Professor and Curriculum Strategist. {lang_instruction}"

        # Restored the request for "Detailed" output
        user_prompt = f"""
        Create a Comprehensive Course Plan for: {course_info['title']} ({course_info['duration']} weeks).
        Context from Market Research: {market_data}
        Previous Feedback (if any): {feedback}

        Structure the output exactly as:
        # {course_info['title']}

        ## 1. Lecture Plan (Week by Week)
        Provide detailed topics and sub-topics for every week.

        ## 2. Labs Content
        Hands-on tasks linked to the industry tools found. Be specific about what students will code.

        ## 3. Capstone Project
        A real-world scenario testing market needs. Describe the problem, dataset, and deliverables.

        ## 4. Course Book & Resources
        The newest accessible books and online repos.
        """
        return query_llm(sys_prompt, user_prompt)


class ArbitratorSlave:
    def __init__(self):
        self.role = "Quality Assurance"

    def evaluate(self, market_data, current_draft):
        # We can enable this again because Groq is fast enough!
        sys_prompt = "You are a strict Accreditation Auditor."
        user_prompt = f"""
        Compare Market Needs vs Course Draft.
        Market: {market_data}
        Draft: {current_draft[:1000]}...

        Output: "APPROVED" if it looks good, otherwise brief feedback.
        """
        response = query_llm(sys_prompt, user_prompt)
        if "APPROVED" in response: return 100, "Approved"
        return 90, "Good"


# --- 3. Master Agent ---

class MasterAgent:
    def __init__(self):
        self.s1 = MarketSlave()
        self.s2 = CurriculumSlave()
        self.s3 = ArbitratorSlave()

    def run(self, course_data):
        status_log = []

        # Phase 1
        status_log.append("Slave 1: Scouting Job Market (Groq Llama-3)...")
        market_data = self.s1.research(course_data['title'], course_data['topics'])
        status_log.append("Market Data Synthesized.")

        # Phase 2
        status_log.append("Slave 2: Drafting Detailed Syllabus...")
        draft = self.s2.draft_plan(course_data, market_data)

        # Phase 3
        status_log.append("Slave 3: Quality Check...")
        score, feedback = self.s3.evaluate(market_data, draft)
        status_log.append(f"Quality Score: {score}/100")

        status_log.append("Plan Finalized.")

        return draft, status_log
