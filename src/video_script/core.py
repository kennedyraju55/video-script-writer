#!/usr/bin/env python3
"""Core logic for Video Script Writer."""

import sys
import os
import re
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


def load_config() -> dict:
    """Load configuration from config.yaml, falling back to defaults."""
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("config.yaml not found – using defaults")
        return {}


def _cfg() -> dict:
    """Return cached config."""
    if not hasattr(_cfg, "_cache"):
        _cfg._cache = load_config()
    return _cfg._cache


def _video_cfg() -> dict:
    return _cfg().get("video", {})


def _llm_cfg() -> dict:
    return _cfg().get("llm", {})


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STYLES: list[str] = _video_cfg().get(
    "styles",
    ["educational", "entertainment", "tutorial", "review", "vlog", "documentary"],
)

DEFAULT_STYLE: str = _video_cfg().get("default_style", "educational")
DEFAULT_DURATION: int = _video_cfg().get("default_duration", 10)
MAX_DURATION: int = _video_cfg().get("max_duration", 60)
WORDS_PER_MINUTE: int = _video_cfg().get("words_per_minute", 150)
LLM_TEMPERATURE: float = _llm_cfg().get("temperature", 0.7)
LLM_MAX_TOKENS: int = _llm_cfg().get("max_tokens", 4096)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ScriptSection:
    """A single section of a video script."""

    title: str
    timestamp_start: str = ""
    timestamp_end: str = ""
    script_text: str = ""
    broll_suggestions: list[str] = field(default_factory=list)
    onscreen_text: str = ""

    @property
    def timestamp(self) -> str:
        if self.timestamp_start and self.timestamp_end:
            return f"[{self.timestamp_start}-{self.timestamp_end}]"
        if self.timestamp_start:
            return f"[{self.timestamp_start}]"
        return ""


@dataclass
class VideoScript:
    """Complete video script with metadata."""

    topic: str
    style: str
    duration_minutes: int
    sections: list[ScriptSection] = field(default_factory=list)
    hook: str = ""
    thumbnail_ideas: list[str] = field(default_factory=list)
    raw_text: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def word_count(self) -> int:
        return len(self.full_text.split())

    @property
    def estimated_duration(self) -> float:
        return estimate_duration(self.full_text)

    @property
    def full_text(self) -> str:
        if self.sections:
            return "\n\n".join(s.script_text for s in self.sections if s.script_text)
        return self.raw_text


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a professional YouTube scriptwriter and content strategist. "
    "You create engaging, well-structured video scripts that keep viewers watching. "
    "You understand pacing, hooks, retention strategies, and platform best practices."
)


def build_prompt(topic: str, duration: int, style: str, audience: Optional[str]) -> str:
    """Build the video script generation prompt."""
    audience_str = f"Target Audience: {audience}\n" if audience else ""
    return (
        f"Create a complete YouTube video script about: {topic}\n\n"
        f"Video Duration: {duration} minutes\n"
        f"Style: {style}\n"
        f"{audience_str}\n"
        f"Structure the script with:\n"
        f"1. **HOOK** (first 15 seconds) - grab viewer attention immediately\n"
        f"2. **INTRO** (30-60 seconds) - introduce the topic and what viewers will learn\n"
        f"3. **MAIN CONTENT** - divided into clear sections with timestamps\n"
        f"4. **OUTRO** (30 seconds) - summary, CTA (subscribe, like, comment)\n\n"
        f"For each section include:\n"
        f"- **[TIMESTAMP]** e.g., [0:00-0:30]\n"
        f"- **Script** (exact words to say)\n"
        f"- **[B-ROLL]** suggestions (visuals to show while speaking)\n"
        f"- **[ON-SCREEN TEXT]** any text overlays or graphics\n\n"
        f"Make it engaging, well-paced for a {duration}-minute video.\n"
        f"Include natural transitions between sections.\n"
    )


# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------


def generate_script(topic: str, duration: int, style: str, audience: Optional[str]) -> str:
    """Generate a full video script using the LLM."""
    logger.info("Generating script: topic=%s duration=%d style=%s", topic, duration, style)
    user_prompt = build_prompt(topic, duration, style, audience)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(
        messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )


def generate_scene_breakdown(topic: str, duration: int, style: str) -> list[ScriptSection]:
    """Return a list of ScriptSection objects with a scene-by-scene breakdown."""
    logger.info("Generating scene breakdown for '%s'", topic)
    prompt = (
        f"Create a detailed scene-by-scene breakdown for a {duration}-minute "
        f"{style} YouTube video about: {topic}\n\n"
        f"For each scene provide exactly this format:\n"
        f"## SCENE: <scene title>\n"
        f"TIMESTAMP: <start>-<end>\n"
        f"SCRIPT: <what to say>\n"
        f"B-ROLL: <visual suggestion 1>\n"
        f"B-ROLL: <visual suggestion 2>\n"
        f"ON-SCREEN TEXT: <text overlay>\n\n"
        f"Include 5-8 scenes covering hook, intro, main content sections, and outro."
    )
    messages = [{"role": "user", "content": prompt}]
    raw = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=LLM_TEMPERATURE, max_tokens=LLM_MAX_TOKENS)
    return parse_script_sections(raw)


def suggest_broll(topic: str, section_text: str, num_suggestions: int = 3) -> list[str]:
    """Generate B-roll ideas for a given script section."""
    logger.info("Generating %d B-roll suggestions for '%s'", num_suggestions, topic)
    prompt = (
        f"Suggest exactly {num_suggestions} B-roll visual ideas for this section "
        f"of a YouTube video about '{topic}':\n\n"
        f"Section text: {section_text}\n\n"
        f"Return each suggestion on its own line, numbered 1-{num_suggestions}. "
        f"Include specific visual descriptions with camera angles and movement."
    )
    messages = [{"role": "user", "content": prompt}]
    raw = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=LLM_TEMPERATURE, max_tokens=1024)
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    suggestions = []
    for line in lines:
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if cleaned:
            suggestions.append(cleaned)
    return suggestions[:num_suggestions] if suggestions else [raw.strip()]


def generate_hook(topic: str, style: str, num_hooks: int = 3) -> list[str]:
    """Generate multiple hook options for a video opening."""
    logger.info("Generating %d hook options for '%s'", num_hooks, topic)
    prompt = (
        f"Write exactly {num_hooks} different hook options (first 15 seconds) "
        f"for a {style} YouTube video about: {topic}\n\n"
        f"Each hook should grab attention immediately.\n"
        f"Number them 1-{num_hooks}, each on its own paragraph.\n"
        f"Include the exact words the creator should say."
    )
    messages = [{"role": "user", "content": prompt}]
    raw = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.9, max_tokens=1024)
    hooks = _split_numbered_items(raw, num_hooks)
    return hooks


def generate_thumbnail_ideas(topic: str, style: str, num_ideas: int = 3) -> list[str]:
    """Generate thumbnail concepts with text overlay and visual descriptions."""
    logger.info("Generating %d thumbnail ideas for '%s'", num_ideas, topic)
    prompt = (
        f"Create exactly {num_ideas} YouTube thumbnail ideas for a {style} video about: {topic}\n\n"
        f"For each idea include:\n"
        f"- Visual description (main image, colors, composition)\n"
        f"- Text overlay (big bold text for the thumbnail)\n"
        f"- Emotion/expression if a person is shown\n\n"
        f"Number them 1-{num_ideas}."
    )
    messages = [{"role": "user", "content": prompt}]
    raw = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.8, max_tokens=1024)
    return _split_numbered_items(raw, num_ideas)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def estimate_duration(script_text: str, wpm: int = WORDS_PER_MINUTE) -> float:
    """Estimate video duration in minutes from script word count."""
    if not script_text or not script_text.strip():
        return 0.0
    word_count = len(script_text.split())
    return round(word_count / wpm, 1)


