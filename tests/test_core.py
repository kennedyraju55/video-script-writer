"""Tests for video_script.core module."""

import pytest
from unittest.mock import patch

from video_script.core import (
    STYLES,
    ScriptSection,
    VideoScript,
    build_prompt,
    estimate_duration,
    export_teleprompter,
    generate_hook,
    generate_scene_breakdown,
    generate_script,
    generate_thumbnail_ideas,
    parse_script_sections,
    suggest_broll,
)


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    def test_prompt_contains_topic(self):
        prompt = build_prompt("Python Tips", 10, "educational", None)
        assert "Python Tips" in prompt

    def test_prompt_contains_duration(self):
        prompt = build_prompt("Python Tips", 15, "educational", None)
        assert "15 minutes" in prompt

    def test_prompt_contains_style(self):
        prompt = build_prompt("Review", 10, "review", None)
        assert "review" in prompt

    def test_prompt_includes_broll(self):
        prompt = build_prompt("Topic", 10, "tutorial", None)
        assert "B-ROLL" in prompt

    def test_prompt_includes_timestamp(self):
        prompt = build_prompt("Topic", 10, "tutorial", None)
        assert "TIMESTAMP" in prompt

    def test_prompt_includes_audience(self):
        prompt = build_prompt("Topic", 10, "educational", "beginners")
        assert "beginners" in prompt

    def test_prompt_without_audience(self):
        prompt = build_prompt("Topic", 10, "educational", None)
        assert "Target Audience" not in prompt


# ---------------------------------------------------------------------------
# estimate_duration
# ---------------------------------------------------------------------------


class TestEstimateDuration:
    def test_empty_string(self):
        assert estimate_duration("") == 0.0

    def test_none_like_empty(self):
        assert estimate_duration("   ") == 0.0

    def test_150_words_is_one_minute(self):
        text = " ".join(["word"] * 150)
        assert estimate_duration(text) == 1.0

    def test_300_words_is_two_minutes(self):
        text = " ".join(["word"] * 300)
        assert estimate_duration(text) == 2.0

    def test_custom_wpm(self):
        text = " ".join(["word"] * 200)
        assert estimate_duration(text, wpm=200) == 1.0

    def test_fractional_result(self):
        text = " ".join(["word"] * 75)
        assert estimate_duration(text) == 0.5


# ---------------------------------------------------------------------------
# parse_script_sections
# ---------------------------------------------------------------------------


class TestParseScriptSections:
    def test_empty_input(self):
        sections = parse_script_sections("")
        assert sections == []

    def test_plain_text_fallback(self):
        sections = parse_script_sections("Just some text without headers")
        assert len(sections) == 1
        assert sections[0].title == "Full Script"
        assert "Just some text" in sections[0].script_text

    def test_parse_scene_format(self):
        raw = (
            "## SCENE: Hook\n"
            "TIMESTAMP: 0:00-0:15\n"
            "SCRIPT: Hey everyone, welcome!\n"
            "B-ROLL: montage of code snippets\n"
            "ON-SCREEN TEXT: Welcome\n"
            "\n"
            "## SCENE: Intro\n"
            "TIMESTAMP: 0:15-1:00\n"
            "SCRIPT: Today we are going to learn...\n"
            "B-ROLL: typing on keyboard\n"
        )
        sections = parse_script_sections(raw)
        assert len(sections) == 2
        assert sections[0].title == "Hook"
        assert sections[0].timestamp_start == "0:00"
        assert sections[0].timestamp_end == "0:15"
        assert "everyone" in sections[0].script_text
        assert len(sections[0].broll_suggestions) == 1
        assert sections[0].onscreen_text == "Welcome"

    def test_parse_bracket_timestamps(self):
        raw = (
            "## HOOK [0:00-0:15]\n"
            "Script goes here\n"
        )
        sections = parse_script_sections(raw)
        assert len(sections) == 1
        assert sections[0].timestamp_start == "0:00"
        assert sections[0].timestamp_end == "0:15"

    def test_timestamp_property(self):
        section = ScriptSection(title="Test", timestamp_start="0:00", timestamp_end="0:30")
        assert section.timestamp == "[0:00-0:30]"

    def test_timestamp_property_start_only(self):
        section = ScriptSection(title="Test", timestamp_start="1:00")
        assert section.timestamp == "[1:00]"

    def test_timestamp_property_empty(self):
        section = ScriptSection(title="Test")
        assert section.timestamp == ""


# ---------------------------------------------------------------------------
# export_teleprompter
# ---------------------------------------------------------------------------


class TestExportTeleprompter:
    def test_from_sections(self):
        sections = [
            ScriptSection(title="Hook", script_text="Hey everyone!"),
            ScriptSection(title="Intro", script_text="Today we learn about Python."),
        ]
        script = VideoScript(
            topic="Python", style="educational", duration_minutes=10, sections=sections
        )
        result = export_teleprompter(script)
        assert "Hey everyone!" in result
        assert "Today we learn" in result
        assert "B-ROLL" not in result

    def test_from_raw_text_strips_broll(self):
        raw = (
            "Say this line\n"
            "[B-ROLL] some visuals\n"
            "Another line\n"
            "[ON-SCREEN TEXT] overlay\n"
            "Final line\n"
        )
        script = VideoScript(
            topic="Test", style="tutorial", duration_minutes=5, raw_text=raw
        )
        result = export_teleprompter(script)
        assert "Say this line" in result
        assert "Another line" in result
        assert "Final line" in result
        assert "B-ROLL" not in result
        assert "ON-SCREEN TEXT" not in result

    def test_empty_sections(self):
        script = VideoScript(
            topic="Test", style="vlog", duration_minutes=3, raw_text="Hello world"
        )
        result = export_teleprompter(script)
        assert "Hello world" in result


