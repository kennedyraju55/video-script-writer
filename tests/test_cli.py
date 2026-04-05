"""Tests for video_script.cli module."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from video_script.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    @patch("video_script.cli.check_ollama_running", return_value=True)
    @patch("video_script.core.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## HOOK\nHey everyone!\n\n## INTRO\nToday we..."
        result = runner.invoke(main, ["--topic", "Python Tips"])
        assert result.exit_code == 0

    @patch("video_script.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--topic", "Test"])
        assert result.exit_code != 0

    @patch("video_script.cli.check_ollama_running", return_value=True)
    @patch("video_script.core.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Script\nFull script content here."
        result = runner.invoke(
            main,
            ["--topic", "Python Tips", "--duration", "15", "--style", "tutorial", "--audience", "beginners"],
        )
        assert result.exit_code == 0

    @patch("video_script.cli.check_ollama_running", return_value=True)
    @patch("video_script.core.chat")
    def test_cli_hooks_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "1. Hook one\n2. Hook two\n3. Hook three"
        result = runner.invoke(main, ["--topic", "Python Tips", "--hooks"])
        assert result.exit_code == 0

    @patch("video_script.cli.check_ollama_running", return_value=True)
    @patch("video_script.core.chat")
    def test_cli_thumbnails_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "1. Thumb one\n2. Thumb two\n3. Thumb three"
        result = runner.invoke(main, ["--topic", "Python Tips", "--thumbnails"])
        assert result.exit_code == 0

    @patch("video_script.cli.check_ollama_running", return_value=True)
    @patch("video_script.core.chat")
    def test_cli_scene_breakdown_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = (
            "## SCENE: Hook\n"
            "TIMESTAMP: 0:00-0:15\n"
            "SCRIPT: Grab attention\n"
            "B-ROLL: montage\n"
        )
        result = runner.invoke(main, ["--topic", "Python Tips", "--scene-breakdown"])
        assert result.exit_code == 0

    @patch("video_script.cli.check_ollama_running", return_value=True)
    @patch("video_script.core.chat")
    def test_cli_teleprompter_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## HOOK\nSay this line\n[B-ROLL] visuals\nAnother line"
        result = runner.invoke(main, ["--topic", "Python Tips", "--teleprompter"])
        assert result.exit_code == 0
        assert "Teleprompter" in result.output
