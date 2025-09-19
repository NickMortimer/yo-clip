"""Tests for the main CLI module."""

from typer.testing import CliRunner
from yoclip.main import app


def test_hello_command():
    """Test the hello command."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello World!" in result.stdout


def test_hello_command_with_count():
    """Test the hello command with count option."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello", "World", "--count", "2"])
    assert result.exit_code == 0
    # Should contain "Hello World!" twice
    assert result.stdout.count("Hello World!") == 2


def test_hello_command_formal():
    """Test the hello command with formal option."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello", "World", "--formal"])
    assert result.exit_code == 0
    assert "Good day World!" in result.stdout


def test_version_command():
    """Test the version command."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "YoClip" in result.stdout


def test_info_command():
    """Test the info command."""
    runner = CliRunner()
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "YoClip" in result.stdout


def test_help():
    """Test the help command."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "YoClip" in result.stdout
