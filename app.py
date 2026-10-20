"""
ResumeAnalyzer - Streamlit Dashboard.

An interactive, NLP-driven application to evaluate alignment between candidate resumes
and job descriptions using in-memory PDF extraction, domain text preprocessing,
unigram/bigram TF-IDF cosine similarity, and dictionary-based skill analysis.
"""

from typing import Optional
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

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Design System
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ResumeAnalyzer - Resume–JD Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimal, clean portfolio styling (light-gray/white palette, restrained neutral accents)
CUSTOM_CSS = """
<style>
/* Global Font & Spacing */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #111827;
}

/* Header Styling */
.header-container {
    padding: 0.5rem 0 1.5rem 0;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid #e5e7eb;
}
.header-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.03em;
    margin: 0;
    padding: 0;
}
.header-subtitle {
    font-size: 1.05rem;
    color: #4b5563;
    margin-top: 0.35rem;
    margin-bottom: 0.5rem;
}
.header-description {
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.45;
}

/* Metric Cards */
.metric-card {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.25rem 1.15rem;
    height: 100%;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}
.metric-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6b7280;
    margin-bottom: 0.35rem;
}
.metric-value {
    font-size: 2.25rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}
.metric-value-na {
    font-size: 1.5rem;
    font-weight: 600;
    color: #9ca3af;
    line-height: 1.4;
    margin-bottom: 0.4rem;
}
.metric-caption {
    font-size: 0.8125rem;
    color: #4b5563;
    line-height: 1.35;
}

/* Skill Tags & Pills */
.skill-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
.skill-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8125rem;
    font-weight: 500;
    line-height: 1.3;
}
.skill-pill-matched {
    background-color: #f3f4f6;
    border: 1px solid #d1d5db;
    color: #111827;
}
.skill-pill-missing {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
}
.skill-pill-additional {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    color: #4b5563;
}

/* Informational Cards & Callouts */
.info-card {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-top: 0.75rem;
    font-size: 0.875rem;
    color: #374151;
    line-height: 1.45;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def reset_session_state() -> None:
    """Clear analysis results and form inputs from session state."""
    st.session_state.pop("analysis_result", None)
    st.session_state.pop("extracted_resume_text", None)
    st.session_state.pop("resume_filename", None)
    st.session_state.pop("extraction_error", None)


def render_skill_pills(skills: list[str], pill_class: str, empty_message: str) -> None:
    """Render a wrapping list of stylized skill pills."""
    if not skills:
        st.markdown(f"<span style='color: #6b7280; font-size: 0.875rem;'>{empty_message}</span>", unsafe_allow_html=True)
        return

    pills_html = "".join([f'<span class="skill-pill {pill_class}">{skill}</span>' for skill in skills])
    st.markdown(f'<div class="skill-grid">{pills_html}</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Header Section
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-container">
        <h1 class="header-title">ResumeAnalyzer</h1>
        <div class="header-subtitle">Understand how closely your resume aligns with a job description.</div>
        <div class="header-description">
            Evaluates candidate alignment through unigram & bigram TF-IDF cosine similarity,
            in-memory PDF text extraction, and deterministic dictionary-based skill analysis across 30+ technical domains.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Input Section: Two Distinct Panels
# -----------------------------------------------------------------------------
col_resume, col_jd = st.columns([1, 1], gap="large")

# --- Panel A: Resume Upload & Extraction ---
with col_resume:
    st.subheader("📄 Resume (PDF)")
    st.caption("Upload a candidate resume in PDF format. Files are processed strictly in memory.")

    uploaded_pdf = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        help="Upload a single PDF file with selectable text.",
        label_visibility="collapsed",
    )

    resume_text: Optional[str] = None
    extraction_error_msg: Optional[str] = None

    if uploaded_pdf is not None:
        try:
            # In-memory extraction via src/pdf_extractor.py without saving to disk
            resume_text = extract_text_from_pdf(uploaded_pdf)
            st.session_state["extracted_resume_text"] = resume_text
            st.session_state["resume_filename"] = uploaded_pdf.name
            st.session_state["extraction_error"] = None

            word_count = len(resume_text.split())
            st.success(f"Extracted {word_count} words from **{uploaded_pdf.name}**")

            with st.expander("Extracted Resume Text Preview", expanded=False):
                st.text_area(
                    "Extracted Text",
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
        # Clear cached extraction if uploader was cleared
        if "extracted_resume_text" in st.session_state:
            reset_session_state()

# --- Panel B: Job Description Input ---
with col_jd:
    st.subheader("📋 Job Description")
    st.caption("Paste the target role's full description, responsibilities, and technical requirements.")

    jd_input = st.text_area(
        "Job Description Text",
        height=220,
        placeholder="Paste full job description here (e.g. required skills, qualifications, responsibilities)...",
        label_visibility="collapsed",
        key="jd_text_input",
    )

    if jd_input.strip():
        jd_words = len(jd_input.split())
        st.caption(f"{jd_words} words entered")

# --- Action Bar ---
st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_spacer = st.columns([1.5, 1.2, 4], gap="medium")

with btn_col1:
    analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

with btn_col2:
    if st.button("↺ Reset", type="secondary", use_container_width=True):
        reset_session_state()
        st.rerun()

# -----------------------------------------------------------------------------
# Input Validation & Execution
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
        with st.spinner("Analyzing text similarity and technical skills..."):
            try:
                # Execute full evaluation via src/scoring.py
                result = evaluate_match(current_resume_text, jd_input)
                st.session_state["analysis_result"] = result
            except Exception as exc:
                st.error(f"Analysis engine encountered an error: {exc}")

# -----------------------------------------------------------------------------
# Results Dashboard
# -----------------------------------------------------------------------------
if "analysis_result" in st.session_state and st.session_state["analysis_result"] is not None:
    res = st.session_state["analysis_result"]

    # Compute additional skills (skills in resume but not in required JD skills)
    resume_skills = res.get("resume_skills", [])
    required_skills = res.get("required_skills", [])
    matched_skills = res.get("matched_skills", [])
    missing_skills = res.get("missing_skills", [])
    additional_skills = sorted(list(set(resume_skills) - set(required_skills)))

    st.markdown("---")
    st.subheader("📊 Analysis Results")

    # A. Score Overview Cards
    card_col1, card_col2, card_col3 = st.columns(3, gap="medium")

    # Metric 1: Text Similarity
    with card_col1:
        text_sim = res.get("text_similarity", 0.0)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Text Similarity</div>
                <div class="metric-value">{text_sim:.1f}%</div>
                <div class="metric-caption">
                    TF-IDF unigram & bigram cosine similarity measuring general vocabulary and phrasing overlap.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Metric 2: Skill Match
    with card_col2:
        skill_score = res.get("skill_match")
        if skill_score is not None:
            value_html = f'<div class="metric-value">{skill_score:.1f}%</div>'
            caption_text = f"Proportion of recognized JD requirements ({len(matched_skills)}/{len(required_skills)}) detected in resume."
        else:
            value_html = '<div class="metric-value-na">Unavailable</div>'
            caption_text = "No recognized technical skills were found in the provided job description."

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Skill Match</div>
                {value_html}
                <div class="metric-caption">{caption_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Metric 3: Combined Score
    with card_col3:
        combined_score = res.get("combined_score")
        w_text_pct = int(DEFAULT_TEXT_WEIGHT * 100)
        w_skill_pct = int(DEFAULT_SKILL_WEIGHT * 100)

        if combined_score is not None:
            value_html = f'<div class="metric-value">{combined_score:.1f}%</div>'
            caption_text = f"Configured composite: {w_text_pct}% Text Similarity + {w_skill_pct}% Skill Match."
        else:
            value_html = '<div class="metric-value-na">Unavailable</div>'
            caption_text = "Combined score cannot be calculated when Skill Match is unavailable."

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Combined Score</div>
                {value_html}
                <div class="metric-caption">{caption_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Transparency Notice
    st.markdown(
        """
        <div class="info-card">
            <strong>ℹ️ Evaluation Methodology & Transparency:</strong><br/>
            • <strong>Text Similarity</strong> measures lexical and phrase overlap between both texts.<br/>
            • <strong>Skill Match</strong> indicates recognized required technical terms detected in the resume text.<br/>
            • <strong>Combined Score</strong> is a configurable heuristic indicator, not an algorithmic hiring decision.<br/>
            • <em>None of these metrics represent candidate competence, qualification, or probability of being hired.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # B. Skill Analysis Sections
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    st.subheader("🎯 Technical Skill Breakdown")

    skill_col1, skill_col2, skill_col3 = st.columns(3, gap="large")

    with skill_col1:
        st.markdown("##### ✅ Matched Skills")
        st.caption(f"Recognized skills found in both documents ({len(matched_skills)}):")
        render_skill_pills(matched_skills, "skill-pill-matched", "No recognized skills matched.")

    with skill_col2:
        st.markdown("##### ⚠️ Potential Skill Gaps")
        st.caption(f"Recognized JD skills not detected in resume ({len(missing_skills)}):")
        render_skill_pills(missing_skills, "skill-pill-missing", "None — all recognized JD skills were detected!")
        if missing_skills:
            st.caption(
                "<span style='color: #6b7280; font-size: 0.775rem;'>"
                "* Note: Indicates absence in resume wording, not necessarily a lack of candidate ability."
                "</span>",
                unsafe_allow_html=True,
            )

    with skill_col3:
        st.markdown("##### 💡 Additional Resume Skills")
        st.caption(f"Detected in resume but not requested in JD ({len(additional_skills)}):")
        render_skill_pills(additional_skills, "skill-pill-additional", "No additional recognized skills detected.")

    # C. Score Explanation
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    st.subheader("📐 Score Explanation")

    w_text_str = f"{int(DEFAULT_TEXT_WEIGHT * 100)}%"
    w_skill_str = f"{int(DEFAULT_SKILL_WEIGHT * 100)}%"

    if res.get("skill_match") is not None:
        st.markdown(
            f"""
            - **Configured Weights**: Text Similarity: `{w_text_str}`, Skill Match: `{w_skill_str}` (from `src/scoring.py`).
            - **Formula**: `Combined Score = ({w_text_str} × {res['text_similarity']:.2f}) + ({w_skill_str} × {res['skill_match']:.2f}) = {res['combined_score']:.2f}%`.
            - **Interpretation**: The score rewards both overall terminology similarity and specific recognized keyword alignment.
            """
        )
    else:
        st.markdown(
            f"""
            - **Configured Weights**: Text Similarity: `{w_text_str}`, Skill Match: `{w_skill_str}` (from `src/scoring.py`).
            - **Formula Status**: `Combined Score` is **unavailable** because the job description did not contain any skills recognized by the built-in dictionary.
            - **Rationale**: Silently defaulting missing skill requirements to 0% would arbitrarily penalize candidates. The system requires both component scores to produce a combined score.
            """
        )

    # D. Actionable Recommendations
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    st.subheader("💡 Tailoring Recommendations")

    recs = []

    if missing_skills:
        skills_str = ", ".join(f"`{s}`" for s in missing_skills)
        recs.append(
            f"**Address Potential Skill Gaps**: If you have demonstrable hands-on experience with {skills_str}, "
            "explicitly describe your practical usage within your project or work history bullet points."
        )

    if res.get("text_similarity", 0.0) < 25.0:
        recs.append(
            "**Align Project Descriptions & Terminology**: Your text similarity is relatively low compared to the JD phrasing. "
            "Consider incorporating terminology, system architecture keywords, and specific responsibilities mentioned in the job post."
        )

    if additional_skills:
        add_str = ", ".join(f"`{s}`" for s in additional_skills[:4])
        suffix = "..." if len(additional_skills) > 4 else ""
        recs.append(
            f"**Highlight Transferable Competencies**: Your resume shows proficiency in {add_str}{suffix}. "
            "Connect these capabilities to the target role's goals to showcase domain versatility."
        )

    if not required_skills:
        recs.append(
            "**Review Job Description Wording**: The JD did not contain recognized keywords from the standard dictionary. "
            "Ensure the pasted text includes the requirements or qualifications section."
        )

    recs.append(
        "**Maintain Truthful Accuracy**: Tailoring should clarify and highlight authentic accomplishments. "
        "Never add technologies, qualifications, or metrics that you cannot confidently substantiate in an interview."
    )

    for rec in recs:
        st.markdown(f"- {rec}")
