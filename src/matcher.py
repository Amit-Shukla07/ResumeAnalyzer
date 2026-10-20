"""
TF-IDF Text Matching Engine for Resume & Job Description.

Uses scikit-learn's TfidfVectorizer and cosine_similarity to compute
lexical and n-gram similarity between preprocessed resume and job description text.

IMPORTANT NOTE:
The output of this module represents lexical and n-gram similarity between two documents.
It is an NLP text overlap metric and MUST NOT be interpreted as a hiring probability,
qualification assessment, or candidate suitability prediction.
"""

from typing import Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessing import preprocess_text


class TFIDFMatcher:
    """
    TF-IDF Vectorizer and Cosine Similarity Matcher.

    Configured with unigrams and bigrams (ngram_range=(1, 2)) and sublinear_tf=True
    to dampen the impact of repeated words.
    """

    def __init__(
        self,
        ngram_range: tuple[int, int] = (1, 2),
        sublinear_tf: bool = True,
        token_pattern: str = r"(?u)\S+",
    ) -> None:
        """
        Initialize the TF-IDF Matcher.

        Args:
            ngram_range: Lower and upper boundary of range of n-values for n-grams.
            sublinear_tf: Apply sublinear tf scaling (1 + log(tf)).
            token_pattern: Regular expression denoting what constitutes a "token".
                           Defaults to non-whitespace tokens to preserve technical
                           terms like C++, C#, .NET, and Node.js after preprocessing.
        """
        self.ngram_range = ngram_range
        self.sublinear_tf = sublinear_tf
        self.token_pattern = token_pattern

    def compute_similarity(
        self,
        resume_text: Optional[str],
        jd_text: Optional[str],
    ) -> float:
        """
        Compute TF-IDF cosine similarity between resume text and job description text.

        Steps:
        1. Preprocess both documents using src.preprocessing.preprocess_text.
        2. Handle empty/None inputs safely by returning 0.0.
        3. Fit TfidfVectorizer on the two preprocessed documents.
        4. Compute pairwise cosine similarity.
        5. Return a bounded percentage score between 0.0 and 100.0.

        Args:
            resume_text: Raw or extracted candidate resume text.
            jd_text: Raw or extracted job description text.

        Returns:
            float: Text similarity score between 0.0 and 100.0 (rounded to 2 decimal places).
        """
        clean_resume = preprocess_text(resume_text)
        clean_jd = preprocess_text(jd_text)

        if not clean_resume or not clean_jd:
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                ngram_range=self.ngram_range,
                sublinear_tf=self.sublinear_tf,
                token_pattern=self.token_pattern,
            )
            tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            raw_score = float(similarity_matrix[0][0]) * 100.0
            if np.isnan(raw_score):
                return 0.0
            bounded_score = float(np.clip(raw_score, 0.0, 100.0))
            return round(bounded_score, 2)
        except ValueError:
            # Handles edge cases such as empty vocabulary after tokenization
            return 0.0


def compute_tfidf_similarity(
    resume_text: Optional[str],
    jd_text: Optional[str],
) -> float:
    """
    Convenience function for computing TF-IDF similarity between resume and JD.

    Args:
        resume_text: Resume text string.
        jd_text: Job description text string.

    Returns:
        float: Similarity score between 0.0 and 100.0.
    """
    matcher = TFIDFMatcher()
    return matcher.compute_similarity(resume_text, jd_text)
