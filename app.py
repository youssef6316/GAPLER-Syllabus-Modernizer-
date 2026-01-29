import streamlit as st
import time
from agents import MasterAgent, PDFParserAgent, InputExpanderAgent
from tools import create_course_pdf
import os
import PyPDF2

# --- CONFIGURATION: API KEY (HIDDEN) ---
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "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"

st.set_page_config(page_title="GAPLER - Student Learning Path", layout="wide", page_icon="🎓")

# --- LOCALIZATION DICTIONARY ---
UI_TEXT = {
    "en": {
        # Sidebar Titles
        "sb_lang_title": "🌐 Language",
        "sb_guide_title": "📖 Quick Guide",
        "sb_about_title": "ℹ️ About System",
        "sb_status_title": "📊 System Status",
        "sb_input_title": "Input Method",

        # Sidebar Content
        "sb_steps_md": """
        **Steps:**
        1. Enter course details
        2. List topics to cover
        3. Define learning goals
        4. Click Generate
        5. Download PDF
        """,
        "sb_tips_md": """
        **Tips:**
        - Be specific with topics
        - Include current level
        - Mention industry focus
        - Add any constraints
        """,
        "sb_about_md": """
        **GAPLER** uses AI to align your course with job market needs.

        **Powered by:**
        - GROQ API (Llama 3)
        - Multi-Agent System
        - Live Market Research
        """,
        "sb_status_ok": "✅ All systems operational",
        "sb_metric_time": "~1 min",
        "sb_metric_lbl": "Avg. Processing Time",

        # Input Methods
        "method_manual": "Manual Entry",
        "method_pdf": "Fast Mode (PDF Upload)",

        # Main Headers
        "mode_student": "🎓 **Student Mode Active**",
        "header_title": "🚀 GAPLER: Career-Aligned Learning Path",
        "header_caption": "Tell us what you want to learn, and we'll build a market-ready syllabus for you.",

        # Form Labels
        "subheader_goal": "🎯 What is your Learning Goal?",
        "lbl_subject": "Core Subject",
        "ph_subject": "e.g. Deep Learning, Full Stack Web Dev...",
        "lbl_code": "Academic Level / Code",
        "ph_code": "e.g. CS101, Senior Project...",
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

        # Buttons & Messages
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
        "pdf_label": "Upload Course Spec (PDF)",
        "pdf_btn": "⚡ Analyze & Auto-Fill",
        "pdf_success": "PDF Analyzed! Form auto-filled.",
        "pdf_err": "Could not read PDF."
    },
    "ar": {
        # Sidebar Titles
        "sb_lang_title": "🌐 اللغة",
        "sb_guide_title": "📖 دليل الاستخدام السريع",
        "sb_about_title": "ℹ️ عن النظام",
        "sb_status_title": "📊 حالة النظام",
        "sb_input_title": "طريقة الإدخال",

        # Sidebar Content
        "sb_steps_md": """
        **الخطوات:**
        1. أدخل تفاصيل الدورة
        2. اذكر المواضيع المطلوبة
        3. حدد أهداف التعلم
        4. اضغط زر الإنشاء
        5. حمل ملف PDF
        """,
        "sb_tips_md": """
        **نصائح:**
        - كن دقيقاً في المواضيع
        - اذكر مستواك الحالي
        - حدد المجال الصناعي
        - أضف أي قيود خاصة
        """,
        "sb_about_md": """
        يستخدم **GAPLER** الذكاء الاصطناعي لربط منهجك باحتياجات سوق العمل.

        **يعمل بواسطة:**
        - GROQ API (Llama 3)
        - نظام الوكلاء المتعددين
        - أبحاث السوق المباشرة
        """,
        "sb_status_ok": "✅ جميع الأنظمة تعمل",
        "sb_metric_time": "~1 دقيقة",
        "sb_metric_lbl": "متوسط وقت المعالجة",

        # Input Methods
        "method_manual": "إدخال يدوي",
        "method_pdf": "الوضع السريع (رفع PDF)",

        # Main Headers
        "mode_student": "🎓 **وضع الطالب مفعل**",
        "header_title": "🚀 GAPLER: مسار تعليمي متوافق مع السوق",
        "header_caption": "أخبرنا بما تريد تعلمه، وسنقوم بإنشاء منهج دراسي جاهز لسوق العمل.",

        # Form Labels
        "subheader_goal": "🎯 ما هو هدفك التعليمي؟",
        "lbl_subject": "الموضوع الأساسي",
        "ph_subject": "مثال: التعلم العميق، تطوير الويب...",
        "lbl_code": "المستوى / الرمز",
        "ph_code": "مثال: مشروع تخرج، CS101...",
        "lbl_duration": "المدة (أسابيع)",
        "lbl_hours": "ساعات الدراسة / أسبوعياً",
        "lbl_lec": "قراءة",
        "lbl_tut": "تمارين",
        "lbl_lab": "عملي",
        "lbl_obj": "الأهداف المهنية",
        "ph_obj": "مثال: أريد العمل كعالم بيانات...",
        "lbl_know": "المعرفة الحالية",
        "ph_know": "مثال: بايثون أساسي...",
        "lbl_topics": "مواضيع محددة",
        "ph_topics": "- الشبكات العصبية\n- المحولات...",
        "lbl_context": "التركيز الصناعي",
        "ph_context": "مثال: المجال الطبي...",

        # Buttons & Messages
        "btn_gen": "✨ إنشاء خطة الدراسة",
        "btn_auto": "✨ تعبئة تلقائية",
        "err_fill": "⚠️ يرجى تعبئة اسم الموضوع والأهداف.",
        "err_no_topic": "⚠️ يرجى كتابة الموضوع الأساسي أولاً.",
        "status_init": "🤖 الذكاء الاصطناعي يبحث في السوق...",
        "status_build": "جاري بناء المسار...",
        "success_ready": "الخطة جاهزة!",
        "success_msg": "إليك خطتك المخصصة!",
        "tab_plan": "📄 عرض الخطة",
        "tab_pdf": "📥 تحميل PDF",
        "pdf_label": "رفع ملف (PDF)",
        "pdf_btn": "⚡ تحليل وتعبئة تلقائية",
        "pdf_success": "تم تحليل الملف! تم تعبئة النموذج.",
        "pdf_err": "تعذر قراءة الملف."
    }
}

