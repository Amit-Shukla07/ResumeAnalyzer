"""
ResumeAnalyzer - Career Intelligence Platform.

A modern, high-precision SaaS interface for evaluating candidate resume alignment
against job descriptions using in-memory PDF extraction, domain-aware tokenization,
TF-IDF unigram/bigram cosine similarity, and deterministic technical skill analysis.
"""

from typing import Optional
import textwrap
import streamlit as st

from src.pdf_extractor import (
    extract_text_from_pdf,
    PDFExtractionError,
    CorruptedPDFError,
    NoExtractableTextError,
)
from src.scoring import (
    evaluate_match,
    DEFAULT_TEXT_WEIGHT,
    DEFAULT_SKILL_WEIGHT,
)
from src.ui_components import (
    GLOBAL_CSS,
    render_navbar,
    render_hero,
    render_combined_score_hero,
    render_metric_grid,
    render_skill_pills,
    extract_resume_evidence,
    render_evidence_section,
    render_recommendation_cards,
)

# -----------------------------------------------------------------------------
# Streamlit Application Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ResumeAnalyzer - Career Intelligence Platform",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Enterprise Dark Theme Design Tokens & Global CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# State Management Helpers
# -----------------------------------------------------------------------------
def reset_session_state() -> None:
    """Clear analysis results and form inputs from session state."""
    st.session_state.pop("analysis_result", None)
    st.session_state.pop("extracted_resume_text", None)
    st.session_state.pop("resume_filename", None)
    st.session_state.pop("extraction_error", None)


# -----------------------------------------------------------------------------
# Top Navigation & Hero Header
# -----------------------------------------------------------------------------
render_navbar()
render_hero()

# -----------------------------------------------------------------------------
# Input Workspace (Dual-Column Architecture)
# -----------------------------------------------------------------------------
col_resume, col_jd = st.columns([1, 1], gap="large")

# --- Column 1: Candidate Resume Upload ---
with col_resume:
    panel_resume_html = textwrap.dedent("""
    <div class="panel-header">
        <div class="panel-num-title">
            <span class="panel-number">01</span>
            <h3 class="panel-title">Candidate Resume</h3>
        </div>
        <span class="status-badge">PDF Document</span>
    </div>
    <div class="panel-caption">
        Upload a candidate resume in PDF format. Content is extracted strictly in RAM with zero disk writes.
    </div>
    """).strip()
    st.markdown(panel_resume_html, unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        help="Upload a single PDF document containing selectable text.",
        label_visibility="collapsed",
    )

    resume_text: Optional[str] = None
    extraction_error_msg: Optional[str] = None

    if uploaded_pdf is not None:
        try:
            # In-memory extraction via src/pdf_extractor.py
            resume_text = extract_text_from_pdf(uploaded_pdf)
            st.session_state["extracted_resume_text"] = resume_text
            st.session_state["resume_filename"] = uploaded_pdf.name
            st.session_state["extraction_error"] = None

            word_count = len(resume_text.split())
            file_size_kb = uploaded_pdf.size / 1024.0

            file_info_html = textwrap.dedent(f"""
            <div style="background: rgba(52, 211, 153, 0.08); border: 1px solid rgba(52, 211, 153, 0.25);
                        border-radius: 8px; padding: 0.65rem 0.9rem; margin-top: 0.65rem; margin-bottom: 0.65rem;
                        display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 0.825rem; color: #6EE7B7;">
                    ✓ <strong>{uploaded_pdf.name}</strong> ({file_size_kb:.1f} KB · {word_count:,} words)
                </div>
            </div>
            """).strip()
            st.markdown(file_info_html, unsafe_allow_html=True)

            with st.expander("📄 Preview Extracted Resume Text", expanded=False):
                st.text_area(
                    "Extracted Text Preview",
                    value=resume_text,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                )

        except NoExtractableTextError:
            extraction_error_msg = (
                "The uploaded PDF contains no extractable text. It may be an image-only scan or blank document. "
                "Please upload a PDF containing selectable text."
            )
            st.session_state["extraction_error"] = extraction_error_msg
            st.error(extraction_error_msg)
        except CorruptedPDFError:
            extraction_error_msg = (
                "The uploaded file is corrupt or not a valid PDF document. Please verify the file integrity."
            )
            st.session_state["extraction_error"] = extraction_error_msg
            st.error(extraction_error_msg)
        except PDFExtractionError as exc:
            extraction_error_msg = f"Failed to extract text from PDF: {exc}"
            st.session_state["extraction_error"] = extraction_error_msg
            st.error(extraction_error_msg)
        except Exception as exc:
            extraction_error_msg = f"An unexpected error occurred during PDF parsing: {exc}"
            st.session_state["extraction_error"] = extraction_error_msg
            st.error(extraction_error_msg)
    else:
        # Reset cached extraction if uploader was cleared
        if "extracted_resume_text" in st.session_state:
            reset_session_state()

