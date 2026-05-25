import streamlit as st
from agents import (
    run_company_intel_agent,
    run_resume_tailor_agent,
    run_cover_letter_agent,
    run_interview_prep_agent
)

# ─── Page Configuration ───
st.set_page_config(
    page_title="RecruitIQ",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS for cleaner look ───
st.markdown("""
<style>
    .stTextArea textarea { font-size: 14px; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
    div[data-testid="stStatusWidget"] { display: none; }
</style>
""", unsafe_allow_html=True)

# Force hide the GitHub icon, Fork button, and header/footer elements
hide_style = """
    <style>
    /* Hides the top right GitHub link and Fork buttons */
    header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* Hides the default Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# ─── Header ───
st.title("🎯 RecruitIQ")
st.markdown(
    "**Multi-agent MBA application intelligence.** "
    "Paste a job description and your resume. Get a complete application package in 5 minutes."
)
st.caption("4 specialized AI agents run in sequence: Company Research → Resume Tailoring → Cover Letter → Interview Prep")
st.divider()

# ─── Input Section ───
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    company_name = st.text_input(
        "🏢 Company Name",
        placeholder="e.g. McKinsey & Company",
        help="The company you're applying to"
    )
    job_description = st.text_area(
        "📋 Paste the Full Job Description",
        height=320,
        placeholder="Paste the complete job description here — the more complete, the better the output...",
        help="Copy the entire JD from LinkedIn, the company website, or wherever you found it"
    )

with col_right:
    resume_text = st.text_area(
        "📄 Paste Your Resume as Plain Text",
        height=400,
        placeholder=(
            "Paste your entire resume as plain text here.\n\n"
            "Tip: Open your resume PDF, select all text (Command+A), copy (Command+C), and paste here.\n\n"
            "Include: education, all work experiences with bullet points, and skills."
        ),
        help="Plain text works best — formatting doesn't matter here"
    )

st.divider()

# ─── Generate Button ───
generate_clicked = st.button(
    "🚀 Generate My Application Package",
    type="primary",
    use_container_width=True
)

# ─── Input Validation ───
if generate_clicked:
    missing = []
    if not company_name.strip():
        missing.append("Company Name")
    if not job_description.strip():
        missing.append("Job Description")
    if not resume_text.strip():
        missing.append("Resume")

    if missing:
        st.error(f"⚠️ Please fill in: {', '.join(missing)}")
        st.stop()

    if len(job_description.strip()) < 100:
        st.warning("⚠️ Your job description looks very short. Paste the full JD for better results.")

    if len(resume_text.strip()) < 200:
        st.warning("⚠️ Your resume looks very short. Paste your full resume for better tailoring.")

    # ─── Run the 4 Agents ───
    st.divider()
    st.markdown("### 🤖 Agents Running...")
    st.caption("Each agent completes before the next one starts. Agents 3 and 4 use Agent 1's research.")

    # Create 4 status boxes
    agent_col1, agent_col2 = st.columns(2)
    with agent_col1:
        status_intel = st.status("🔍 Agent 1: Company Intelligence", expanded=False)
        status_resume = st.status("📝 Agent 2: Resume Tailor", expanded=False)
    with agent_col2:
        status_cover = st.status("✉️ Agent 3: Cover Letter Writer", expanded=False)
        status_interview = st.status("🎤 Agent 4: Interview Prep", expanded=False)

    results = {}
    error_occurred = False

    # ── Agent 1 ──
    with status_intel:
        st.write(f"Searching the web for real intelligence on {company_name}...")
    try:
        results["intel"] = run_company_intel_agent(company_name, job_description)
        status_intel.update(label="✅ Agent 1: Company Intelligence — Complete", state="complete", expanded=False)
    except Exception as e:
        status_intel.update(label="❌ Agent 1 failed", state="error")
        st.error(f"Company Intelligence Agent error: {str(e)}")
        st.info("💡 Check that your TAVILY_API_KEY and GROQ_API_KEY in .env are correct.")
        error_occurred = True

    if not error_occurred:
        # ── Agent 2 ──
        with status_resume:
            st.write("Analyzing your resume against the job description...")
        try:
            results["resume"] = run_resume_tailor_agent(job_description, resume_text, company_name)
            status_resume.update(label="✅ Agent 2: Resume Tailor — Complete", state="complete", expanded=False)
        except Exception as e:
            status_resume.update(label="❌ Agent 2 failed", state="error")
            st.error(f"Resume Tailor Agent error: {str(e)}")
            error_occurred = True

    if not error_occurred:
        # ── Agent 3 (uses Agent 1's output) ──
        with status_cover:
            st.write(f"Writing a letter that references what Agent 1 found about {company_name}...")
        try:
            results["cover"] = run_cover_letter_agent(
                job_description, resume_text, company_name, results["intel"]
            )
            status_cover.update(label="✅ Agent 3: Cover Letter — Complete", state="complete", expanded=False)
        except Exception as e:
            status_cover.update(label="❌ Agent 3 failed", state="error")
            st.error(f"Cover Letter Agent error: {str(e)}")
            error_occurred = True

    if not error_occurred:
        # ── Agent 4 (uses Agent 1's output) ──
        with status_interview:
            st.write("Predicting likely questions and mapping your best stories...")
        try:
            results["interview"] = run_interview_prep_agent(
                job_description, resume_text, company_name, results["intel"]
            )
            status_interview.update(label="✅ Agent 4: Interview Prep — Complete", state="complete", expanded=False)
        except Exception as e:
            status_interview.update(label="❌ Agent 4 failed", state="error")
            st.error(f"Interview Prep Agent error: {str(e)}")
            error_occurred = True

    # ─── Display Results ───
    if not error_occurred and len(results) == 4:
        st.divider()
        st.success("✅ Your application package is ready. Everything below is tailored specifically for this role.")

        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Company Intel",
            "📝 Tailored Bullets",
            "✉️ Cover Letter",
            "🎤 Interview Prep"
        ])

        with tab1:
            st.markdown(f"### Company Intelligence: {company_name}")
            st.caption("Researched in real-time by Agent 1 using Tavily web search + Groq synthesis")
            st.markdown(results["intel"])

        with tab2:
            st.markdown("### Your Top 5 Resume Bullets for This Application")
            st.caption("Selected and rewritten by Agent 2 to mirror this JD's language and priorities")
            st.markdown(results["resume"])

        with tab3:
            st.markdown("### Personalized Cover Letter")
            st.caption(
                f"Written by Agent 3 using Agent 1's company research — "
                f"Para 1 references something specific about {company_name}"
            )
            st.markdown(results["cover"])
            st.divider()
            col_dl, col_copy = st.columns([1, 3])
            with col_dl:
                st.download_button(
                    label="⬇️ Download as .txt",
                    data=results["cover"],
                    file_name=f"cover_letter_{company_name.replace(' ', '_').replace('&', 'and')}.txt",
                    mime="text/plain"
                )

        with tab4:
            st.markdown("### Interview Intelligence Report")
            st.caption(
                "8 questions predicted by Agent 4 — each mapped to your best resume story "
                "with an opening line you can memorize"
            )
            st.markdown(results["interview"])

        st.divider()
        st.caption(
            "⏱ All 4 agents ran sequentially. "
            "Agents 3 and 4 received Agent 1's company intelligence as context — "
            "this is why the cover letter references something real about the company."
        )