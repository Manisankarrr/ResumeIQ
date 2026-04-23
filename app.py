"""
Hugging Face Spaces entry point — a standard Streamlit script.

HF Spaces runs: streamlit run app.py
This file boots the FastAPI backend as a background subprocess at import time,
then contains all Streamlit UI logic inline.
"""

import os
import sys
import subprocess
import time

# ── 1. Start FastAPI backend (once) ──────────────────────────────────────────
# Use session-state-like guard at module level so the subprocess is only
# spawned on the very first import, not on every Streamlit rerun.
_BACKEND_STARTED_FLAG = os.environ.get("_BACKEND_STARTED")
if not _BACKEND_STARTED_FLAG:
    subprocess.Popen(
        [sys.executable, "-m", "api.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    os.environ["_BACKEND_STARTED"] = "1"
    time.sleep(3)  # give uvicorn a moment to bind

# ── 2. Make ui/ importable (theme.py, html_components.py live there) ─────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ui"))

# ── 3. Streamlit UI ──────────────────────────────────────────────────────────
import streamlit as st
import httpx
from theme import apply_theme
from html_components import (
    build_candidate_card_html,
    build_ranking_chart_html,
    build_skill_matrix_html,
    build_metrics_html,
    get_colors,
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ResumeIQ",
    layout="wide",
    page_icon=None,
    initial_sidebar_state="expanded",
)

# SESSION STATE INIT
st.session_state.setdefault("results", None)
st.session_state.setdefault("jd_skills", [])
st.session_state.setdefault("screening", False)
st.session_state.setdefault("proc_time", 0.0)

# THEME
dark = False
apply_theme(dark)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
      <div style="width:9px;height:9px;background:#534AB7;border-radius:50%"></div>
      <div>
        <div style="font-size:15px;font-weight:700;color:var(--text,#111110);line-height:1">ResumeIQ</div>
        <div style="font-size:10px;color:#999890;margin-top:1px">AI resume screening</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Job description
    st.markdown('<p style="font-size:10px;font-weight:600;color:#999890;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px">Job description</p>', unsafe_allow_html=True)
    jd_text = st.text_area(
        label="jd_input",
        label_visibility="collapsed",
        height=180,
        placeholder="Paste the full job description here…\n\nInclude required skills, nice-to-haves, and role details for best results.",
        key="jd_text_input",
    )

    st.divider()

    # File uploader
    st.markdown('<p style="font-size:10px;font-weight:600;color:#999890;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px">Resumes (PDF · max 5)</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        label="resume_upload",
        label_visibility="collapsed",
        type=["pdf"],
        accept_multiple_files=True,
        key="resume_files",
    )

    # Show selected file count
    if uploaded_files:
        n = len(uploaded_files)
        color = "#27500A" if n <= 5 else "#791F1F"
        bg = "#EAF3DE" if n <= 5 else "#FCEBEB"
        st.markdown(f"""
        <div style="font-size:11px;font-weight:500;color:{color};background:{bg};
          padding:5px 10px;border-radius:20px;display:inline-block;margin-top:4px">
          {n} of 5 file{'s' if n != 1 else ''} selected
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='flex:1;min-height:20px'></div>", unsafe_allow_html=True)

    # Spinner — shown during processing via session state
    if st.session_state.get("screening", False):
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;padding:10px 12px;
          background:#EEEDFE;border-radius:10px;margin-bottom:10px">
          <style>
            @keyframes sbpulse{0%,80%,100%{opacity:.2}40%{opacity:1}}
            .sb-dot{width:6px;height:6px;border-radius:50%;background:#534AB7;
              animation:sbpulse 1s ease-in-out infinite}
            .sb-dot:nth-child(2){animation-delay:.2s}
            .sb-dot:nth-child(3){animation-delay:.4s}
          </style>
          <div class="sb-dot"></div><div class="sb-dot"></div><div class="sb-dot"></div>
          <span style="font-size:11px;font-weight:500;color:#534AB7">Screening candidates…</span>
        </div>
        """, unsafe_allow_html=True)

    # Screen button
    can_run = bool(jd_text and jd_text.strip() and uploaded_files and len(uploaded_files) <= 5)
    screen_btn = st.button(
        "Screen Candidates",
        type="primary",
        disabled=not can_run,
        use_container_width=True,
        key="screen_btn",
    )

    st.markdown('<p style="font-size:10px;color:#c0bfb8;text-align:center;margin-top:8px">Llama 3.3 · FAISS · LangGraph</p>', unsafe_allow_html=True)

# ── BUTTON HANDLER ───────────────────────────────────────────────────────────
if screen_btn:
    if len(uploaded_files) > 5:
        st.sidebar.error("Maximum 5 resumes allowed.")
    else:
        st.session_state["screening"] = True
        st.rerun()

# ── API CALL ─────────────────────────────────────────────────────────────────
if st.session_state.get("screening", False) and uploaded_files and jd_text:
    try:
        files = [("resumes", (f.name, f.read(), "application/pdf")) for f in uploaded_files]
        with httpx.Client(timeout=120) as client:
            response = client.post(
                f"{API_URL}/api/v1/screen",
                files=files,
                data={"jd_text": jd_text},
            )
        if response.status_code == 200:
            data = response.json()
            st.session_state["results"] = data["results"]
            st.session_state["jd_skills"] = data["jd_skills"]
            st.session_state["proc_time"] = data["processing_time_seconds"]
        else:
            st.sidebar.error(f"API error: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.sidebar.error(f"Could not reach backend: {e}")
    finally:
        st.session_state["screening"] = False
        st.rerun()

# ── COLORS ───────────────────────────────────────────────────────────────────
c = get_colors(dark)

# ── RESULTS DISPLAY ──────────────────────────────────────────────────────────
if st.session_state.results is not None:
    results = st.session_state.results
    jd_skills = st.session_state.jd_skills

    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    class CandidateObj:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    res_objs = [CandidateObj(**r) for r in results]

    st.markdown(
        f"**Screening Results** &middot; <span style='color:{c['text3']}'>{len(results)} candidates</span>",
        unsafe_allow_html=True,
    )
    metrics_html = build_metrics_html(res_objs, jd_skills, dark)
    st.html(metrics_html)

    universal_gaps = [s for s in jd_skills if all(s in r.get("missing_skills", []) for r in results)]
    if universal_gaps:
        st.warning(
            f"These skills are missing from every candidate: {', '.join(universal_gaps)}. "
            "Consider whether they're truly required."
        )

    tab1, tab2, tab3 = st.tabs(["Overview", "Candidate cards", "Skill matrix"])

    with tab1:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.markdown("**Score ranking**")
            chart_html = build_ranking_chart_html(res_objs, dark)
            st.html(chart_html)

        with col_b:
            st.markdown("**Common missing skills**")
            total_cnt = len(results)
            heatmap_rows = []
            for skill in jd_skills:
                count = sum(1 for r in results if skill in r.get("matched_skills", []))
                if count == total_cnt and total_cnt > 0:
                    bg = c["green_bg"]
                    text_c = c["green"]
                elif count == 0:
                    bg = c["red_bg"]
                    text_c = c["red"]
                else:
                    bg = c["amber_bg"]
                    text_c = c["amber"]

                heatmap_rows.append(f'''
                <div style="display:flex; justify-content:space-between; align-items:center; background:{c['bg']}; padding:8px 12px; margin-bottom:6px; border-radius:6px; border:1px solid {c['border']}; font-family:'Inter', sans-serif;">
                    <span style="font-size:13px; font-weight:500; color:{c['text']};">{skill}</span>
                    <span style="background:{bg}; color:{text_c}; font-size:11px; font-weight:600; padding:3px 8px; border-radius:12px;">{count}/{total_cnt}</span>
                </div>
                ''')

            heatmap_content = "".join(heatmap_rows)
            heatmap_html = f'''
            <div style="background:{c['bg2']}; padding:14px; border-radius:10px; font-family:'Inter', sans-serif;">
                {heatmap_content}
            </div>
            '''
            st.html(heatmap_html)

    with tab2:
        for r_obj, r_dict in zip(res_objs, results):
            card_html = build_candidate_card_html(r_obj, r_dict["rank"], jd_skills, dark)
            st.html(card_html)

    with tab3:
        matrix_html = build_skill_matrix_html(res_objs, jd_skills, dark)
        st.html(matrix_html)
        st.divider()

        csv_lines = ["Rank,Name,Score%,Matched,Missing,Verdict"]
        for r in results:
            rank = r["rank"]
            name = f'"{r.get("candidate_name", "")}"'
            score_pct = f"{r.get('score', 0) * 100:.0f}%"
            matched_str = f'"{", ".join(r.get("matched_skills", []))}"'
            missing_str = f'"{", ".join(r.get("missing_skills", []))}"'
            score_val = r.get("score", 0)
            verdict = "Shortlist" if score_val >= 0.7 else "Maybe" if score_val >= 0.4 else "Reject"

            csv_lines.append(f"{rank},{name},{score_pct},{matched_str},{missing_str},{verdict}")

        csv_string = "\n".join(csv_lines)
        st.download_button(
            "Download results as CSV",
            data=csv_string.encode("utf-8"),
            file_name="screening_results.csv",
            mime="text/csv",
        )

else:
    # MAIN AREA — NO RESULTS STATE
    empty_html = f"""
    <div style="margin-top: 80px; text-align: center; color: {c['text3']}; font-family: 'Inter', sans-serif;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px;">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        <h3 style="color:{c['text']}; font-weight:600; margin-bottom:8px;">Ready to screen</h3>
        <p>Upload PDFs and paste a job description to begin.</p>
    </div>
    """
    st.markdown(empty_html, unsafe_allow_html=True)
