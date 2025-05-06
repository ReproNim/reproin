"""Basic tests for the ReproIn CLI."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from reproin.cli import main
from reproin.config import Config
from reproin.utils import get_dcm2niix_version, get_heudiconv_version


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


def test_config_initialization():
    """Test that the Config class initializes correctly."""
    config = Config()
    assert config.dicom_dir == "/inbox/DICOM"
    assert config.bids_dir == "/inbox/BIDS"
    assert config.list_dir == "/inbox/BIDS/reproin/lists"
    assert config.heuristic == "reproin"


def test_config_update_from_env():
    """Test that the Config class updates from environment variables."""
    config = Config()
    with patch.dict(os.environ, {"DICOM_DIR": "/test/dicom", "BIDS_DIR": "/test/bids"}):
        config.update_from_env()
        assert config.dicom_dir == "/test/dicom"
        assert config.bids_dir == "/test/bids"
        assert config.list_dir == "/test/bids/reproin/lists"


def test_utils_get_versions():
    """Test that the version utilities work as expected when commands don't exist."""
    # This should return None or a string depending on if command exists
    assert get_dcm2niix_version() is None or isinstance(get_dcm2niix_version(), str)
    assert get_heudiconv_version() is None or isinstance(get_heudiconv_version(), str)


@patch("reproin.utils.run_command")
def test_utils_get_dcm2niix_version(mock_run):
    """Test that the dcm2niix version utility returns the version."""
    mock_result = MagicMock()
    mock_result.stdout = "dcm2niiX version v1.0.20211006"
    mock_run.return_value = mock_result
    
    assert get_dcm2niix_version() == "1.0.20211006"


@patch("reproin.utils.run_command")
def test_utils_get_heudiconv_version(mock_run):
    """Test that the heudiconv version utility returns the version."""
    mock_result = MagicMock()
    mock_result.stdout = "1.0.0"
    mock_run.return_value = mock_result
    
    assert get_heudiconv_version() == "1.0.0"