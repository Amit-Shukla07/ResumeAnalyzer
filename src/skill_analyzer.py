"""
Dictionary-Based Skill Extraction & Analysis Module.

Extracts technical skills and tools from resumes and job descriptions using
a curated, domain-specific regular expression dictionary.

IMPORTANT ARCHITECTURAL NOTE:
This module performs deterministic dictionary-based keyword matching with boundary
and context checks. It is NOT a trained Named Entity Recognition (NER) model.
Dictionary-based extraction provides fast, explainable, and zero-hallucination skill
detection, but recognizes only the vocabulary defined in the dictionary.
"""

import re
from typing import Optional, Union


# Curated, editable dictionary mapping canonical skill names to regex patterns.
# Uses explicit boundaries and negative lookarounds to avoid substring false positives
# (e.g. "Java" vs "JavaScript", "C" vs "C++" vs "C#", "SQL" vs "PostgreSQL",
# and preventing standalone words like "next" or "node" from triggering without ".js").
DEFAULT_SKILL_PATTERNS: dict[str, str] = {
    "Python": r"(?<![a-zA-Z0-9])python(?![a-zA-Z0-9])",
    "Java": r"(?<![a-zA-Z0-9._-])java(?![a-zA-Z0-9])",
    "JavaScript": r"(?<![a-zA-Z0-9._-])(?:javascript|js)(?![a-zA-Z0-9])",
    "TypeScript": r"(?<![a-zA-Z0-9._-])typescript(?![a-zA-Z0-9])",
    "C": r"(?<![a-zA-Z0-9+#\-_])c(?![a-zA-Z0-9+#])",
    "C++": r"(?<![a-zA-Z0-9])c\+\+(?![a-zA-Z0-9+])",
    "C#": r"(?<![a-zA-Z0-9])(?:c#|c\s*sharp)(?![a-zA-Z0-9#])",
    ".NET": r"(?<![a-zA-Z0-9])(?:\.net|dotnet|asp\.net)(?![a-zA-Z0-9])",
    "React": r"(?<![a-zA-Z0-9])react(?:\.js|js)?(?![a-zA-Z0-9])",
    "Next.js": r"(?<![a-zA-Z0-9])next(?:\.js|js|\s+js)(?![a-zA-Z0-9])",
    "Node.js": r"(?<![a-zA-Z0-9])node(?:\.js|js|\s+js)(?![a-zA-Z0-9])",
    "Express": r"(?<![a-zA-Z0-9])(?:express(?:\.js|js)|express\s+framework|express\s+backend|\bexpress\b(?!\s+(?:interest|gratitude|enthusiasm|opinion|concerns|desire|myself|ourselves|ideas|clearly|an?\b|the\b|my\b|our\b|your\b)))(?![a-zA-Z0-9])",  # noqa: E501
    "SQL": r"(?<![a-zA-Z0-9])sql(?![a-zA-Z0-9])",
    "MySQL": r"(?<![a-zA-Z0-9])mysql(?![a-zA-Z0-9])",
    "PostgreSQL": r"(?<![a-zA-Z0-9])(?:postgresql|postgres)(?![a-zA-Z0-9])",
    "MongoDB": r"(?<![a-zA-Z0-9])(?:mongodb|mongo)(?![a-zA-Z0-9])",
    "Machine Learning": r"(?<![a-zA-Z0-9])machine\s+learning(?![a-zA-Z0-9])",
    "Deep Learning": r"(?<![a-zA-Z0-9])deep\s+learning(?![a-zA-Z0-9])",
    "NLP": r"(?<![a-zA-Z0-9])(?:nlp|natural\s+language\s+processing)(?![a-zA-Z0-9])",
    "Data Structures": r"(?<![a-zA-Z0-9])data\s+structures?(?![a-zA-Z0-9])",
    "Algorithms": r"(?<![a-zA-Z0-9])algorithms?(?![a-zA-Z0-9])",
    "Git": r"(?<![a-zA-Z0-9])git(?![a-zA-Z0-9])",
    "Docker": r"(?<![a-zA-Z0-9])docker(?![a-zA-Z0-9])",
    "REST API": r"(?<![a-zA-Z0-9])(?:rest\s*apis?|restful\s*apis?|rest\s+endpoints?)(?![a-zA-Z0-9])",
    "Pandas": r"(?<![a-zA-Z0-9])pandas(?![a-zA-Z0-9])",
    "NumPy": r"(?<![a-zA-Z0-9])numpy(?![a-zA-Z0-9])",
    "TensorFlow": r"(?<![a-zA-Z0-9])tensorflow(?![a-zA-Z0-9])",
    "PyTorch": r"(?<![a-zA-Z0-9])pytorch(?![a-zA-Z0-9])",
    "AWS": r"(?<![a-zA-Z0-9])(?:aws|amazon\s+web\s+services)(?![a-zA-Z0-9])",
    "Linux": r"(?<![a-zA-Z0-9])linux(?![a-zA-Z0-9])",
}


