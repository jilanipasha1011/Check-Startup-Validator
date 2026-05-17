import streamlit as st
import requests
import time

# =========================================================
# CONFIG
# =========================================================

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Startup Validator AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 2rem 3rem 4rem !important;
    max-width: 1200px;
    margin: auto;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: white;
}

.hero-sub {
    color: #64748b;
    margin-top: 0.5rem;
}

.result-card {
    background: #0d1627;
    border: 1px solid #1e2d45;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-title {
    color: white;
    font-weight: 700;
    font-size: 1.1rem;
}

.card-body {
    color: #94a3b8;
    line-height: 1.7;
    white-space: pre-wrap;
}

.err-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    padding: 1rem;
    color: #f87171;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================

STEPS = [
    "Market Research",
    "Competitor Analysis",
    "Merging Results",
    "Revenue Model",
    "MVP Planning",
    "Landing Page",
    "Finalizing",
    "Done"
]


def card(title: str, content: str):

    safe = content.replace("<", "&lt;").replace(">", "&gt;")

    st.markdown(
        f"""
        <div class="result-card">
            <div class="card-title">{title}</div>
            <div class="card-body">{safe}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def submit_idea(idea: str):

    try:

        r = requests.post(
            f"{API_BASE}/analyze",
            json={
                "startup_idea": idea
            },
            timeout=10
        )

        r.raise_for_status()

        return r.json()["job_id"]

    except Exception as e:

        st.error(
            f"API Error: {e}"
        )

        return None


def poll_status(job_id: str):

    try:

        r = requests.get(
            f"{API_BASE}/status/{job_id}",
            timeout=10
        )

        r.raise_for_status()

        return r.json()

    except Exception:

        return None


# =========================================================
# SESSION STATE
# =========================================================

for key, default in {
    "job_id": None,
    "result": None,
    "running": False,
    "error": None
}.items():

    if key not in st.session_state:
        st.session_state[key] = default


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<h1 class="hero-title">AI Startup Validator</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="hero-sub">Get market research, competitors, business model, MVP roadmap and landing page instantly.</p>',
    unsafe_allow_html=True
)

# =========================================================
# INPUT
# =========================================================

idea = st.text_area(
    "",
    placeholder="Enter your startup idea...",
    height=130
)

analyze_clicked = st.button(
    "🚀 Analyze My Startup Idea",
    use_container_width=True
)

# =========================================================
# START
# =========================================================

if analyze_clicked:

    if not idea.strip():

        st.warning(
            "Please enter your startup idea."
        )

    else:

        st.session_state.result = None
        st.session_state.error = None
        st.session_state.running = True

        job_id = submit_idea(
            idea.strip()
        )

        st.session_state.job_id = job_id

        if not job_id:
            st.session_state.running = False


# =========================================================
# POLLING
# =========================================================

if st.session_state.running:

    progress = st.progress(0)

    status_text = st.empty()

    while True:

        data = poll_status(
            st.session_state.job_id
        )

        if not data:

            st.session_state.error = "Connection lost."
            st.session_state.running = False
            break

        pct = data.get("progress", 0)

        step = data.get(
            "current_step",
            "Running..."
        )

        status = data.get(
            "status",
            "running"
        )

        progress.progress(
            pct / 100
        )

        status_text.info(
            f"{step} ({pct}%)"
        )

        if status == "completed":

            st.session_state.result = data["result"]
            st.session_state.running = False

            st.rerun()

        if status == "failed":

            st.session_state.error = data["error"]
            st.session_state.running = False

            st.rerun()

        time.sleep(2)


# =========================================================
# ERROR
# =========================================================

if st.session_state.error:

    st.markdown(
        f'<div class="err-box">{st.session_state.error}</div>',
        unsafe_allow_html=True
    )


# =========================================================
# RESULTS
# =========================================================

if st.session_state.result:

    result = st.session_state.result

    st.markdown("## Startup Validation Report")

    col1, col2 = st.columns(2)

    with col1:

        card(
            "📈 Market Research",
            str(
                result.get(
                    "market_research",
                    ""
                )
            )
        )

        card(
            "💰 Revenue Model",
            str(
                result.get(
                    "revenue_model",
                    ""
                )
            )
        )

    with col2:

        card(
            "🔍 Competitor Analysis",
            str(
                result.get(
                    "competitors",
                    ""
                )
            )
        )

        card(
            "🗺 MVP Plan",
            str(
                result.get(
                    "mvp_plan",
                    ""
                )
            )
        )

    # Landing page
    

    # Full AI report
    full_report = f"""
STARTUP IDEA:
{result.get("startup_idea")}


MARKET RESEARCH:
{result.get("market_research")}


COMPETITOR ANALYSIS:
{result.get("competitors")}


REVENUE MODEL:
{result.get("revenue_model")}


MVP PLAN:
{result.get("mvp_plan")}
"""

    with st.expander(
        "View Full AI Report"
    ):

        st.text(
            full_report
        )

    st.download_button(
        "⬇ Download Full Report",
        data=full_report,
        file_name="startup_report.txt",
        mime="text/plain"
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## Pipeline Steps"
    )

    for step in STEPS:

        st.write(
            f"• {step}"
        )

    if st.button(
        "Reset"
    ):

        st.session_state.job_id = None
        st.session_state.result = None
        st.session_state.running = False
        st.session_state.error = None

        st.rerun()