"""
UI Components and Design System for ResumeAnalyzer.

Provides reusable HTML/CSS rendering helpers for an enterprise-grade dark SaaS interface,
including SVG progress gauges, skill badges, evidence extractors, and responsive cards.
"""

from typing import Optional
import re
import html
import textwrap
import streamlit as st


# -----------------------------------------------------------------------------
# Design Tokens & Global CSS
# -----------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap'); /* noqa: E501 */

:root {
    --bg-canvas: #0A0D14;
    --bg-surface-1: #111625;
    --bg-surface-2: #161F33;
    --bg-surface-3: #1E293B;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-medium: rgba(255, 255, 255, 0.14);
    --border-accent: rgba(99, 102, 241, 0.35);
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --accent-indigo: #6366F1;
    --accent-violet: #818CF8;
    --accent-cyan: #22D3EE;
    --accent-emerald: #34D399;
    --accent-rose: #FB7185;
    --accent-amber: #FBBF24;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;
}

html, body, [class*="css"], .stApp {
    font-family: var(--font-sans);
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
}

header[data-testid="stHeader"] {
    background-color: rgba(10, 13, 20, 0.8) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-subtle);
}

.stMainBlockContainer {
    max-width: 1240px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
}

.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0 1.25rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-subtle);
}
.brand-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.brand-mark {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: linear-gradient(135deg, #6366F1 0%, #22D3EE 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-weight: 800;
    font-size: 1.05rem;
    box-shadow: 0 0 16px -2px rgba(99, 102, 241, 0.4);
}
.brand-title {
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
}
.brand-badge {
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent-cyan);
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.25);
    padding: 0.18rem 0.5rem;
    border-radius: 9999px;
}
.nav-privacy {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.775rem;
    color: var(--text-muted);
    background: var(--bg-surface-1);
    border: 1px solid var(--border-subtle);
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
}
.privacy-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--accent-emerald);
    box-shadow: 0 0 8px var(--accent-emerald);
}

.hero-card {
    position: relative;
    background: radial-gradient(120% 120% at 50% -10%,
        rgba(99, 102, 241, 0.12) 0%, rgba(17, 22, 37, 0.6) 60%, rgba(10, 13, 20, 0) 100%),
        var(--bg-surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 2rem 2.25rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.5);
    overflow: hidden;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--accent-violet);
    background: rgba(129, 140, 248, 0.1);
    border: 1px solid rgba(129, 140, 248, 0.25);
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    margin-bottom: 0.85rem;
}
.hero-title {
    font-size: 1.95rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.035em;
    margin: 0 0 0.55rem 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.55;
    max-width: 780px;
    margin: 0;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}
.panel-num-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.panel-number {
    font-size: 0.75rem;
    font-weight: 700;
    font-family: var(--font-mono);
    color: var(--accent-cyan);
    background: rgba(34, 211, 238, 0.1);
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    border: 1px solid rgba(34, 211, 238, 0.2);
}
.panel-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}
.panel-caption {
    font-size: 0.825rem;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
    line-height: 1.45;
}

div[data-testid="stFileUploader"] {
    background-color: transparent !important;
}
div[data-testid="stFileUploader"] > section {
    background-color: var(--bg-surface-1) !important;
    border: 1px dashed var(--border-medium) !important;
    border-radius: 12px !important;
    padding: 1.5rem 1rem !important;
    transition: all 0.2s ease-in-out !important;
}
div[data-testid="stFileUploader"] > section:hover {
    border-color: var(--accent-indigo) !important;
    background-color: rgba(99, 102, 241, 0.04) !important;
    box-shadow: 0 0 16px -2px rgba(99, 102, 241, 0.15);
}
div[data-testid="stFileUploader"] small {
    color: var(--text-muted) !important;
}

div[data-testid="stTextArea"] textarea {
    background-color: var(--bg-surface-1) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 0.9rem !important;
    font-family: var(--font-sans) !important;
    font-size: 0.875rem !important;
    line-height: 1.5 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    background-color: var(--bg-surface-2) !important;
}

div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.925rem !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.35) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #7073F5 0%, #5B52EE 100%) !important;
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-1px);
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: var(--bg-surface-1) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-secondary) !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background-color: var(--bg-surface-2) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-medium) !important;
}