# --- SESSION STATE ---
if 'form_data' not in st.session_state:
    st.session_state['form_data'] = {
        "title": "", "code": "", "duration": 12,
        "lec": 4, "tut": 2, "lab": 4,
        "obj": "", "know": "", "topics": "", "context": ""
    }

# --- SIDEBAR (LOGIC) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/student-center.png", width=60)

    # 1. Language Toggle
    # We use a placeholder title that gets updated
    lang_choice = st.radio("lang_hidden", ["English", "العربية"], horizontal=True, label_visibility="collapsed")
    lang_code = "ar" if lang_choice == "العربية" else "en"
    t = UI_TEXT[lang_code]

    # Display Language Title properly
    st.markdown(f"### {t['sb_lang_title']}")

    st.markdown("---")

    # 2. Quick Guide
    st.markdown(f"### {t['sb_guide_title']}")
    st.markdown(t['sb_steps_md'])
    st.info(t['sb_tips_md'])

    st.markdown("---")

    # 3. About
    st.markdown(f"### {t['sb_about_title']}")
    st.markdown(t['sb_about_md'])

    st.markdown("---")

    # 4. System Status
    st.markdown(f"### {t['sb_status_title']}")
    st.success(t['sb_status_ok'])
    st.metric(t['sb_metric_lbl'], t['sb_metric_time'])

    st.markdown("---")

    # 5. Input Type
    st.markdown(f"### {t['sb_input_title']}")
    input_method = st.radio("input_method_hidden", [t["method_manual"], t["method_pdf"]], label_visibility="collapsed")
    is_pdf_mode = (input_method == t["method_pdf"])

