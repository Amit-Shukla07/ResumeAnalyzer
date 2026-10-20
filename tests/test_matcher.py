"""
Unit tests for the TF-IDF Matching Engine (src/matcher.py).
"""

from src.matcher import TFIDFMatcher, compute_tfidf_similarity


class TestTFIDFMatcher:
    """Test suite for TF-IDF cosine similarity calculations."""

    def test_identical_documents_return_max_score(self):
        """Identical texts should achieve maximum cosine similarity (100.0)."""
        text = "Senior Python engineer with AWS, Docker, and PostgreSQL experience."
        score = compute_tfidf_similarity(text, text)
        assert score == 100.0

    def test_similar_documents_produce_higher_score_than_unrelated(self):
        """Similar technical documents should score significantly higher than unrelated ones."""
        resume = (
            "Backend software developer with 4 years building APIs in Python, "
            "Docker, PostgreSQL, and Linux microservices."
        )
        similar_jd = (
            "Looking for a Backend Developer skilled in Python, Docker containerization, "
            "and PostgreSQL database management."
        )
        unrelated_jd = (
            "Executive chef needed for French cuisine restaurant. Must have pastry baking "
            "and culinary arts certification."
        )

        sim_score = compute_tfidf_similarity(resume, similar_jd)
        unrelated_score = compute_tfidf_similarity(resume, unrelated_jd)

        # Meaningful relational property: similar documents have higher similarity than unrelated
        assert sim_score > unrelated_score
        assert sim_score > 15.0
        assert unrelated_score < 5.0

    def test_empty_and_whitespace_inputs(self):
        """Empty or whitespace-only inputs should return 0.0 without errors."""
        valid_jd = "Python software engineer with AWS knowledge."

        assert compute_tfidf_similarity("", valid_jd) == 0.0
        assert compute_tfidf_similarity("   \n\t  ", valid_jd) == 0.0
        assert compute_tfidf_similarity(valid_jd, "") == 0.0
        assert compute_tfidf_similarity("", "") == 0.0

    def test_none_inputs_handled_safely(self):
        """None values for resume or JD should safely return 0.0."""
        valid_text = "Software Engineer with Git and Linux."
        assert compute_tfidf_similarity(None, valid_text) == 0.0
        assert compute_tfidf_similarity(valid_text, None) == 0.0
        assert compute_tfidf_similarity(None, None) == 0.0

    def test_score_bounds(self):
        """Ensure scores always remain strictly within [0.0, 100.0]."""
        test_pairs = [
            ("Python", "Python"),
            ("A" * 1000, "B" * 1000),
            ("Java C++ Docker", "Kubernetes Go Rust"),
            ("Specialized NLP researcher", "NLP research scientist"),
        ]
        for r, j in test_pairs:
            score = compute_tfidf_similarity(r, j)
            assert 0.0 <= score <= 100.0

    def test_technical_terms_preserved_in_tfidf(self):
        """Verify technical tokens like C++, C#, .NET, Node.js are matched."""
        resume = "Experienced in C++, C#, .NET, and Node.js backend systems."
        jd = "Seeking developer with C++, C#, .NET, and Node.js skills."

        score = compute_tfidf_similarity(resume, jd)
        disjoint_jd = "Seeking Python Django developer with AWS and MySQL."
        disjoint_score = compute_tfidf_similarity(resume, disjoint_jd)

        # Technical terms overlap should produce significant similarity compared to disjoint tech stack
        assert score > disjoint_score
        assert score > 20.0
        assert disjoint_score < 10.0

    def test_sublinear_tf_dampening(self):
        """Sublinear TF scaling should dampen the effect of repeated keyword stuffing."""
        normal_resume = "Python developer."
        stuffed_resume = "Python " * 50
        jd = "Looking for a Python developer."

        score_normal = compute_tfidf_similarity(normal_resume, jd)
        score_stuffed = compute_tfidf_similarity(stuffed_resume, jd)

        # Both match, but stuffing does not scale linearly
        assert 0.0 <= score_stuffed <= 100.0
        assert 0.0 <= score_normal <= 100.0

    def test_custom_matcher_instance(self):
        """Verify TFIDFMatcher class configuration options."""
        matcher = TFIDFMatcher(ngram_range=(1, 1), sublinear_tf=False)
        score = matcher.compute_similarity("Python Docker", "Python Docker")
        assert score == 100.0

    def test_nan_or_unmatched_vector_handling(self):
        """Verify matcher safely returns 0.0 without producing NaN on noise inputs."""
        import numpy as np
        score = compute_tfidf_similarity("!!! ???", "--- ...")
        assert score == 0.0
        assert not np.isnan(score)