# ---------------------------------------------------------------------------
# VideoScript dataclass
# ---------------------------------------------------------------------------


class TestVideoScript:
    def test_word_count(self):
        script = VideoScript(
            topic="Test", style="tutorial", duration_minutes=10,
            raw_text="one two three four five"
        )
        assert script.word_count == 5

    def test_estimated_duration(self):
        text = " ".join(["word"] * 300)
        script = VideoScript(
            topic="Test", style="tutorial", duration_minutes=10, raw_text=text
        )
        assert script.estimated_duration == 2.0

    def test_full_text_from_sections(self):
        sections = [
            ScriptSection(title="A", script_text="First part."),
            ScriptSection(title="B", script_text="Second part."),
        ]
        script = VideoScript(
            topic="Test", style="vlog", duration_minutes=5,
            sections=sections, raw_text="raw fallback"
        )
        assert "First part." in script.full_text
        assert "Second part." in script.full_text
        assert "raw fallback" not in script.full_text


# ---------------------------------------------------------------------------
# ScriptSection dataclass
# ---------------------------------------------------------------------------


class TestScriptSection:
    def test_default_values(self):
        s = ScriptSection(title="Test")
        assert s.timestamp_start == ""
        assert s.timestamp_end == ""
        assert s.script_text == ""
        assert s.broll_suggestions == []
        assert s.onscreen_text == ""


# ---------------------------------------------------------------------------
# generate_script (mocked)
# ---------------------------------------------------------------------------


class TestGenerateScript:
    @patch("video_script.core.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "## HOOK\n[0:00-0:15]\nHey everyone! Today we're diving into..."
        result = generate_script("Python Tips", 10, "educational", None)
        assert "HOOK" in result
        mock_chat.assert_called_once()

    @patch("video_script.core.chat")
    def test_generate_uses_correct_max_tokens(self, mock_chat):
        mock_chat.return_value = "Script content"
        generate_script("Topic", 10, "tutorial", None)
        _, kwargs = mock_chat.call_args
        assert kwargs["max_tokens"] == 4096


# ---------------------------------------------------------------------------
# generate_hook (mocked)
# ---------------------------------------------------------------------------


class TestGenerateHook:
    @patch("video_script.core.chat")
    def test_returns_list(self, mock_chat):
        mock_chat.return_value = "1. Hook one text\n2. Hook two text\n3. Hook three text"
        hooks = generate_hook("Python", "educational", num_hooks=3)
        assert isinstance(hooks, list)
        assert len(hooks) == 3

    @patch("video_script.core.chat")
    def test_single_item_fallback(self, mock_chat):
        mock_chat.return_value = "Just one big hook paragraph."
        hooks = generate_hook("Python", "tutorial", num_hooks=3)
        assert isinstance(hooks, list)
        assert len(hooks) >= 1


# ---------------------------------------------------------------------------
# generate_thumbnail_ideas (mocked)
# ---------------------------------------------------------------------------


class TestGenerateThumbnailIdeas:
    @patch("video_script.core.chat")
    def test_returns_list(self, mock_chat):
        mock_chat.return_value = "1. Idea one\n2. Idea two\n3. Idea three"
        ideas = generate_thumbnail_ideas("Python", "educational", num_ideas=3)
        assert isinstance(ideas, list)
        assert len(ideas) == 3


# ---------------------------------------------------------------------------
# suggest_broll (mocked)
# ---------------------------------------------------------------------------


class TestSuggestBroll:
    @patch("video_script.core.chat")
    def test_returns_list(self, mock_chat):
        mock_chat.return_value = "1. Close-up of hands typing\n2. Screen recording\n3. Whiteboard diagram"
        suggestions = suggest_broll("Python", "This section explains decorators", num_suggestions=3)
        assert isinstance(suggestions, list)
        assert len(suggestions) == 3


# ---------------------------------------------------------------------------
# generate_scene_breakdown (mocked)
# ---------------------------------------------------------------------------


class TestGenerateSceneBreakdown:
    @patch("video_script.core.chat")
    def test_returns_sections(self, mock_chat):
        mock_chat.return_value = (
            "## SCENE: Hook\n"
            "TIMESTAMP: 0:00-0:15\n"
            "SCRIPT: Grab attention here\n"
            "B-ROLL: Quick cuts montage\n"
            "\n"
            "## SCENE: Main Content\n"
            "TIMESTAMP: 0:15-5:00\n"
            "SCRIPT: Explain the topic in depth\n"
            "B-ROLL: Screen recording\n"
        )
        scenes = generate_scene_breakdown("Python Tips", 10, "educational")
        assert isinstance(scenes, list)
        assert len(scenes) == 2
        assert scenes[0].title == "Hook"


# ---------------------------------------------------------------------------
# STYLES constant
# ---------------------------------------------------------------------------


class TestStyles:
    def test_styles_is_list(self):
        assert isinstance(STYLES, list)

    def test_styles_contains_educational(self):
        assert "educational" in STYLES

    def test_styles_count(self):
        assert len(STYLES) >= 6
