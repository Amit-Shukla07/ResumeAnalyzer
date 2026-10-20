"""
Unit tests for text preprocessing module.
"""

from src.preprocessing import preprocess_text, normalize_whitespace


class TestTextPreprocessing:
    """Tests covering text normalization, edge cases, and technical term preservation."""

    def test_normal_text(self):
        """Verify standard text with simple punctuation and casing."""
        raw = "Senior Software Engineer with extensive experience in cloud computing."
        expected = "senior software engineer with extensive experience in cloud computing"
        assert preprocess_text(raw) == expected

    def test_empty_string(self):
        """Verify empty string returns empty string."""
        assert preprocess_text("") == ""
        assert preprocess_text("   ") == ""

    def test_none_input(self):
        """Verify None input is safely handled without raising an exception."""
        assert preprocess_text(None) == ""

    def test_non_string_input(self):
        """Verify non-string types (numbers) are converted and cleaned safely."""
        assert preprocess_text(12345) == "12345"

    def test_extra_whitespace(self):
        """Verify multiple spaces, tabs, and newlines are normalized to a single space."""
        raw = "   Leading spaces\t\twith tabs\r\nand multiple\n\nnewlines   "
        expected = "leading spaces with tabs and multiple newlines"
        assert preprocess_text(raw) == expected

    def test_normalize_whitespace_helper(self):
        """Verify normalize_whitespace helper directly."""
        raw = "  hello   world \n test \t 123  "
        assert normalize_whitespace(raw) == "hello world test 123"
        assert normalize_whitespace("") == ""

    def test_technical_terms(self):
        """
        Verify preservation of critical technical terms:
        C++, C#, .NET, Node.js, and REST APIs.
        """
        raw = "Hands-on experience with C++, C#, .NET, Node.js, and REST APIs."
        result = preprocess_text(raw)

        # Ensure terms are not stripped or mangled
        assert "c++" in result
        assert "c#" in result
        assert ".net" in result
        assert "node.js" in result
        assert "rest apis" in result

    def test_technical_terms_additional(self):
        """Verify other common tech terms like CI/CD, TCP/IP, and React.js."""
        raw = "Managed CI/CD pipelines, TCP/IP networking, and Vue.js / React.js frontends."
        result = preprocess_text(raw)
        assert "ci/cd" in result
        assert "tcp/ip" in result
        assert "vue.js" in result
        assert "react.js" in result

    def test_numbers_and_punctuation(self):
        """Verify text containing numbers, versioning, percentages, and punctuation."""
        raw = "Built microservices using Python 3.12 (Achieved 99.9% uptime across 10+ regions)."
        result = preprocess_text(raw)
        # Brackets removed, lowercase applied, versions and numbers preserved
        assert "python 3.12" in result
        assert "99.9%" in result
        assert "10+" in result
        assert "(" not in result
        assert ")" not in result

    def test_bullets_and_formatting(self):
        """Verify resume bullet symbols (•, ▪, ★, etc.) are stripped cleanly."""
        raw = "• Developed RESTful services\n▪ Optimized SQL queries\n★ Led team of 5 engineers"
        result = preprocess_text(raw)
        assert "•" not in result
        assert "▪" not in result
        assert "★" not in result
        assert result == "developed restful services optimized sql queries led team of 5 engineers"

    def test_sentence_ending_period_vs_embedded_period(self):
        """
        Verify trailing periods at the end of sentences are stripped
        while preserving internal/leading periods (.NET, node.js).
        """
        raw = "Skilled in Node.js. Also proficient in .NET."
        result = preprocess_text(raw)
        assert result == "skilled in node.js also proficient in .net"
