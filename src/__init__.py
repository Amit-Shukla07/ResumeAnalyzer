"""
Resume–JD Matcher Core Modules.
"""

from src.pdf_extractor import (
    extract_text_from_pdf,
    PDFExtractionError,
    CorruptedPDFError,
    NoExtractableTextError,
)
from src.preprocessing import preprocess_text, normalize_whitespace
from src.matcher import TFIDFMatcher, compute_tfidf_similarity
from src.skill_analyzer import (
    DEFAULT_SKILL_PATTERNS,
    SkillAnalyzer,
    extract_skills,
    analyze_skills,
)
from src.scoring import (
    DEFAULT_TEXT_WEIGHT,
    DEFAULT_SKILL_WEIGHT,
    calculate_skill_match,
    calculate_combined_score,
    evaluate_match,
)

__all__ = [
    # PDF Extractor
    "extract_text_from_pdf",
    "PDFExtractionError",
    "CorruptedPDFError",
    "NoExtractableTextError",
    # Preprocessing
    "preprocess_text",
    "normalize_whitespace",
    # Matcher
    "TFIDFMatcher",
    "compute_tfidf_similarity",
    # Skill Analyzer
    "DEFAULT_SKILL_PATTERNS",
    "SkillAnalyzer",
    "extract_skills",
    "analyze_skills",
    # Scoring
    "DEFAULT_TEXT_WEIGHT",
    "DEFAULT_SKILL_WEIGHT",
    "calculate_skill_match",
    "calculate_combined_score",
    "evaluate_match",
]
