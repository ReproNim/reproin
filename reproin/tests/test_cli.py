"""Tests for the CLI interface of ReproIn."""

import pytest
from unittest.mock import patch, MagicMock, ANY
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
    assert "setup" in result.output
    assert "reconvert" in result.output


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
        # Use ANY for config as it's a different instance but should have the same values
        assert args[1:] == ("2024", "01", "01")


@patch("reproin.cli.study_create")
def test_cli_study_create_command(mock_study_create, runner):
    """Test that the study create command works."""
    with patch("reproin.cli.config", Config()):
        mock_study_create.return_value = 0
        result = runner.invoke(main, ["study", "create", "test/study"])
        assert result.exit_code == 0
        mock_study_create.assert_called_once()
        
        # Check only the study argument, not the config
        args, _ = mock_study_create.call_args
        assert args[1] == "test/study"


@patch("reproin.cli.study_show")
def test_cli_study_show_command(mock_study_show, runner):
    """Test that the study show command works."""
    with patch("reproin.cli.config", Config()):
        mock_study_show.return_value = 0
        result = runner.invoke(main, ["study", "show", "test/study"])
        assert result.exit_code == 0
        mock_study_show.assert_called_once()
        
        # Check only the study and target_sub arguments, not the config
        args, _ = mock_study_show.call_args
        assert args[1] == "test/study"
        assert args[2] is None


@patch("reproin.cli.study_convert")
def test_cli_study_convert_command(mock_study_convert, runner):
    """Test that the study convert command works."""
    with patch("reproin.cli.config", Config()):
        mock_study_convert.return_value = 0
        result = runner.invoke(main, ["study", "convert", "test/study"])
        assert result.exit_code == 0
        mock_study_convert.assert_called_once()
        
        # Check only the study and target_sub arguments, not the config
        args, _ = mock_study_convert.call_args
        assert args[1] == "test/study"
        assert args[2] is None


@patch("reproin.cli.validator")
def test_cli_validate_run_command(mock_validator, runner):
    """Test that the validate run command works."""
    with patch("reproin.cli.config", Config()):
        mock_validator.return_value = 0
        result = runner.invoke(main, ["validate", "run", "test/study"])
        assert result.exit_code == 0
        mock_validator.assert_called_once()
        
        # Check only the study argument, not the config
        args, _ = mock_validator.call_args
        assert args[1] == "test/study"


@patch("reproin.cli.validator_save")
def test_cli_validate_save_command(mock_validator_save, runner):
    """Test that the validate save command works."""
    with patch("reproin.cli.config", Config()):
        mock_validator_save.return_value = 0
        result = runner.invoke(main, ["validate", "save", "test/study"])
        assert result.exit_code == 0
        mock_validator_save.assert_called_once()
        
        # Check only the study argument, not the config
        args, _ = mock_validator_save.call_args
        assert args[1] == "test/study"


@patch("reproin.cli.setup_containers")
def test_cli_setup_containers_command(mock_setup_containers, runner):
    """Test that the setup containers command works."""
    with patch("reproin.cli.config", Config()):
        mock_setup_containers.return_value = 0
        result = runner.invoke(main, ["setup", "containers"])
        assert result.exit_code == 0
        mock_setup_containers.assert_called_once()


@patch("reproin.cli.reconvert_sourcedata")
def test_cli_reconvert_sourcedata_command(mock_reconvert_sourcedata, runner):
    """Test that the reconvert sourcedata command works."""
    with patch("reproin.cli.config", Config()):
        mock_reconvert_sourcedata.return_value = 0
        result = runner.invoke(main, ["reconvert", "sourcedata", "path1", "path2"])
        assert result.exit_code == 0
        mock_reconvert_sourcedata.assert_called_once()
        
        # Check only the paths argument, not the config
        args, _ = mock_reconvert_sourcedata.call_args
        assert args[1] == ("path1", "path2")


# Test for backward compatibility
@patch("reproin.cli.lists_update")
def test_cli_legacy_lists_update_command(mock_lists_update, runner):
    """Test that the legacy lists-update command still works."""
    with patch("reproin.cli.config", Config()):
        mock_lists_update.return_value = "/tmp/lists.txt"
        result = runner.invoke(main, ["lists-update", "2024", "01", "01"])
        assert result.exit_code == 0
        assert "DEPRECATED: Use 'reproin lists update' instead" in result.output
        mock_lists_update.assert_called_once()