def export_teleprompter(script: VideoScript) -> str:
    """Export clean script text without B-roll notes for teleprompter reading."""
    if script.sections:
        parts: list[str] = []
        for section in script.sections:
            if section.script_text:
                parts.append(section.script_text.strip())
        return "\n\n---\n\n".join(parts)

    # Fallback: strip B-roll / on-screen markers from raw text
    text = script.raw_text
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("[B-ROLL]") or stripped.upper().startswith("B-ROLL:"):
            continue
        if stripped.upper().startswith("[ON-SCREEN TEXT]") or stripped.upper().startswith("ON-SCREEN TEXT:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def parse_script_sections(raw_text: str) -> list[ScriptSection]:
    """Parse LLM output into ScriptSection objects.

    Handles formats like:
        ## SCENE: Title
        TIMESTAMP: 0:00-0:30
        SCRIPT: words to say
        B-ROLL: visual suggestion
        ON-SCREEN TEXT: overlay text
    Also handles ## HOOK, ## INTRO, ## SECTION, ## OUTRO headers.
    """
    sections: list[ScriptSection] = []
    # Split on markdown headers (## ...)
    header_pattern = re.compile(r"^##\s+(.+)", re.MULTILINE)
    parts = header_pattern.split(raw_text)

    # parts[0] is text before first header; then alternating title, body
    i = 1
    while i < len(parts) - 1:
        title_raw = parts[i].strip()
        body = parts[i + 1].strip()
        i += 2

        # Clean title: remove "SCENE:" prefix if present
        title = re.sub(r"^SCENE:\s*", "", title_raw, flags=re.IGNORECASE).strip()

        # Extract timestamp
        ts_match = re.search(r"TIMESTAMP:\s*(\d[\d:]*)\s*-\s*(\d[\d:]*)", body, re.IGNORECASE)
        ts_start = ts_match.group(1) if ts_match else ""
        ts_end = ts_match.group(2) if ts_match else ""

        # Also check for [0:00-0:30] style timestamps in the title or body
        if not ts_start:
            bracket_ts = re.search(r"\[(\d[\d:]*)\s*-\s*(\d[\d:]*)\]", title_raw + " " + body)
            if bracket_ts:
                ts_start = bracket_ts.group(1)
                ts_end = bracket_ts.group(2)

        # Extract script text
        script_match = re.search(r"SCRIPT:\s*(.+?)(?=\n(?:B-ROLL|ON-SCREEN|TIMESTAMP|$))", body, re.IGNORECASE | re.DOTALL)
        script_text = script_match.group(1).strip() if script_match else ""
        if not script_text:
            # Fallback: use the body minus known tags
            cleaned = re.sub(r"(?:TIMESTAMP|B-ROLL|ON-SCREEN TEXT):.*", "", body, flags=re.IGNORECASE).strip()
            script_text = cleaned

        # Extract B-roll suggestions
        broll_items = re.findall(r"B-ROLL:\s*(.+)", body, re.IGNORECASE)

        # Extract on-screen text
        onscreen_match = re.search(r"ON-SCREEN TEXT:\s*(.+)", body, re.IGNORECASE)
        onscreen = onscreen_match.group(1).strip() if onscreen_match else ""

        section = ScriptSection(
            title=title,
            timestamp_start=ts_start,
            timestamp_end=ts_end,
            script_text=script_text,
            broll_suggestions=broll_items,
            onscreen_text=onscreen,
        )
        sections.append(section)

    if not sections and raw_text.strip():
        sections.append(ScriptSection(title="Full Script", script_text=raw_text.strip()))

    return sections


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _split_numbered_items(text: str, expected: int) -> list[str]:
    """Split numbered LLM output (1. ..., 2. ..., etc.) into a list of strings."""
    # Try splitting on number prefixes
    items = re.split(r"\n\s*\d+[\.\)]\s+", "\n" + text.strip())
    items = [item.strip() for item in items if item.strip()]

    if len(items) >= expected:
        return items[:expected]

    # Fallback: split on double newlines
    items = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    if len(items) >= expected:
        return items[:expected]

    # Last resort: return as single item
    return [text.strip()] if text.strip() else []


def setup_logging() -> None:
    """Configure logging based on config."""
    level_name = _cfg().get("logging", {}).get("level", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
