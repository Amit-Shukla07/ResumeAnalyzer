"""
Text Preprocessing Module for Resume & Job Description Matching.

Cleans and normalizes raw text for downstream NLP tasks while preserving
critical domain-specific terms (such as C++, C#, .NET, Node.js, REST APIs).
"""

import re
from typing import Optional


def normalize_whitespace(text: str) -> str:
    """Normalize multiple spaces, tabs, and newlines into single spaces."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def preprocess_text(text: Optional[str]) -> str:
    """
    Preprocess raw text from a resume or job description.

    Steps:
    1. Gracefully handle None, non-string, or empty inputs.
    2. Normalize bullet points, decorative glyphs, and special separators into spaces.
    3. Normalize whitespace (tabs, newlines, carriage returns, consecutive spaces).
    4. Convert to lowercase for uniform keyword matching.
    5. Strip non-semantic punctuation (quotes, brackets, formatting symbols)
       while preserving technical characters:
       - '+' for C++, C++17, etc.
       - '#' for C#
       - '.' for .NET, Node.js, Vue.js, Python 3.12, etc.
       - '/' for CI/CD, TCP/IP, I/O, etc.
       - '-' for front-end, back-end, rest-api, etc.
       - '@' and '_' for emails, handles, identifiers.
    6. Strip sentence-ending / trailing periods and list separators without
       affecting leading dots (.NET) or internal dots (Node.js).
    7. Clean isolated punctuation and collapse excess whitespace.

    Args:
        text: Raw text string (or None/empty).

    Returns:
        str: Preprocessed, normalized lowercase text.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    if not text.strip():
        return ""

    # 1. Normalize bullet point glyphs to spaces
    bullet_pattern = r"[\u2022\u2023\u25E6\u2043\u2219\u25CB\u25CF\u25AA\u25A0\u25C6\u2605\u2713\u2714\u25BA·*]"
    cleaned = re.sub(bullet_pattern, " ", text)

    # 2. Normalize newlines, carriage returns, and tabs to spaces
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)

    # 3. Convert to lowercase for uniform matching
    cleaned = cleaned.lower()

    # 4. Remove brackets, quotes, and non-semantic punctuation
    # Preserves: +, #, ., -, /, @, _, %
    cleaned = re.sub(r"[()\[\]{}<>\"'`~;!?|]", " ", cleaned)

    # 5. Clean list separators (commas and colons) that separate items
    # e.g., "python, c++, c#, .net" -> "python c++ c# .net"
    cleaned = re.sub(r"[,:](?=\s|$)", " ", cleaned)
    cleaned = re.sub(r"(?<=\s)[,:](?=\s|$)", " ", cleaned)

    # 6. Clean sentence-ending / trailing periods
    # Matches one or more periods at the end of a token before whitespace or end of string.
    # Leaves leading dots (.net) and internal dots (node.js, python 3.12) intact.
    cleaned = re.sub(r"\.+(?=\s|$)", "", cleaned)

    # 7. Clean isolated symbols that are not attached to any token (e.g. standalone /, -, --)
    cleaned = re.sub(r"(?<=\s)[-–—\/%]+(?=\s|$)", " ", cleaned)
    cleaned = re.sub(r"^[-–—\/%]+(?=\s|$)", " ", cleaned)

    # 8. Collapse multiple whitespace and strip edges
    return re.sub(r"\s+", " ", cleaned).strip()