.score-hero-card {
    background: radial-gradient(100% 100% at 50% 0%,
        rgba(99, 102, 241, 0.15) 0%, rgba(17, 22, 37, 0.8) 60%, var(--bg-surface-1) 100%);
    border: 1px solid var(--border-accent);
    border-radius: 14px;
    padding: 1.85rem;
    display: flex;
    align-items: center;
    gap: 2.25rem;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6), 0 0 20px -5px rgba(99, 102, 241, 0.15);
    margin-bottom: 1.5rem;
}
.score-hero-left {
    flex-shrink: 0;
}
.score-hero-right {
    flex-grow: 1;
}
.score-hero-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent-violet);
    margin-bottom: 0.35rem;
}
.score-hero-headline {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
    line-height: 1.25;
}
.score-hero-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 0.85rem;
}
.score-disclaimer-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-tile {
    background-color: var(--bg-surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.25rem;
    position: relative;
    transition: all 0.2s ease;
}
.metric-tile:hover {
    border-color: var(--border-medium);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.4);
}
.metric-tile-label {
    font-size: 0.725rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 0.45rem;
}
.metric-tile-val {
    font-size: 1.85rem;
    font-weight: 700;
    font-family: var(--font-sans);
    color: var(--text-primary);
    line-height: 1.1;
    margin-bottom: 0.35rem;
}
.metric-tile-val.na {
    font-size: 1.2rem;
    color: var(--text-muted);
}
.metric-tile-sub {
    font-size: 0.775rem;
    color: var(--text-secondary);
    line-height: 1.4;
}

.skill-category-card {
    background-color: var(--bg-surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.25rem;
    height: 100%;
}
.skill-category-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}
.skill-category-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.45rem;
}
.skill-count-badge {
    font-size: 0.75rem;
    font-family: var(--font-mono);
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
}
.skill-count-matched {
    background: rgba(52, 211, 153, 0.15);
    color: var(--accent-emerald);
    border: 1px solid rgba(52, 211, 153, 0.3);
}
.skill-count-missing {
    background: rgba(251, 113, 133, 0.15);
    color: var(--accent-rose);
    border: 1px solid rgba(251, 113, 133, 0.3);
}
.skill-count-additional {
    background: rgba(167, 139, 250, 0.15);
    color: var(--accent-violet);
    border: 1px solid rgba(167, 139, 250, 0.3);
}
.skill-category-caption {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
    line-height: 1.4;
}

.skill-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
}
.skill-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.65rem;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    line-height: 1.3;
}
.skill-pill-matched {
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.25);
    color: #6EE7B7;
}
.skill-pill-missing {
    background: rgba(251, 113, 133, 0.1);
    border: 1px solid rgba(251, 113, 133, 0.25);
    color: #FDA4AF;
}
.skill-pill-additional {
    background: rgba(167, 139, 250, 0.1);
    border: 1px solid rgba(167, 139, 250, 0.25);
    color: #C4B5FD;
}

