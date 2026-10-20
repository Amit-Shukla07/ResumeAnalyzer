"""
Scoring and Evaluation Engine for Resume–JD Matching.

Calculates independent text similarity and skill match metrics, alongside
a configurable composite heuristic score.

IMPORTANT DISCLAIMER:
All metrics produced by this module are heuristic indicators designed to assist human
reviewers by measuring text and skill overlap against a specific job description.
They ARE NOT predictive models of candidate competence, performance, or hiring success.
"""

from typing import Optional
import numpy as np

from src.matcher import compute_tfidf_similarity
from src.skill_analyzer import analyze_skills


DEFAULT_TEXT_WEIGHT: float = 0.2
DEFAULT_SKILL_WEIGHT: float = 0.8


def calculate_skill_match(
    matched_skills: list[str],
    required_skills: list[str],
) -> Optional[float]:
    """
    Calculate the percentage of recognized required skills satisfied by the resume.

    Formula:
        (total matched skills / total recognized required skills) * 100

    Args:
        matched_skills: Skills present in both resume and JD.
        required_skills: Recognized skills required by the JD.

    Returns:
        Optional[float]: Skill match percentage between 0.0 and 100.0,
                         or None if no recognized skills were detected in the JD
                         (marked as unavailable to avoid false penalties).
    """
    if not required_skills:
        return None

    ratio = len(matched_skills) / len(required_skills)
    score = float(np.clip(ratio * 100.0, 0.0, 100.0))
    return round(score, 2)


def calculate_combined_score(
    text_similarity: float,
    skill_match: Optional[float],
    text_weight: float = DEFAULT_TEXT_WEIGHT,
    skill_weight: float = DEFAULT_SKILL_WEIGHT,
) -> Optional[float]:
    """
    Calculate the weighted composite heuristic match score.

    Formula:
        combined_score = (text_weight * text_similarity) + (skill_weight * skill_match)
        (weights are normalized to sum to 1.0)

    Handling Missing/Unavailable Skill Match:
        If `skill_match` is None (because the JD contained no recognized skills),
        this function returns None rather than silently defaulting `skill_match` to 0.0,
        which would arbitrarily penalize the candidate.

    Args:
        text_similarity: TF-IDF cosine similarity score (0.0 to 100.0).
        skill_match: Skill match score (0.0 to 100.0) or None if unavailable.
        text_weight: Relative weight for text similarity (default 0.2).
        skill_weight: Relative weight for skill matching (default 0.8).

    Returns:
        Optional[float]: Combined score between 0.0 and 100.0, or None if skill_match is unavailable.

    Raises:
        ValueError: If weights are negative or both sum to zero.
    """
    if skill_match is None:
        return None

    if text_weight < 0 or skill_weight < 0:
        raise ValueError("Weights must be non-negative numbers.")

    total_weight = text_weight + skill_weight
    if total_weight == 0:
        raise ValueError("The sum of text_weight and skill_weight must be greater than zero.")

    # Normalize weights so they always sum to 1.0
    w_text = text_weight / total_weight
    w_skill = skill_weight / total_weight

    raw_score = (w_text * text_similarity) + (w_skill * skill_match)
    bounded_score = float(np.clip(raw_score, 0.0, 100.0))
    return round(bounded_score, 2)


def evaluate_match(
    resume_text: Optional[str],
    jd_text: Optional[str],
    text_weight: float = DEFAULT_TEXT_WEIGHT,
    skill_weight: float = DEFAULT_SKILL_WEIGHT,
    skill_patterns: Optional[dict[str, str]] = None,
) -> dict:
    """
    Perform a complete matching evaluation between resume text and job description.

    Integrates:
    1. Lexical TF-IDF cosine text similarity (unigrams + bigrams, sublinear TF).
    2. Dictionary-based skill analysis (recognized, matched, and missing skills).
    3. Skill match percentage calculation.
    4. Composite combined score (when skill match is available).

    Args:
        resume_text: Candidate resume text string.
        jd_text: Job description text string.
        text_weight: Configurable weight for text similarity (default 0.2).
        skill_weight: Configurable weight for skill matching (default 0.8).
        skill_patterns: Optional custom skill regex dictionary.

    Returns:
        dict: Standardized match result dictionary:
            {
                "text_similarity": float,          # 0.0 - 100.0
                "skill_match": Optional[float],    # 0.0 - 100.0 or None
                "combined_score": Optional[float], # 0.0 - 100.0 or None
                "resume_skills": list[str],
                "required_skills": list[str],
                "matched_skills": list[str],
                "missing_skills": list[str],
            }
    """
    # 1. Text Similarity
    text_similarity = compute_tfidf_similarity(resume_text, jd_text)

    # 2. Skill Extraction & Analysis
    skills_data = analyze_skills(resume_text, jd_text, skill_patterns=skill_patterns)
    resume_skills = skills_data["resume_skills"]
    required_skills = skills_data["required_skills"]
    matched_skills = skills_data["matched_skills"]
    missing_skills = skills_data["missing_skills"]

    # 3. Component Skill Match Score
    skill_match = calculate_skill_match(matched_skills, required_skills)

    # 4. Optional Combined Score
    combined_score = calculate_combined_score(
        text_similarity=text_similarity,
        skill_match=skill_match,
        text_weight=text_weight,
        skill_weight=skill_weight,
    )

    return {
        "text_similarity": text_similarity,
        "skill_match": skill_match,
        "combined_score": combined_score,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
