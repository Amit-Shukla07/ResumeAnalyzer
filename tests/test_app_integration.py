"""
Integration and UI-facing logic tests for Streamlit application (app.py).
"""

import io
from pathlib import Path
import pymupdf
from streamlit.testing.v1 import AppTest

from src.pdf_extractor import extract_text_from_pdf
from src.scoring import evaluate_match, DEFAULT_TEXT_WEIGHT, DEFAULT_SKILL_WEIGHT


def create_sample_pdf(text: str) -> io.BytesIO:
    """Create an in-memory PDF stream containing given text."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    bio = io.BytesIO(pdf_bytes)
    bio.name = "resume.pdf"
    return bio


class TestAppIntegration:
    """Test suite verifying end-to-end integration and Streamlit UI behavior."""

    def test_app_starts_cleanly_via_apptest(self):
        """Verify app initializes without exceptions or syntax issues."""
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        at = AppTest.from_file(str(app_path), default_timeout=10)
        at.run()
        assert not at.exception
        # Ensure header rendered
        assert any("ResumeAnalyzer" in str(getattr(h, "value", "")) for h in at.markdown)

    def test_end_to_end_analysis_pipeline(self):
        """Verify full pipeline: in-memory PDF -> extraction -> evaluate_match."""
        pdf_stream = create_sample_pdf("Senior Engineer with Python, Docker, and Git.")
        extracted_text = extract_text_from_pdf(pdf_stream)
        assert "Python" in extracted_text

        jd_text = "Looking for a software engineer skilled in Python, Docker, Git, and AWS."
        result = evaluate_match(extracted_text, jd_text)

        # 3 of 4 skills matched
        assert result["skill_match"] == 75.0
        assert result["matched_skills"] == ["Docker", "Git", "Python"]
        assert result["missing_skills"] == ["AWS"]
        assert result["text_similarity"] > 10.0
        assert result["combined_score"] is not None

        # Verify additional skills calculation
        additional_skills = sorted(list(set(result["resume_skills"]) - set(result["required_skills"])))
        assert additional_skills == []

    def test_unavailable_scores_when_jd_has_no_recognized_skills(self):
        """Verify that when JD has no recognized skills, skill_match and combined_score are None."""
        resume_text = "Proficient in Python, C++, and Docker."
        generic_jd = "We need an energetic, creative, and enthusiastic self-starter."

        result = evaluate_match(resume_text, generic_jd)
        assert result["required_skills"] == []
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []
        assert result["skill_match"] is None
        assert result["combined_score"] is None
        assert 0.0 <= result["text_similarity"] <= 100.0

    def test_empty_input_handling_in_backend(self):
        """Verify evaluate_match handles empty text inputs without crashing."""
        result = evaluate_match("", "")
        assert result["text_similarity"] == 0.0
        assert result["skill_match"] is None
        assert result["combined_score"] is None

    def test_configured_weights_used_in_combined_score(self):
        """Verify scoring respects DEFAULT_TEXT_WEIGHT and DEFAULT_SKILL_WEIGHT."""
        text_sim = 80.0
        skill_score = 60.0
        expected = round(DEFAULT_TEXT_WEIGHT * text_sim + DEFAULT_SKILL_WEIGHT * skill_score, 2)

        # 0.2 * 80 + 0.8 * 60 = 16 + 48 = 64.0
        assert expected == 64.0