.evidence-card {
    background: var(--bg-surface-2);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--accent-cyan);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.825rem;
    color: var(--text-secondary);
    line-height: 1.45;
}
.evidence-skill-tag {
    font-size: 0.7rem;
    font-family: var(--font-mono);
    color: var(--accent-cyan);
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.rec-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 0.75rem;
}
.rec-card {
    background: var(--bg-surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: all 0.15s ease;
}
.rec-card:hover {
    border-color: var(--border-medium);
    background: var(--bg-surface-2);
}
.rec-badge {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 0.15rem;
}
.rec-badge-critical {
    background: rgba(251, 113, 133, 0.15);
    color: var(--accent-rose);
    border: 1px solid rgba(251, 113, 133, 0.3);
}
.rec-badge-align {
    background: rgba(34, 211, 238, 0.15);
    color: var(--accent-cyan);
    border: 1px solid rgba(34, 211, 238, 0.3);
}
.rec-badge-highlight {
    background: rgba(167, 139, 250, 0.15);
    color: var(--accent-violet);
    border: 1px solid rgba(167, 139, 250, 0.3);
}
.rec-badge-advisory {
    background: rgba(251, 191, 36, 0.15);
    color: var(--accent-amber);
    border: 1px solid rgba(251, 191, 36, 0.3);
}
.rec-badge-integrity {
    background: rgba(52, 211, 153, 0.15);
    color: var(--accent-emerald);
    border: 1px solid rgba(52, 211, 153, 0.3);
}
.rec-content {
    flex-grow: 1;
}
.rec-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}
.rec-body {
    font-size: 0.835rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

div[data-testid="stExpander"] {
    background-color: var(--bg-surface-1) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    overflow: hidden;
}
div[data-testid="stExpander"] > details > summary {
    background-color: var(--bg-surface-1) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    padding: 0.85rem 1.15rem !important;
}
div[data-testid="stExpander"] > details > summary:hover {
    color: var(--accent-cyan) !important;
}

@media (max-width: 900px) {
    .score-hero-card {
        flex-direction: column;
        align-items: flex-start;
        gap: 1.25rem;
    }
    .metric-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
@media (max-width: 600px) {
    .metric-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""


# -----------------------------------------------------------------------------
# Component Renderers
# -----------------------------------------------------------------------------
def render_navbar() -> None:
    """Render top application brand bar with wordmark and privacy badge."""
    nav_html = textwrap.dedent("""
    <div class="nav-bar">
        <div class="brand-group">
            <div class="brand-mark">R</div>
            <div>
                <h1 class="brand-title">ResumeAnalyzer</h1>
            </div>
            <span class="brand-badge">CAREER INTELLIGENCE</span>
        </div>
        <div class="nav-privacy">
            <span class="privacy-dot"></span>
            <span>In-Memory RAM Only · Zero Cloud Storage · Local CPU</span>
        </div>
    </div>
    """).strip()
    st.markdown(nav_html, unsafe_allow_html=True)


def render_hero() -> None:
    """Render the hero section with headline and supporting text."""
    hero_html = textwrap.dedent("""
    <div class="hero-card">
        <div class="hero-pill">
            <span>✦ Natural Language Alignment Platform</span>
        </div>
        <h2 class="hero-title">Make your next move with confidence.</h2>
        <p class="hero-subtitle">
            Understand how your experience aligns with a job, identify important skill gaps,
            and discover where your resume can communicate your strengths more effectively.
        </p>
    </div>
    """).strip()
    st.markdown(hero_html, unsafe_allow_html=True)


def render_svg_gauge(score: Optional[float], size: int = 130) -> str:
    """
    Generate an SVG circular progress meter representing alignment percentage.

    Args:
        score: Score between 0.0 and 100.0, or None if unavailable.
        size: Pixel dimension for SVG viewbox.
    """
    radius = 50
    circumference = 2 * 3.14159 * radius
    stroke_width = 8

    if score is not None:
        pct = max(0.0, min(100.0, score))
        dash_offset = circumference * (1.0 - (pct / 100.0))
        text_val = f"{score:.1f}%"
        sub_text = "ALIGNMENT"

        if score >= 70.0:
            stroke_color = "#34D399"
            bg_stroke = "rgba(52, 211, 153, 0.15)"
        elif score >= 40.0:
            stroke_color = "#818CF8"
            bg_stroke = "rgba(129, 140, 248, 0.15)"
        else:
            stroke_color = "#22D3EE"
            bg_stroke = "rgba(34, 211, 238, 0.15)"
    else:
        dash_offset = circumference
        text_val = "N/A"
        sub_text = "UNAVAILABLE"
        stroke_color = "#64748B"
        bg_stroke = "rgba(100, 116, 139, 0.2)"

    svg = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 120 120" style="transform: rotate(-90deg);">'
        f'<circle cx="60" cy="60" r="{radius}" fill="none" stroke="{bg_stroke}" stroke-width="{stroke_width}" />'
        f'<circle cx="60" cy="60" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" '
        f'stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}" '
        f'stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;" />'
        f'</svg>'
        f'<div style="position: absolute; top: 0; left: 0; width: {size}px; height: {size}px; '
        f'display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">'
        f'<span style="font-size: 1.55rem; font-weight: 800; font-family: var(--font-sans); '
        f'color: #F8FAFC; line-height: 1;">{text_val}</span>'
        f'<span style="font-size: 0.625rem; font-weight: 700; letter-spacing: 0.08em; '
        f'color: {stroke_color}; margin-top: 4px;">{sub_text}</span>'
        f'</div>'
    )
    return f'<div style="position: relative; width: {size}px; height: {size}px;">{svg}</div>'


def render_combined_score_hero(res: dict, text_weight_pct: int, skill_weight_pct: int) -> None:
    """Render the primary hero score card with circular gauge and clear heuristic explanation."""
    combined_score = res.get("combined_score")
    gauge_html = render_svg_gauge(combined_score, size=130)

    if combined_score is not None:
        if combined_score >= 70.0:
            headline = "Strong Overall Alignment"
            desc = (
                f"Your profile strongly satisfies both vocabulary overlap and key technical requirements "
                f"({text_weight_pct}% text similarity / {skill_weight_pct}% skill match weighting)."
            )
        elif combined_score >= 40.0:
            headline = "Moderate Overall Alignment"
            desc = (
                "You demonstrate notable technical alignment with specific requirements, with opportunities "
                "to bridge vocabulary phrasing and missing keywords."
            )
        else:
            headline = "Limited Direct Overlap"
            desc = (
                "The resume wording and listed technologies have minimal direct overlap with this specific job post. "
                "Review missing skills to determine if your background aligns."
            )
    else:
        headline = "Alignment Metric Unavailable"
        desc = (
            "The job description contains no technical skills recognized by our dictionary. "
            "To avoid false penalties, the combined score is left unset."
        )

    disclaimer_text = (
        f"Heuristic indicator based on {text_weight_pct}% text similarity & {skill_weight_pct}% skill match. "
        "Not an algorithm of hiring probability."
    )

    card_html = textwrap.dedent(f"""
    <div class="score-hero-card">
        <div class="score-hero-left">
            {gauge_html}
        </div>
        <div class="score-hero-right">
            <div class="score-hero-label">Overall Composite Match</div>
            <h3 class="score-hero-headline">{headline}</h3>
            <p class="score-hero-desc">{desc}</p>
            <div class="score-disclaimer-pill">
                <span>ℹ️</span>
                <span>{disclaimer_text}</span>
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(card_html, unsafe_allow_html=True)


def render_metric_grid(res: dict) -> None:
    """Render 4 responsive supporting metric tiles."""
    text_sim = res.get("text_similarity", 0.0)
    skill_match = res.get("skill_match")
    matched_skills = res.get("matched_skills", [])
    missing_skills = res.get("missing_skills", [])
    required_skills = res.get("required_skills", [])

    skill_str = f"{skill_match:.1f}%" if skill_match is not None else "Unavailable"
    skill_class = "" if skill_match is not None else "na"
    skill_sub = (
        f"{len(matched_skills)} of {len(required_skills)} required skills detected"
        if skill_match is not None
        else "No recognized skills in JD"
    )

    grid_html = textwrap.dedent(f"""
    <div class="metric-grid">
        <div class="metric-tile">
            <div class="metric-tile-label">Text Similarity</div>
            <div class="metric-tile-val">{text_sim:.1f}%</div>
            <div class="metric-tile-sub">TF-IDF unigram & bigram cosine overlap</div>
        </div>
        <div class="metric-tile">
            <div class="metric-tile-label">Skill Coverage</div>
            <div class="metric-tile-val {skill_class}">{skill_str}</div>
            <div class="metric-tile-sub">{skill_sub}</div>
        </div>
        <div class="metric-tile">
            <div class="metric-tile-label">Matched Skills</div>
            <div class="metric-tile-val">{len(matched_skills)}</div>
            <div class="metric-tile-sub">Present in both resume and JD</div>
        </div>
        <div class="metric-tile">
            <div class="metric-tile-label">Potential Gaps</div>
            <div class="metric-tile-val">{len(missing_skills)}</div>
            <div class="metric-tile-sub">Required in JD, absent in resume</div>
        </div>
    </div>
    """).strip()
    st.markdown(grid_html, unsafe_allow_html=True)


def render_skill_pills(skills: list[str], pill_class: str, empty_message: str) -> None:
    """Render stylized skill pills inside a flexible grid."""
    if not skills:
        st.markdown(
            f"<div style='color: var(--text-muted); font-size: 0.825rem; font-style: italic; "
            f"padding: 0.4rem 0;'>{empty_message}</div>",
            unsafe_allow_html=True,
        )
        return

    pills_html = "".join([f'<span class="skill-pill {pill_class}">{html.escape(s)}</span>' for s in skills])
    st.markdown(f'<div class="skill-grid">{pills_html}</div>', unsafe_allow_html=True)


def extract_resume_evidence(resume_text: str, matched_skills: list[str], max_snippets: int = 4) -> list[dict]:
    """
    Extract authentic resume evidence snippets showing where matched skills appear in context.

    Args:
        resume_text: Extracted text from uploaded PDF resume.
        matched_skills: List of skills matched between resume and JD.
        max_snippets: Maximum number of evidence snippets to present.

    Returns:
        List of dicts with 'skill' and 'snippet' keys.
    """
    if not resume_text or not matched_skills:
        return []

    raw_lines = re.split(r"[\n\r•–—*]+|\.\s+", resume_text)
    clean_lines = [line.strip() for line in raw_lines if len(line.strip()) >= 20]

    evidence = []
    seen_lines = set()

    for skill in matched_skills:
        pattern = re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
        for line in clean_lines:
            if pattern.search(line) and line not in seen_lines:
                seen_lines.add(line)
                display_line = line if len(line) <= 180 else line[:177] + "..."
                evidence.append({"skill": skill, "snippet": display_line})
                break
        if len(evidence) >= max_snippets:
            break

    return evidence


def render_evidence_section(evidence: list[dict]) -> None:
    """Render verified resume contextual evidence cards."""
    if not evidence:
        return

    cards_html = "".join([
        f'<div class="evidence-card">'
        f'<div class="evidence-skill-tag">Matched: {html.escape(item["skill"])}</div>'
        f'<div>"{html.escape(item["snippet"])}"</div>'
        f'</div>'
        for item in evidence
    ])

    section_html = (
        '<div style="margin-top: 1.25rem; margin-bottom: 0.5rem;">'
        '<div style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">'
        '📋 Requirement Evidence in Resume</div>'
        '<div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">'
        'Verified context snippets extracted directly from your uploaded document:</div>'
        f'{cards_html}</div>'
    )
    st.markdown(section_html, unsafe_allow_html=True)


def render_recommendation_cards(
    missing_skills: list[str],
    text_similarity: float,
    additional_skills: list[str],
    required_skills: list[str],
) -> None:
    """Render actionable recommendations with priority badges."""
    recs = []

    if missing_skills:
        skills_str = ", ".join(missing_skills[:5])
        suffix = "..." if len(missing_skills) > 5 else ""
        recs.append({
            "type": "critical",
            "badge": "High Priority",
            "title": "Address Identified Skill Gaps",
            "body": (
                f"The job requires proficiency in <strong>{skills_str}{suffix}</strong>. "
                "If you have hands-on experience with these technologies, ensure they are explicitly "
                "named inside your project descriptions or professional experience bullets."
            ),
        })

    if text_similarity < 25.0:
        recs.append({
            "type": "align",
            "badge": "Terminology",
            "title": "Align Industry & Domain Vocabulary",
            "body": (
                f"Your text similarity is currently {text_similarity:.1f}%. "
                "Incorporate exact terminology, architectural patterns, and responsibility phrasing "
                "from the job description to improve automated screening concordance."
            ),
        })

    if additional_skills:
        add_str = ", ".join(additional_skills[:4])
        suffix = "..." if len(additional_skills) > 4 else ""
        recs.append({
            "type": "highlight",
            "badge": "Transferable",
            "title": "Spotlight Complementary Competencies",
            "body": (
                f"Your resume includes recognized skills ({add_str}{suffix}) not explicitly listed in the JD. "
                "Frame these as adjacent advantages that enhance your core technical depth."
            ),
        })

    if not required_skills:
        recs.append({
            "type": "advisory",
            "badge": "Clarification",
            "title": "Refine Job Description Input",
            "body": (
                "The target job description did not match any recognized technical terms from our dictionary. "
                "Ensure you include the full 'Requirements' or 'Qualifications' section of the job posting."
            ),
        })

    recs.append({
        "type": "integrity",
        "badge": "Integrity",
        "title": "Maintain Verifiable Accuracy",
        "body": (
            "Resume tailoring should highlight authentic capabilities. "
            "Never add technologies or responsibilities you cannot substantiate with technical confidence "
            "in an interview."
        ),
    })

    cards_html = "".join([
        f'<div class="rec-card">'
        f'<span class="rec-badge rec-badge-{rec["type"]}">{rec["badge"]}</span>'
        f'<div class="rec-content">'
        f'<div class="rec-title">{rec["title"]}</div>'
        f'<div class="rec-body">{rec["body"]}</div>'
        f'</div>'
        f'</div>'
        for rec in recs
    ])
    st.markdown(f'<div class="rec-list">{cards_html}</div>', unsafe_allow_html=True)
