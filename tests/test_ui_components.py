"""
Unit tests for UI Components and Design System helpers (src/ui_components.py).
"""

from unittest.mock import patch
from src.ui_components import (
    render_navbar,
    render_hero,
    render_svg_gauge,
    render_combined_score_hero,
    render_metric_grid,
    render_skill_pills,
    extract_resume_evidence,
    render_evidence_section,
    render_recommendation_cards,
)


class TestUIComponents:
    """Test suite verifying UI helper rendering, SVG generation, and evidence extraction."""

    def test_render_svg_gauge_with_scores(self):
        """Test SVG gauge generation across high, medium, low, and boundary scores."""
        # High score (emerald)
        svg_high = render_svg_gauge(85.0)
        assert "85.0%" in svg_high
        assert "#34D399" in svg_high
        assert "ALIGNMENT" in svg_high

        # Moderate score (violet)
        svg_med = render_svg_gauge(55.0)
        assert "55.0%" in svg_med
        assert "#818CF8" in svg_med

        # Low score (cyan)
        svg_low = render_svg_gauge(25.0)
        assert "25.0%" in svg_low
        assert "#22D3EE" in svg_low

        # Unavailable score (None)
        svg_none = render_svg_gauge(None)
        assert "N/A" in svg_none
        assert "UNAVAILABLE" in svg_none

        # Boundary clamping (above 100, below 0)
        svg_clamped_high = render_svg_gauge(120.0)
        assert "120.0%" in svg_clamped_high
        svg_clamped_low = render_svg_gauge(-10.0)
        assert "-10.0%" in svg_clamped_low

    def test_extract_resume_evidence(self):
        """Test extraction of contextual evidence sentences for matched skills."""
        resume_text = (
            "Professional Summary:\n"
            "• Built high-performance distributed microservices using Python and Docker.\n"
            "• Managed cloud deployments on AWS infrastructure using Terraform and Git version control.\n"
            "• Optimized relational queries on PostgreSQL databases with index tuning.\n"
        )
        matched_skills = ["Python", "Docker", "AWS", "PostgreSQL", "Git"]

        evidence = extract_resume_evidence(resume_text, matched_skills, max_snippets=3)
        assert len(evidence) <= 3
        skills_found = [e["skill"] for e in evidence]
        assert "Python" in skills_found
        assert all(len(e["snippet"]) >= 20 for e in evidence)

    def test_extract_resume_evidence_empty_inputs(self):
        """Test evidence extraction safely handles empty inputs."""
        assert extract_resume_evidence("", ["Python"]) == []
        assert extract_resume_evidence("Some resume text here", []) == []
        assert extract_resume_evidence("", []) == []

    @patch("streamlit.markdown")
    def test_render_navbar_and_hero(self, mock_markdown):
        """Verify navbar and hero call streamlit.markdown with expected keywords."""
        render_navbar()
        assert mock_markdown.called
        navbar_html = mock_markdown.call_args[0][0]
        assert "ResumeAnalyzer" in navbar_html
        assert "CAREER INTELLIGENCE" in navbar_html

        render_hero()
        hero_html = mock_markdown.call_args[0][0]
        assert "Make your next move with confidence" in hero_html

    @patch("streamlit.markdown")
    def test_render_combined_score_hero(self, mock_markdown):
        """Verify combined score hero renders properly for available and unavailable scores."""
        res_available = {
            "combined_score": 75.0,
            "text_similarity": 20.0,
            "skill_match": 88.75,
        }
        render_combined_score_hero(res_available, text_weight_pct=20, skill_weight_pct=80)
        hero_html = mock_markdown.call_args[0][0]
        assert "Strong Overall Alignment" in hero_html
        assert "75.0%" in hero_html

        # Moderate score
        render_combined_score_hero({"combined_score": 50.0}, text_weight_pct=20, skill_weight_pct=80)
        assert "Moderate Overall Alignment" in mock_markdown.call_args[0][0]

        # Low score
        render_combined_score_hero({"combined_score": 20.0}, text_weight_pct=20, skill_weight_pct=80)
        assert "Limited Direct Overlap" in mock_markdown.call_args[0][0]

        # None score
        render_combined_score_hero({"combined_score": None}, text_weight_pct=20, skill_weight_pct=80)
        assert "Alignment Metric Unavailable" in mock_markdown.call_args[0][0]

    @patch("streamlit.markdown")
    def test_render_metric_grid(self, mock_markdown):
        """Verify metric grid displays all 4 supporting metric values."""
        res = {
            "text_similarity": 28.5,
            "skill_match": 75.0,
            "matched_skills": ["Python", "Git", "Docker"],
            "missing_skills": ["AWS"],
            "required_skills": ["Python", "Git", "Docker", "AWS"],
        }
        render_metric_grid(res)
        grid_html = mock_markdown.call_args[0][0]
        assert "28.5%" in grid_html
        assert "75.0%" in grid_html
        assert "3" in grid_html
        assert "1" in grid_html

    @patch("streamlit.markdown")
    def test_render_skill_pills(self, mock_markdown):
        """Verify skill pills render lists or display empty messages."""
        render_skill_pills(["Python", "Docker"], "skill-pill-matched", "No skills")
        assert "Python" in mock_markdown.call_args[0][0]
        assert "Docker" in mock_markdown.call_args[0][0]

        render_skill_pills([], "skill-pill-missing", "All skills detected!")
        assert "All skills detected!" in mock_markdown.call_args[0][0]

    @patch("streamlit.markdown")
    def test_render_evidence_section(self, mock_markdown):
        """Verify requirement evidence section formatting."""
        evidence = [
            {"skill": "Python", "snippet": "Engineered automated data pipelines in Python and Pandas."},
            {"skill": "Docker", "snippet": "Containerized backend services using Docker."},
        ]
        render_evidence_section(evidence)
        ev_html = mock_markdown.call_args[0][0]
        assert "Python" in ev_html
        assert "Docker" in ev_html
        assert "Requirement Evidence" in ev_html

        # Calling with empty evidence should not call markdown
        mock_markdown.reset_mock()
        render_evidence_section([])
        assert not mock_markdown.called

    @patch("streamlit.markdown")
    def test_render_recommendation_cards(self, mock_markdown):
        """Verify recommendation card generation across multiple conditions."""
        render_recommendation_cards(
            missing_skills=["AWS", "Kubernetes"],
            text_similarity=18.0,
            additional_skills=["Node.js", "React"],
            required_skills=["Python", "AWS", "Kubernetes"],
        )
        rec_html = mock_markdown.call_args[0][0]
        assert "Address Identified Skill Gaps" in rec_html
        assert "Align Industry & Domain Vocabulary" in rec_html
        assert "Spotlight Complementary Competencies" in rec_html
        assert "Maintain Verifiable Accuracy" in rec_html