class SkillAnalyzer:
    """
    Skill extraction and comparison engine based on dictionary pattern matching.
    """

    def __init__(self, skill_patterns: Optional[dict[str, str]] = None) -> None:
        """
        Initialize with a skill pattern dictionary.

        Args:
            skill_patterns: Optional dictionary mapping canonical skill names to regex patterns.
                            Defaults to DEFAULT_SKILL_PATTERNS.
        """
        patterns = skill_patterns or DEFAULT_SKILL_PATTERNS
        self.skill_patterns = patterns
        # Precompile regexes for performance
        self._compiled_patterns = {
            skill: re.compile(pattern, re.IGNORECASE)
            for skill, pattern in patterns.items()
        }

    def extract_skills(self, text: Optional[Union[str, bytes]]) -> list[str]:
        """
        Extract unique recognized skills from a given text.

        Args:
            text: Raw or preprocessed text string.

        Returns:
            list[str]: Deduplicated, sorted list of canonical skill names detected.
        """
        if not text or not isinstance(text, str):
            return []

        detected = []
        for skill_name, compiled_regex in self._compiled_patterns.items():
            if compiled_regex.search(text):
                detected.append(skill_name)

        return sorted(detected)

    def analyze_skills(
        self,
        resume_text: Optional[str],
        jd_text: Optional[str],
    ) -> dict[str, list[str]]:
        """
        Compare skills between a candidate resume and a job description.

        Args:
            resume_text: Candidate resume text.
            jd_text: Job description text.

        Returns:
            dict with:
                - resume_skills: Recognized skills found in the resume.
                - required_skills: Recognized skills found in the JD.
                - matched_skills: Recognized skills present in both resume and JD.
                - missing_skills: Recognized JD skills not found in the resume.
        """
        resume_skills = self.extract_skills(resume_text)
        required_skills = self.extract_skills(jd_text)

        matched_skills = sorted(list(set(resume_skills).intersection(set(required_skills))))
        missing_skills = sorted(list(set(required_skills).difference(set(resume_skills))))

        return {
            "resume_skills": resume_skills,
            "required_skills": required_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        }


# Module-level convenience functions using default patterns
_default_analyzer = SkillAnalyzer()


def extract_skills(
    text: Optional[str],
    skill_patterns: Optional[dict[str, str]] = None,
) -> list[str]:
    """
    Extract unique recognized skills from text using default or custom patterns.
    """
    if skill_patterns is not None:
        return SkillAnalyzer(skill_patterns).extract_skills(text)
    return _default_analyzer.extract_skills(text)


def analyze_skills(
    resume_text: Optional[str],
    jd_text: Optional[str],
    skill_patterns: Optional[dict[str, str]] = None,
) -> dict[str, list[str]]:
    """
    Analyze skill overlap between resume text and job description text.
    """
    if skill_patterns is not None:
        return SkillAnalyzer(skill_patterns).analyze_skills(resume_text, jd_text)
    return _default_analyzer.analyze_skills(resume_text, jd_text)
