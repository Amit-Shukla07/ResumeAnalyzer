"""
Unit tests for Skill Extraction and Analysis (src/skill_analyzer.py).
"""

from src.skill_analyzer import (
    SkillAnalyzer,
    extract_skills,
    analyze_skills,
)


class TestSkillAnalyzer:
    """Test suite for dictionary-based skill extraction and comparison."""

    def test_case_insensitive_matching(self):
        """Skills should be extracted regardless of upper/lower/mixed casing."""
        text = "Proficient in python, DOCKER, Git, and aWs."
        skills = extract_skills(text)
        assert "Python" in skills
        assert "Docker" in skills
        assert "Git" in skills
        assert "AWS" in skills

    def test_duplicate_skills_deduplicated(self):
        """Repeated mentions of a skill must produce a single entry in the output."""
        text = "Git version control. Experienced with git branches, git rebase, and GIT workflows."
        skills = extract_skills(text)
        assert skills.count("Git") == 1

    def test_multiword_skills(self):
        """Verify extraction of multi-word skills like Machine Learning, Deep Learning, REST API."""
        text = (
            "Specialized in Machine Learning, Deep Learning, NLP algorithms, "
            "Data Structures, and REST API development."
        )
        skills = extract_skills(text)
        assert "Machine Learning" in skills
        assert "Deep Learning" in skills
        assert "NLP" in skills
        assert "Algorithms" in skills
        assert "Data Structures" in skills
        assert "REST API" in skills

    def test_c_versus_cpp_and_csharp_distinction(self):
        """
        Verify distinct handling for C, C++, and C#:
        - Mentioning only C++ must NOT detect C.
        - Mentioning only C# must NOT detect C.
        - Mentioning C alone must detect C and not C++ or C#.
        - Mentioning C/C++ should detect both C and C++.
        """
        # Case 1: Only C++
        skills_cpp = extract_skills("Software engineer writing high-performance C++ code.")
        assert "C++" in skills_cpp
        assert "C" not in skills_cpp
        assert "C#" not in skills_cpp

        # Case 2: Only C#
        skills_csharp = extract_skills("Backend engineer building enterprise apps in C#.")
        assert "C#" in skills_csharp
        assert "C" not in skills_csharp
        assert "C++" not in skills_csharp

        # Case 3: Only C
        skills_c = extract_skills("Embedded firmware programming strictly in C language.")
        assert "C" in skills_c
        assert "C++" not in skills_c
        assert "C#" not in skills_c

        # Case 4: C/C++ together
        skills_both = extract_skills("Proficient in C/C++ and Linux kernel debugging.")
        assert "C" in skills_both
        assert "C++" in skills_both

    def test_nodejs_and_dotnet_and_nextjs(self):
        """
        Verify Node.js, Next.js, and .NET matching and avoidance of false positives:
        - "Node.js" should match Node.js (not plain "node" in cluster node).
        - "Next.js" should match Next.js (not "next month").
        - ".NET" should match .NET (including dotnet or asp.net).
        """
        text = "Built web apps using Node.js backend, Next.js frontend, and .NET Core microservices."
        skills = extract_skills(text)
        assert "Node.js" in skills
        assert "Next.js" in skills
        assert ".NET" in skills

        # False positive checks
        fp_text = "Scheduled the next cluster node deployment for next week."
        fp_skills = extract_skills(fp_text)
        assert "Next.js" not in fp_skills
        assert "Node.js" not in fp_skills

    def test_avoid_substring_false_positives(self):
        """
        Verify that sub-tokens do not trigger incorrect skill matches:
        - "JavaScript" must NOT trigger "Java".
        - "PostgreSQL" must NOT trigger "SQL".
        - "reaction" must NOT trigger "React".
        - "express my interest" must NOT trigger "Express".
        """
        text = "Experienced with JavaScript frontend and PostgreSQL database."
        skills = extract_skills(text)
        assert "JavaScript" in skills
        assert "Java" not in skills
        assert "PostgreSQL" in skills
        assert "SQL" not in skills

        # Express framework vs English verb "to express"
        verb_text = "I would like to express my gratitude and enthusiasm for this role."
        assert "Express" not in extract_skills(verb_text)

        tech_text = "Backend stack: Node.js, Express, and MongoDB."
        assert "Express" in extract_skills(tech_text)

    def test_empty_and_invalid_inputs(self):
        """Empty, whitespace, None, or non-string inputs should return an empty list."""
        assert extract_skills("") == []
        assert extract_skills("   ") == []
        assert extract_skills(None) == []
        assert extract_skills(12345) == []

    def test_analyze_skills_comparison(self):
        """Verify matched_skills and missing_skills logic."""
        resume = "Skills: Python, Docker, Git, Linux."
        jd = "Requirements: Python, Docker, Kubernetes, AWS, PostgreSQL."

        analysis = analyze_skills(resume, jd)
        assert analysis["resume_skills"] == ["Docker", "Git", "Linux", "Python"]
        assert analysis["required_skills"] == ["AWS", "Docker", "PostgreSQL", "Python"]
        assert analysis["matched_skills"] == ["Docker", "Python"]
        assert analysis["missing_skills"] == ["AWS", "PostgreSQL"]

    def test_custom_skill_patterns_override(self):
        """Verify that a custom dictionary can be supplied."""
        custom_dict = {"Rust": r"\brust\b", "Go": r"\bgo\b"}
        analyzer = SkillAnalyzer(skill_patterns=custom_dict)
        skills = analyzer.extract_skills("Experienced in Rust and Go.")
        assert skills == ["Go", "Rust"]
