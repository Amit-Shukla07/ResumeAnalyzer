"""
Unit tests for Scoring and Evaluation Engine (src/scoring.py).
"""

import pytest
from src.scoring import (
    calculate_skill_match,
    calculate_combined_score,
    evaluate_match,
)


class TestScoring:
    """Test suite for individual and composite heuristic scoring functions."""

    def test_skill_match_calculation(self):
        """Verify matched / total * 100 ratio calculation."""
        matched = ["Python", "SQL"]
        required = ["Python", "SQL", "Git", "Docker"]
        # 2 / 4 = 50.0%
        assert calculate_skill_match(matched, required) == 50.0

        # All matched = 100.0%
        assert calculate_skill_match(["Python", "SQL"], ["Python", "SQL"]) == 100.0

        # None matched = 0.0%
        assert calculate_skill_match([], ["Python", "SQL"]) == 0.0

    def test_no_recognized_skills_in_jd_returns_none(self):
        """
        When JD contains no recognized skills, skill_match must be marked
        as unavailable (None) rather than 0.0.
        """
        assert calculate_skill_match(matched_skills=[], required_skills=[]) is None
        assert calculate_skill_match(matched_skills=["Python"], required_skills=[]) is None

    def test_combined_score_formula_and_weights(self):
        """
        Verify default combined_score = 0.2 * text_similarity + 0.8 * skill_match.
        e.g., text=75.2, skill=66.67 -> combined = 0.2 * 75.2 + 0.8 * 66.67 = 15.04 + 53.336 = 68.38.
        Also verifies configurable weights when overridden.
        """
        # Default weights (20% text, 80% skills)
        combined_default = calculate_combined_score(
            text_similarity=75.2,
            skill_match=66.67,
        )
        assert combined_default == 68.38

        # Explicit weights
        combined_explicit = calculate_combined_score(
            text_similarity=75.2,
            skill_match=66.67,
            text_weight=0.2,
            skill_weight=0.8,
        )
        assert combined_explicit == 68.38

    def test_combined_score_when_skill_match_unavailable_is_none(self):
        """
        If skill_match is unavailable (None), combined_score must be None,
        not silently defaulting to 0.2 * text_similarity.
        """
        score = calculate_combined_score(text_similarity=85.0, skill_match=None)
        assert score is None

    def test_weight_normalization(self):
        """Weights that do not sum to 1.0 should be normalized automatically."""
        # text_weight=1, skill_weight=4 -> normalized: 0.2 and 0.8
        # 0.2 * 80 + 0.8 * 60 = 16 + 48 = 64.0
        score1 = calculate_combined_score(80.0, 60.0, text_weight=0.2, skill_weight=0.8)
        score2 = calculate_combined_score(80.0, 60.0, text_weight=1.0, skill_weight=4.0)
        assert score1 == score2 == 64.0

    def test_invalid_weights_raise_value_error(self):
        """Negative weights or both weights zero should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            calculate_combined_score(50.0, 50.0, text_weight=-0.2, skill_weight=0.8)

        with pytest.raises(ValueError, match="greater than zero"):
            calculate_combined_score(50.0, 50.0, text_weight=0.0, skill_weight=0.0)

    def test_score_bounds(self):
        """Scores must remain within [0.0, 100.0]."""
        for t in [0.0, 50.0, 100.0]:
            for s in [0.0, 50.0, 100.0]:
                score = calculate_combined_score(t, s)
                assert 0.0 <= score <= 100.0

    def test_evaluate_match_standard_structure(self):
        """
        Verify evaluate_match integration produces the exact required dictionary format
        and calculated numerical values.
        """
        resume = "Senior Python engineer with Docker, SQL, and Git."
        jd = "Seeking a developer proficient in Python, SQL, Git, and Docker."

        result = evaluate_match(resume, jd)

        expected_keys = {
            "text_similarity",
            "skill_match",
            "combined_score",
            "resume_skills",
            "required_skills",
            "matched_skills",
            "missing_skills",
        }
        assert set(result.keys()) == expected_keys

        # Since all skills in JD are present in resume:
        assert result["skill_match"] == 100.0
        assert result["missing_skills"] == []
        assert len(result["matched_skills"]) == 4
        assert 0.0 <= result["text_similarity"] <= 100.0
        assert 0.0 <= result["combined_score"] <= 100.0

    def test_evaluate_match_with_no_jd_skills(self):
        """Verify behavior when JD has no recognized skills."""
        resume = "Experienced in Python and Docker."
        jd = "We need an enthusiastic, fast learner who communicates clearly."

        result = evaluate_match(resume, jd)
        assert result["required_skills"] == []
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []
        assert result["skill_match"] is None
        assert result["combined_score"] is None
        assert 0.0 <= result["text_similarity"] <= 100.0

    def test_evaluate_match_with_empty_inputs(self):
        """Verify evaluate_match handles empty string inputs safely."""
        result = evaluate_match("", "")
        assert result["text_similarity"] == 0.0
        assert result["skill_match"] is None
        assert result["combined_score"] is None
        assert result["resume_skills"] == []
        assert result["required_skills"] == []