# --- Column 2: Job Description Input ---
with col_jd:
    panel_jd_html = textwrap.dedent("""
    <div class="panel-header">
        <div class="panel-num-title">
            <span class="panel-number">02</span>
            <h3 class="panel-title">Target Job Description</h3>
        </div>
        <span class="status-badge">Plain Text</span>
    </div>
    <div class="panel-caption">
        Paste the target role's full description, responsibilities, and technical requirements.
    </div>
    """).strip()
    st.markdown(panel_jd_html, unsafe_allow_html=True)

    jd_input = st.text_area(
        "Job Description Text",
        height=225,
        placeholder="Paste full job description here (e.g. required skills, qualifications, responsibilities)...",
        label_visibility="collapsed",
        key="jd_text_input",
    )

    jd_trimmed = jd_input.strip() if jd_input else ""
    if jd_trimmed:
        jd_words = len(jd_trimmed.split())
        count_html = textwrap.dedent(f"""
        <div style="font-size: 0.775rem; color: var(--text-muted); text-align: right; margin-top: 0.35rem;">
            {jd_words:,} words entered · {len(jd_trimmed):,} characters
        </div>
        """).strip()
        st.markdown(count_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Action & Status Bar
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_status = st.columns([1.6, 1.2, 3.2], gap="medium")

with btn_col1:
    analyze_clicked = st.button("✦ Analyze Resume", type="primary", use_container_width=True)

with btn_col2:
    if st.button("↺ Reset", type="secondary", use_container_width=True):
        reset_session_state()
        st.rerun()

with btn_status:
    has_resume = bool(st.session_state.get("extracted_resume_text"))
    has_jd = bool(jd_input and jd_input.strip())

    if has_resume and has_jd:
        status_html = (
            "<div style='display: flex; align-items: center; gap: 0.5rem; height: 100%; "
            "padding-top: 0.4rem; color: #6EE7B7; font-size: 0.85rem; font-weight: 500;'>"
            "<span style='width: 8px; height: 8px; border-radius: 50%; background-color: #34D399;'></span>"
            "Ready for Analysis · Both documents provided"
            "</div>"
        )
    elif has_resume:
        status_html = (
            "<div style='display: flex; align-items: center; gap: 0.5rem; height: 100%; "
            "padding-top: 0.4rem; color: #FBBF24; font-size: 0.85rem; font-weight: 500;'>"
            "<span style='width: 8px; height: 8px; border-radius: 50%; background-color: #FBBF24;'></span>"
            "Awaiting target job description text"
            "</div>"
        )
    elif has_jd:
        status_html = (
            "<div style='display: flex; align-items: center; gap: 0.5rem; height: 100%; "
            "padding-top: 0.4rem; color: #FBBF24; font-size: 0.85rem; font-weight: 500;'>"
            "<span style='width: 8px; height: 8px; border-radius: 50%; background-color: #FBBF24;'></span>"
            "Awaiting candidate resume PDF"
            "</div>"
        )
    else:
        status_html = (
            "<div style='display: flex; align-items: center; gap: 0.5rem; height: 100%; "
            "padding-top: 0.4rem; color: var(--text-muted); font-size: 0.85rem;'>"
            "Upload a resume and paste a job description to begin"
            "</div>"
        )

    st.markdown(status_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Input Validation & Analysis Execution
# -----------------------------------------------------------------------------
if analyze_clicked:
    current_resume_text = st.session_state.get("extracted_resume_text")
    current_extraction_error = st.session_state.get("extraction_error")

    if uploaded_pdf is None:
        st.warning("Please upload a PDF resume before running analysis.")
    elif current_extraction_error is not None:
        st.error(f"Cannot analyze: {current_extraction_error}")
    elif not current_resume_text or not current_resume_text.strip():
        st.warning("The uploaded resume produced no text. Please upload a valid document.")
    elif not jd_input or not jd_input.strip():
        st.warning("Please paste a target job description before running analysis.")
    else:
        with st.spinner("Evaluating vocabulary alignment and technical competencies..."):
            try:
                result = evaluate_match(current_resume_text, jd_input)
                st.session_state["analysis_result"] = result
            except Exception as exc:
                st.error(f"Analysis engine encountered an error: {exc}")

# -----------------------------------------------------------------------------
# Results Dashboard
# -----------------------------------------------------------------------------
if "analysis_result" in st.session_state and st.session_state["analysis_result"] is not None:
    res = st.session_state["analysis_result"]
    current_resume_text = st.session_state.get("extracted_resume_text", "")

    resume_skills = res.get("resume_skills", [])
    required_skills = res.get("required_skills", [])
    matched_skills = res.get("matched_skills", [])
    missing_skills = res.get("missing_skills", [])
    additional_skills = sorted(list(set(resume_skills) - set(required_skills)))

    w_text_pct = int(DEFAULT_TEXT_WEIGHT * 100)
    w_skill_pct = int(DEFAULT_SKILL_WEIGHT * 100)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    results_head_html = textwrap.dedent("""
    <div class="results-header-container">
        <h2 class="results-title">Alignment Analysis Results</h2>
        <span class="results-tag">Verified Analysis</span>
    </div>
    """).strip()
    st.markdown(results_head_html, unsafe_allow_html=True)

    # 1. Primary Composite Score Hero (with SVG Gauge)
    render_combined_score_hero(res, w_text_pct, w_skill_pct)

    # 2. Supporting Metric Grid
    render_metric_grid(res)

    # 3. Technical Skill Breakdown
    skill_section_header = textwrap.dedent("""
    <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);
                margin-top: 1.5rem; margin-bottom: 0.85rem;">
        🎯 Technical Skill Alignment & Gap Analysis
    </div>
    """).strip()
    st.markdown(skill_section_header, unsafe_allow_html=True)

    skill_col1, skill_col2, skill_col3 = st.columns(3, gap="medium")

    with skill_col1:
        card1_top = (
            '<div class="skill-category-card">'
            '<div class="skill-category-header">'
            '<span class="skill-category-title">✓ Matched Skills</span>'
            f'<span class="skill-count-badge skill-count-matched">{len(matched_skills)}</span>'
            '</div>'
            '<div class="skill-category-caption">Recognized skills present in both documents:</div>'
        )
        st.markdown(card1_top, unsafe_allow_html=True)
        render_skill_pills(matched_skills, "skill-pill-matched", "No recognized skills matched.")
        st.markdown("</div>", unsafe_allow_html=True)

    with skill_col2:
        card2_top = (
            '<div class="skill-category-card">'
            '<div class="skill-category-header">'
            '<span class="skill-category-title">⚠️ Potential Gaps</span>'
            f'<span class="skill-count-badge skill-count-missing">{len(missing_skills)}</span>'
            '</div>'
            '<div class="skill-category-caption">Recognized in JD, absent in resume wording:</div>'
        )
        st.markdown(card2_top, unsafe_allow_html=True)
        render_skill_pills(missing_skills, "skill-pill-missing", "None — all recognized skills detected!")
        if missing_skills:
            gap_note = (
                '<div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.65rem; line-height: 1.35;">'
                '* Indicates absence in resume text, not necessarily a lack of candidate ability.'
                '</div>'
            )
            st.markdown(gap_note, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with skill_col3:
        card3_top = (
            '<div class="skill-category-card">'
            '<div class="skill-category-header">'
            '<span class="skill-category-title">💡 Additional Skills</span>'
            f'<span class="skill-count-badge skill-count-additional">{len(additional_skills)}</span>'
            '</div>'
            '<div class="skill-category-caption">Detected in resume, not requested in JD:</div>'
        )
        st.markdown(card3_top, unsafe_allow_html=True)
        render_skill_pills(additional_skills, "skill-pill-additional", "No additional recognized skills detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Verified Requirement Evidence in Resume
    evidence_snippets = extract_resume_evidence(current_resume_text, matched_skills, max_snippets=4)
    if evidence_snippets:
        render_evidence_section(evidence_snippets)

    # 5. Tailoring Recommendations
    recs_title_html = (
        '<div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); '
        'margin-top: 1.75rem; margin-bottom: 0.25rem;">'
        '💡 Actionable Tailoring Recommendations</div>'
        '<div style="font-size: 0.825rem; color: var(--text-secondary); margin-bottom: 0.5rem;">'
        'Targeted guidance based on your alignment metrics and identified skill patterns:</div>'
    )
    st.markdown(recs_title_html, unsafe_allow_html=True)

    render_recommendation_cards(
        missing_skills=missing_skills,
        text_similarity=res.get("text_similarity", 0.0),
        additional_skills=additional_skills,
        required_skills=required_skills,
    )

    # 6. Scoring Methodology & Transparency Drawer
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("📐 Scoring Methodology & Architectural Transparency", expanded=False):
        method_desc = textwrap.dedent(f"""
        #### 1. Configured Weights & Formulas
        - **Weight Configuration**: `{w_text_pct}%` Text Similarity + `{w_skill_pct}%` Skill Coverage
          (configured in `src/scoring.py`).
        - **Text Similarity Metric**: Fits a `TfidfVectorizer` over unigram and bigram features
          (`ngram_range=(1, 2)`) with `sublinear_tf=True` to dampen keyword repetition.
        - **Skill Match Metric**: Identifies 30+ technical keywords via deterministic regular expressions
          with strict word-boundary anchors to prevent substring false-positives
          (e.g., distinguishing `C` from `React` or `Docker`).
          Ratio: `(Matched Skills / Required Skills) × 100`.
        - **Active Calculation**:
        """).strip()
        st.markdown(method_desc)

        if res.get("skill_match") is not None:
            st.code(
                f"Combined Score = ({w_text_pct}% × {res['text_similarity']:.2f}) + "
                f"({w_skill_pct}% × {res['skill_match']:.2f}) = {res['combined_score']:.2f}%",
                language="text",
            )
        else:
            st.code(
                "Combined Score = Unavailable (Job description has no recognized technical skills from dictionary)",
                language="text",
            )

        interpret_desc = textwrap.dedent("""
        #### 2. What These Metrics Mean & Do Not Mean
        - **Lexical Concordance**: Text similarity reflects phrasing alignment, not candidate seniority.
        - **Keyword Absence vs. Competency**: An identified skill gap indicates that a word was not detected;
          it does not imply that a candidate cannot perform the role.
        - **Deterministic Integrity**: No third-party LLMs, external APIs, or probabilistic inference are used.
        - **Not a Hiring Predictor**: These indicators are intended solely for personal resume tailoring.
        """).strip()
        st.markdown(interpret_desc)
