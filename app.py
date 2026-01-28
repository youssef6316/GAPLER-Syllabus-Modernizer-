import streamlit as st
import time
from agents import MasterAgent
from tools import create_course_pdf
import os

# Page Config
st.set_page_config(page_title="CMAS - AI Curriculum Optimizer", layout="wide", page_icon="🎓")

# Custom CSS to match the dark theme in screenshot
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    .stButton>button {
        background-color: #0068c9;
        color: white;
        width: 100%;
        border-radius: 5px;
    }
    /* Input fields styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730;
        color: white;
        border: 1px solid #4f4f4f;
    }
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=50)
    st.title("Quick Guide")
    st.markdown("""
    **Steps:**
    1. Enter course details
    2. List topics to cover
    3. Define learning goals
    4. Click Generate
    5. Download PDF
    """)

    st.info("System running on Groq (Llama 3)")

    # API Key Input
    api_key = st.text_input("Groq API Key", type="password", help="Get free key at console.groq.com")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    language = st.selectbox("Output Language", ["English", "Arabic (Egyptian Style)"])

# Main Header
col1, col2 = st.columns([1, 5])
with col2:
    st.title("🎓 CMAS")
    st.caption("Course-Market Alignment System - Powered by Multi-Agent Gemini System")

st.markdown("---")

# --- Input Section (Replicating Image) ---
st.subheader("📝 Enter Your Course Information")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Basic Information**")
    course_title = st.text_input("Course Title *", value="Deep Learning")
    course_code = st.text_input("Course Code *", value="CS555")
    duration = st.number_input("Study Duration (weeks) *", min_value=1, value=13)

    st.markdown("**Weekly Hours**")
    h1, h2, h3 = st.columns(3)
    lec = h1.number_input("Lectures", value=2)
    tut = h2.number_input("Tutorials", value=2)
    lab = h3.number_input("Labs", value=1)

with c2:
    st.markdown("**Learning Objectives**")
    objectives = st.text_area("What should students learn? *",
                              value="- Mathematical interpretation of topics\n- Use cases of each model type\n- Model design, train & test with metrics\n- Learn Industry Tools used in current market")

    st.markdown("**Previous Work / Current Resources**")
    resources = st.text_area("Existing content",
                             value="- Math & Linear Algebra Foundation\n- Classical Machine Learning theories\n- Python programming")

st.markdown("**📚 Topics to Cover**")
topics = st.text_area("List the topics you want to study *",
                      value="- Neural Networks\n- Back propagation\n- Loss function and Optimizers\n- Convolution Neural Networks & Arch.\n- RNNs\n- LSTMs")

st.markdown("**Additional Information (Optional)**")
context = st.text_input("", value="Post-grad students seeking to merge research work with industry tools.")

# --- Action Section ---
st.markdown("---")
generate_btn = st.button("🚀 Generate Market-Aligned Course Plan")

if generate_btn:
    if not os.environ.get("GROQ_API_KEY"):
        st.error("Please enter a Grok Gemini API Key in the sidebar.")
    else:
        # Progress Bar and Status
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. Initialize Master
        master = MasterAgent()

        # Package Data
        course_data = {
            "title": course_title,
            "code": course_code,
            "duration": duration,
            "lec": lec, "tut": tut, "lab": lab,
            "topics": topics,
            "objectives": objectives,
            "language": language
        }

        # 2. Run Agents
        status_text.text("Initializing Multi-Agent System...")
        time.sleep(1)
        progress_bar.progress(5)

        status_log = []

        with st.spinner('Agents are analyzing market data...'):
            try:
                final_plan, logs = master.run(course_data)

                # Visual Simulation of the "System Status" box in the screenshot
                for i, log in enumerate(logs):
                    time.sleep(1.0)
                    status_text.code(f"System Log: {log}")
                    # Calculate progress dynamically based on steps
                    prog = min(90, 10 + (i * 25))
                    progress_bar.progress(prog)

                progress_bar.progress(100)
                status_text.success("Optimization Complete.")

                # 3. Display Result
                st.success("Course Plan Generated Successfully!")

                # Result Tabs
                tab1, tab2 = st.tabs(["📄 Plan View", "📥 Download PDF"])

                with tab1:
                    st.markdown("### Generated Course Plan")
                    st.markdown(final_plan)

                with tab2:
                    # Generate PDF
                    pdf_file = create_course_pdf(course_data, final_plan)

                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="Download PDF Plan",
                            data=f,
                            file_name=pdf_file,
                            mime="application/pdf"
                        )

            except Exception as e:
                st.error(f"An error occurred: {e}")