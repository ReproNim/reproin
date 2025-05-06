"""Tests for the CLI interface of ReproIn."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from reproin.cli import main
from reproin.config import Config


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


def test_cli_help(runner):
    """Test that the CLI help text is correct."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "ReproIn - automatic generation of shareable BIDS datasets" in result.output
    assert "Options:" in result.output
    assert "Commands:" in result.output
    assert "lists" in result.output
    assert "study" in result.output
    assert "validate" in result.output


def test_cli_version(runner):
    """Test that the CLI version is correct."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "main, version" in result.output


@patch("reproin.cli.lists_update")
def test_cli_lists_update_command(mock_lists_update, runner):
    """Test that the lists update command works."""
    with patch("reproin.cli.config", Config()):
        mock_lists_update.return_value = "/tmp/lists.txt"
        result = runner.invoke(main, ["lists", "update", "2024", "01", "01"])
        assert result.exit_code == 0
        mock_lists_update.assert_called_once()
        
        # Check that the arguments were passed correctly
        args, _ = mock_lists_update.call_args
        assert args[1] == "2024"
        assert args[2] == "01"
        assert args[3] == "01"