import streamlit as st
import time
from agents import MasterAgent, PDFParserAgent, InputExpanderAgent
from tools import create_course_pdf
import os
import PyPDF2

# --- CONFIGURATION: API KEY (HIDDEN) ---
if "GROQ_API_KEY" not in os.environ:
    # Replace with your actual key if not set in environment variables
    os.environ["GROQ_API_KEY"] = "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"

st.set_page_config(page_title="GAPLER - Student Learning Path", layout="wide", page_icon="🎓")

# --- UI TEXT CONSTANTS ---
UI = {
    # Sidebar
    "sb_guide_title": "📖 Quick Guide",
    "sb_steps": "**Steps:**\n1. Enter course details\n2. List topics to cover\n3. Define learning goals\n4. Click Generate\n5. Download PDF",
    "sb_tips": "**Tips:**\n- Be specific with topics\n- Include current level\n- Mention industry focus\n- Add any constraints",
    "sb_about_title": "ℹ️ About System",
    "sb_about_text": "**GAPLER** uses AI to align your course with job market needs.\n\n**Powered by:**\n- Google GROQ API\n- Multi-Agent System\n- Live Market Research",
    "sb_status_title": "📊 System Status",
    "sb_status_msg": "✅ All systems operational",
    "sb_metric_lbl": "Avg. Processing Time",
    "sb_metric_val": "~1 min",
    "sb_input_title": "Input Method",

    # Input Methods
    "method_manual": "Manual Entry",
    "method_pdf": "Fast Mode (PDF Upload)",

    # Headers
    "header_title": "🚀 GAPLER: Career-Aligned Learning Path",
    "header_caption": "Tell us what you want to learn, and we'll build a market-ready syllabus for you.",
    "subheader_goal": "🎯 What is your Learning Goal?",

    # Form Labels
    "lbl_subject": "Core Subject",
    "ph_subject": "e.g. Deep Learning, Full Stack Web Dev...",
    "lbl_duration": "Duration (Weeks)",
    "lbl_hours": "Study Hours / Week",
    "lbl_lec": "Reading",
    "lbl_tut": "Tutorials",
    "lbl_lab": "Coding/Lab",
    "lbl_obj": "Career Objectives",
    "ph_obj": "e.g. I want to work as a Data Scientist...",
    "lbl_know": "Current Knowledge",
    "ph_know": "e.g. Basic Python...",
    "lbl_topics": "Specific Topics",
    "ph_topics": "- Neural Networks\n- Transformers...",
    "lbl_context": "Industry Focus",
    "ph_context": "e.g. Medical, Finance...",

    # Actions
    "btn_gen": "✨ Generate Personalized Study Plan",
    "btn_auto": "✨ Auto-Complete",
    "err_fill": "⚠️ Please fill in Subject and Objectives.",
    "err_no_topic": "⚠️ Please enter a Core Subject first.",
    "status_init": "🤖 AI Agents are researching...",
    "status_build": "Building your roadmap...",
    "success_ready": "Roadmap Ready!",
    "success_msg": "Here is your personalized plan!",
    "tab_plan": "📄 Study Plan",
    "tab_pdf": "📥 Download PDF",

    # PDF Upload
    "pdf_label": "Upload Course Spec (PDF)",
    "pdf_btn": "⚡ Analyze & Auto-Fill",
    "pdf_success": "PDF Analyzed! Form auto-filled.",
    "pdf_err": "Could not read PDF."
}

# --- SESSION STATE ---
if 'form_data' not in st.session_state:
    st.session_state['form_data'] = {
        "title": "", "duration": 12,
        "lec": 1, "tut": 2, "lab": 2,
        "obj": "", "know": "", "topics": "", "context": ""
    }

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730; color: white; border: 1px solid #4f4f4f;
    }

    /* Center Main Headers */
    h1, h2, h3 { text-align: center !important; }

    /* Center Sidebar Headers */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { 
        text-align: center !important; 
    }

    /* Increase Input Label Font Size */
    .stTextInput label p, .stTextArea label p, .stNumberInput label p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }

    /* Metric Alignment */
    [data-testid="stMetricLabel"] { justify-content: center; }
    [data-testid="stMetricValue"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    # st.image("https://img.icons8.com/color/96/student-center.png", width=120)

    # st.markdown("---")

    # Quick Guide
    st.markdown(f"### {UI['sb_guide_title']}")
    st.markdown(UI['sb_steps'])
    st.info(UI['sb_tips'])

    st.markdown("---")

    # About
    st.markdown(f"### {UI['sb_about_title']}")
    st.markdown(UI['sb_about_text'])

    st.markdown("---")

    # System Status
    st.markdown(f"### {UI['sb_status_title']}")
    st.success(UI['sb_status_msg'])
    st.metric(UI['sb_metric_lbl'], UI['sb_metric_val'])

    st.markdown("---")

    # Input Type Toggle
    st.markdown(f"### {UI['sb_input_title']}")
    input_method = st.radio("input_method_hidden", [UI["method_manual"], UI["method_pdf"]],
                            label_visibility="collapsed")
    is_pdf_mode = (input_method == UI["method_pdf"])

# --- MAIN HEADER ---
st.title(UI["header_title"])
st.markdown(f"""
    <div style="text-align: center; color: #a3a8b8; font-size: 1.2em; margin-top: -20px; margin-bottom: 30px;">
        {UI['header_caption']}
    </div>
    """, unsafe_allow_html=True)

with st.expander("ℹ️ About GAPLER", expanded=False):
    st.markdown("""
    **CMAS** uses advanced AI agents to align your course content with current job market requirements.

    **How it works:**
    1. 🔍 **Job Market Analyzer** - Researches current industry requirements
    2. 📚 **Content Curator** - Designs market-aligned curriculum  
    3. ⚖️ **Alignment Arbiter** - Validates quality and alignment
    4. 📄 **Output Generator** - Creates comprehensive course plan PDF

    **What you get:**
    - Week-by-week lecture plan
    - Practical laboratory sessions
    - Industry-relevant capstone project
    - Current learning resources (2024-2026)
    - Market alignment analysis
    """)

# --- LOGIC: PDF MODE ---
if is_pdf_mode:
    st.info(f"💡 {UI['method_pdf']}")
    uploaded_file = st.file_uploader(UI["pdf_label"], type="pdf")

    if uploaded_file and st.button(UI["pdf_btn"]):
        with st.spinner("Reading PDF..."):
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "".join([p.extract_text() for p in reader.pages])
                parser = PDFParserAgent()
                data = parser.extract_course_details(text)
                if data:
                    st.session_state['form_data'].update(data)
                    st.session_state['form_data']['duration'] = int(data.get('duration', 12))
                    st.success(UI["pdf_success"])
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"{UI['pdf_err']}: {e}")