# --- CSS STYLING (Fonts, Alignment, Sizes) ---
if lang_code == "ar":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
        }

        /* RTL for Main App & Sidebar */
        .stApp { direction: rtl; text-align: right; }
        [data-testid="stSidebar"] { text-align: right; }
        .stTextInput, .stTextArea, .stNumberInput { text-align: right; }

        /* CENTER HEADERS (Professional Look) */
        h1, h2, h3, h4, h5, h6 { text-align: center !important; }

        /* Sidebar specific: Center Titles, Right Align Text */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            text-align: center !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] li {
            text-align: right;
        }

        /* Fix Markdown Lists in RTL */
        .stMarkdown ul {
            direction: rtl;
            padding-right: 20px;
            list-style-position: inside;
        }

        /* Metric Alignment (Center looks best for numbers) */
        [data-testid="stMetricLabel"] { justify-content: center; }
        [data-testid="stMetricValue"] { justify-content: center; }

        /* INCREASE INPUT LABEL FONT SIZE (ARABIC) */
        .stTextInput label p, .stTextArea label p, .stNumberInput label p {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        /* Fix Radio Buttons Alignment in Sidebar */
        .stRadio div[role="radiogroup"] {
            direction: rtl;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #262730; color: white; border: 1px solid #4f4f4f;
        }

        /* CENTER MAIN TITLES */
        h1, h2, h3 { text-align: center !important; }

        /* Sidebar Headers Centered */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { 
            text-align: center !important; 
        }

        /* INCREASE INPUT LABEL FONT SIZE (ENGLISH) */
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

# --- MAIN BODY (Centered Title & Caption) ---
st.title(t["header_title"])
st.markdown(f"""
    <div style="text-align: center; color: #a3a8b8; font-size: 1.2em; margin-top: -20px; margin-bottom: 30px;">
        {t['header_caption']}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- LAZY MODE ---
if is_pdf_mode:
    st.info(f"💡 {t['method_pdf']}")
    uploaded_file = st.file_uploader(t["pdf_label"], type="pdf")
    if uploaded_file and st.button(t["pdf_btn"]):
        with st.spinner("Reading PDF..."):
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "".join([p.extract_text() for p in reader.pages])
                parser = PDFParserAgent()
                data = parser.extract_course_details(text)
                if data:
                    st.session_state['form_data'].update(data)
                    st.session_state['form_data']['duration'] = int(data.get('duration', 12))
                    st.success(t["pdf_success"])
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"{t['pdf_err']}: {e}")
else:
    # --- MANUAL ENTRY VIEW ---
    st.subheader(t["subheader_goal"])

    # 1. Subject & Auto-Complete (Aligned)
    c_title, c_btn = st.columns([4, 1], vertical_alignment="bottom")

    with c_title:
        course_title = st.text_input(t["lbl_subject"],
                                     value=st.session_state['form_data']['title'],
                                     placeholder=t["ph_subject"],
                                     key="title_input")

    with c_btn:
        if st.button(t["btn_auto"], use_container_width=True):
            if not course_title:
                st.warning(t["err_no_topic"])
            else:
                with st.spinner("✨"):
                    expander = InputExpanderAgent()
                    lang_pref = "Arabic" if lang_code == "ar" else "English"
                    data = expander.expand_topic(course_title, lang_pref)

                    if data:
                        st.session_state['form_data']['title'] = course_title
                        st.session_state['form_data']['code'] = data.get('code', '')
                        st.session_state['form_data']['duration'] = int(data.get('duration', 12))
                        st.session_state['form_data']['lec'] = int(data.get('lec', 3))
                        st.session_state['form_data']['tut'] = int(data.get('tut', 1))
                        st.session_state['form_data']['lab'] = int(data.get('lab', 3))
                        st.session_state['form_data']['obj'] = data.get('obj', '')
                        st.session_state['form_data']['topics'] = data.get('topics', '')
                        st.session_state['form_data']['context'] = data.get('context', '')
                        st.session_state['form_data']['know'] = data.get('know', '')
                        st.rerun()

    # 2. Rest of Inputs
    c1, c2 = st.columns(2)
    with c1:
        course_code = st.text_input(t["lbl_code"], value=st.session_state['form_data']['code'],
                                    placeholder=t["ph_code"])
        duration = st.number_input(t["lbl_duration"], min_value=1, value=st.session_state['form_data']['duration'])

        st.markdown(f"**{t['lbl_hours']}**")
        h1, h2, h3 = st.columns(3)
        lec = h1.number_input(t["lbl_lec"], min_value=1, value=st.session_state['form_data']['lec'])
        tut = h2.number_input(t["lbl_tut"], min_value=0, value=st.session_state['form_data']['tut'])
        lab = h3.number_input(t["lbl_lab"], min_value=0, value=st.session_state['form_data']['lab'])

    with c2:
        objectives = st.text_area(t["lbl_obj"], value=st.session_state['form_data']['obj'], placeholder=t["ph_obj"],
                                  height=140)
        resources = st.text_area(t["lbl_know"], value=st.session_state['form_data']['know'], placeholder=t["ph_know"],
                                 height=100)

    st.markdown("---")
    topics = st.text_area(t["lbl_topics"], value=st.session_state['form_data']['topics'], placeholder=t["ph_topics"],
                          height=150)
    context = st.text_input(t["lbl_context"], value=st.session_state['form_data']['context'],
                            placeholder=t["ph_context"])

# --- GENERATE ---
st.markdown("---")
if st.button(t["btn_gen"]):
    if not course_title or not objectives:
        st.warning(t["err_fill"])
    elif "PASTE_YOUR" in os.environ.get("GROQ_API_KEY", ""):
        st.error("🚨 System Error: Please set the API Key in app.py")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        master = MasterAgent()

        course_data = {
            "title": course_title,
            "code": course_code or "Self-Paced",
            "duration": duration,
            "lec": lec, "tut": tut, "lab": lab,
            "topics": topics,
            "objectives": objectives + f" ({context})",
            "language": "Arabic (Egyptian Style)" if lang_code == "ar" else "English"
        }

        status_text.text(t["status_init"])
        time.sleep(1)
        progress_bar.progress(10)

        with st.spinner(t["status_build"]):
            try:
                final_plan, logs = master.run(course_data)
                for i, log in enumerate(logs):
                    time.sleep(0.5)
                    prog = min(90, 10 + (i * 25))
                    progress_bar.progress(prog)

                progress_bar.progress(100)
                status_text.success(t["success_ready"])
                st.success(f"{t['success_msg']} ({course_title})")

                tab1, tab2 = st.tabs([t["tab_plan"], t["tab_pdf"]])
                with tab1:
                    st.markdown(final_plan)
                with tab2:
                    pdf_file = create_course_pdf(course_data, final_plan)
                    with open(pdf_file, "rb") as f:
                        st.download_button(t["tab_pdf"], f, file_name=pdf_file, mime="application/pdf")
            except Exception as e:
                st.error(f"Error: {e}")