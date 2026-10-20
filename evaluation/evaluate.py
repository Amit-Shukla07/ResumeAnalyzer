"""
Reproducible Evaluation Script for ResumeAnalyzer.

Executes a small, clearly labeled synthetic benchmark suite to verify
pipeline mechanics, scoring properties, and skill detection behavior.

IMPORTANT METHODOLOGICAL DISCLAIMER:
These synthetic test pairs are designed strictly to verify functional correctness,
boundary behaviors, and scoring logic under controlled test conditions.
They DO NOT establish real-world screening accuracy, nor do they constitute
a statistically valid benchmark of recruitment outcomes.
"""

import sys
from pathlib import Path

# Add project root to sys.path to allow execution directly or from subdirectories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.scoring import evaluate_match, DEFAULT_TEXT_WEIGHT, DEFAULT_SKILL_WEIGHT  # noqa: E402


SYNTHETIC_DATASET = [
    {
        "id": "scenario_1_strong_overlap",
        "description": "Strongly Overlapping Backend Engineer Pair",
        "resume": (
            "Senior Backend Engineer with 6 years of experience building scalable systems. "
            "Extensive expertise in Python, Docker, PostgreSQL, Git, and AWS cloud architecture. "
            "Designed and implemented high-throughput REST APIs and managed Linux server fleets. "
            "Hands-on work with C++ for low-latency background processing."
        ),
        "jd": (
            "Seeking a Senior Backend Engineer to lead our cloud microservices team. "
            "Requirements:\n"
            "- Strong proficiency in Python and REST API development.\n"
            "- Hands-on containerization experience using Docker.\n"
            "- Proven database expertise with PostgreSQL.\n"
            "- Proficiency with Git version control and Linux environments.\n"
            "- Familiarity with AWS and C++ is a plus."
        ),
        "expected_properties": "High text similarity (>20%), 100% skill match, high combined score.",
    },
    {
        "id": "scenario_2_partial_overlap",
        "description": "Partially Overlapping Full-Stack Developer Pair",
        "resume": (
            "Full-Stack Web Developer proficient in JavaScript, React, Node.js, and MongoDB. "
            "Built responsive client applications and integrated third-party REST APIs using Git."
        ),
        "jd": (
            "Looking for a Full-Stack Engineer with experience in TypeScript, React, Next.js, "
            "Docker, and PostgreSQL. Must be comfortable with Git and AWS deployments."
        ),
        "expected_properties": (
            "Moderate text similarity, partial skill match (React, Git matched; "
            "TypeScript, Next.js, Docker, PostgreSQL, AWS missing)."
        ),
    },
    {
        "id": "scenario_3_unrelated_pair",
        "description": "Completely Unrelated Pair (Culinary Chef vs Embedded Robotics)",
        "resume": (
            "Executive Head Chef with 10 years leading Michelin-starred kitchen operations. "
            "Expert in pastry design, classical French culinary techniques, menu planning, "
            "food safety sanitation standards, and kitchen inventory management."
        ),
        "jd": (
            "Embedded Robotics Engineer needed for autonomous drone firmware. "
            "Requirements: C, C++, Linux device drivers, RTOS, and Git version control."
        ),
        "expected_properties": "Low or near-zero text similarity (<10%), 0% skill match, low combined score.",
    },
    {
        "id": "scenario_4_no_recognized_skills_in_jd",
        "description": "Job Description With No Recognized Technical Skills",
        "resume": (
            "Data Scientist experienced in Python, Machine Learning, Deep Learning, "
            "Pandas, NumPy, and PyTorch."
        ),
        "jd": (
            "We are seeking an energetic, punctual, and highly collaborative team player "
            "with excellent presentation skills, active listening capabilities, and a positive attitude."
        ),
        "expected_properties": (
            "Skill match is Unavailable (None), Combined score is Unavailable (None), "
            "text similarity reflects general overlap."
        ),
    },
]


def run_evaluation() -> bool:
    """Run evaluation over all synthetic scenarios and print formatted report."""
    print("=" * 80)
    print("ResumeAnalyzer - Synthetic Evaluation Benchmark")
    print(
        f"Configured Scoring Weights: Text = {int(DEFAULT_TEXT_WEIGHT * 100)}%, "
        f"Skills = {int(DEFAULT_SKILL_WEIGHT * 100)}%"
    )
    print("=" * 80)

    results = []
    all_passed = True

    for item in SYNTHETIC_DATASET:
        res = evaluate_match(item["resume"], item["jd"])
        results.append((item, res))

        text_sim = res["text_similarity"]
        skill_match = res["skill_match"]
        combined = res["combined_score"]

        skill_str = f"{skill_match:.1f}%" if skill_match is not None else "Unavailable (None)"
        comb_str = f"{combined:.1f}%" if combined is not None else "Unavailable (None)"

        print(f"\nScenario [{item['id']}]: {item['description']}")
        print(f"  • Text Similarity: {text_sim:.2f}%")
        print(f"  • Skill Match:     {skill_str}")
        print(f"  • Combined Score:  {comb_str}")
        print(f"  • Resume Skills:   {res['resume_skills']}")
        print(f"  • Required Skills: {res['required_skills']}")
        print(f"  • Matched Skills:  {res['matched_skills']}")
        print(f"  • Missing Skills:  {res['missing_skills']}")

    # Relational Consistency Checks
    res_strong = results[0][1]
    res_partial = results[1][1]
    res_unrelated = results[2][1]
    res_no_skills = results[3][1]

    print("\n" + "=" * 80)
    print("Relational Property Verification")
    print("-" * 80)

    # 1. Strong vs Partial vs Unrelated
    check_similarity_order = (
        res_strong["text_similarity"] > res_unrelated["text_similarity"]
        and res_partial["text_similarity"] > res_unrelated["text_similarity"]
    )
    print(f"  [{'PASS' if check_similarity_order else 'FAIL'}] Similarity ordering: Strong & Partial > Unrelated")

    # 2. Skill match: strong has 100%, partial has partial, unrelated has 0%
    check_skill_order = (
        res_strong["skill_match"] == 100.0
        and 0.0 < res_partial["skill_match"] < 100.0
        and res_unrelated["skill_match"] == 0.0
    )
    status_str = 'PASS' if check_skill_order else 'FAIL'
    print(f"  [{status_str}] Skill match gradation: 100% (Strong) > Partial > 0% (Unrelated)")

    # 3. No recognized skills in JD -> skill_match and combined_score must be None
    check_unavailable = (
        res_no_skills["skill_match"] is None
        and res_no_skills["combined_score"] is None
    )
    print(f"  [{'PASS' if check_unavailable else 'FAIL'}] Missing JD skills handled safely as None (not zero)")

    all_passed = check_similarity_order and check_skill_order and check_unavailable

    print("=" * 80)
    print(f"Overall Evaluation Status: {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=" * 80)
    print("NOTE: This evaluation uses synthetic, illustrative test pairs to verify system")
    print("functionality and scoring mechanics. It tests basic expected pipeline behavior")
    print("but does not establish real-world accuracy or represent a statistically valid")
    print("evaluation on human-curated recruitment datasets.")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = run_evaluation()
    sys.exit(0 if success else 1)