# --- LOGIC: MANUAL MODE ---
else:
    st.subheader(UI["subheader_goal"])

    # 1. Subject & Auto-Complete (Aligned)
    c_title, c_btn = st.columns([4, 1], vertical_alignment="bottom")

    with c_title:
        course_title = st.text_input(UI["lbl_subject"],
                                     value=st.session_state['form_data']['title'],
                                     placeholder=UI["ph_subject"],
                                     key="title_input")

    with c_btn:
        if st.button(UI["btn_auto"], use_container_width=True):
            if not course_title:
                st.warning(UI["err_no_topic"])
            else:
                with st.spinner("✨"):
                    expander = InputExpanderAgent()
                    data = expander.expand_topic(course_title)
                    if data:
                        st.session_state['form_data']['title'] = course_title
                        st.session_state['form_data']['duration'] = int(data.get('duration', 12))
                        st.session_state['form_data']['lec'] = int(data.get('lec', 3))
                        st.session_state['form_data']['tut'] = int(data.get('tut', 1))
                        st.session_state['form_data']['lab'] = int(data.get('lab', 3))
                        st.session_state['form_data']['obj'] = data.get('obj', '')
                        st.session_state['form_data']['topics'] = data.get('topics', '')
                        st.session_state['form_data']['context'] = data.get('context', '')
                        st.session_state['form_data']['know'] = data.get('know', '')
                        st.rerun()

    # 2. Other Inputs
    c1, c2 = st.columns(2)
    with c1:
        duration = st.number_input(UI["lbl_duration"], min_value=1, value=st.session_state['form_data']['duration'])

        st.markdown(f"##### **{UI['lbl_hours']}**")
        h1, h2, h3 = st.columns(3)
        lec = h1.number_input(UI["lbl_lec"], min_value=1, value=st.session_state['form_data']['lec'])
        tut = h2.number_input(UI["lbl_tut"], min_value=0, value=st.session_state['form_data']['tut'])
        lab = h3.number_input(UI["lbl_lab"], min_value=0, value=st.session_state['form_data']['lab'])

    with c2:
        objectives = st.text_area(UI["lbl_obj"], value=st.session_state['form_data']['obj'], placeholder=UI["ph_obj"],
                                  height=140)
        resources = st.text_area(UI["lbl_know"], value=st.session_state['form_data']['know'], placeholder=UI["ph_know"],
                                 height=100)

    st.markdown("---")
    topics = st.text_area(UI["lbl_topics"], value=st.session_state['form_data']['topics'], placeholder=UI["ph_topics"],
                          height=150)
    context = st.text_input(UI["lbl_context"], value=st.session_state['form_data']['context'],
                            placeholder=UI["ph_context"])

# --- GENERATE ACTION ---
st.markdown("---")
if st.button(UI["btn_gen"]):
    if not course_title or not objectives:
        st.warning(UI["err_fill"])
    elif "PASTE_YOUR" in os.environ.get("GROQ_API_KEY", ""):
        st.error("🚨 System Error: Please set the GROQ API Key in app.py")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        master = MasterAgent()

        course_data = {
            "title": course_title,
            "duration": duration,
            "lec": lec, "tut": tut, "lab": lab,
            "topics": topics,
            "objectives": objectives + f" ({context})",
            "language": "English"
        }

        status_text.text(UI["status_init"])
        time.sleep(1)
        progress_bar.progress(10)

        with st.spinner(UI["status_build"]):
            try:
                final_plan, logs = master.run(course_data)
                for i, log in enumerate(logs):
                    time.sleep(0.5)
                    prog = min(90, 10 + (i * 25))
                    progress_bar.progress(prog)

                progress_bar.progress(100)
                status_text.success(UI["success_ready"])
                st.success(f"{UI['success_msg']} ({course_title})")

                tab1, tab2 = st.tabs([UI["tab_plan"], UI["tab_pdf"]])
                with tab1:
                    st.markdown(final_plan)
                with tab2:
                    pdf_file = create_course_pdf(course_data, final_plan)
                    with open(pdf_file, "rb") as f:
                        st.download_button(UI["tab_pdf"], f, file_name=pdf_file, mime="application/pdf")
            except Exception as e:
                st.error(f"Error: {e}")