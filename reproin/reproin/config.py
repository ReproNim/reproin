"""Configuration for the ReproIn package using Pydantic."""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ReproInSettings(BaseSettings):
    """Configuration for the ReproIn package.
    
    This class manages configuration values from environment variables and defaults.
    
    Attributes:
        dicom_dir: Directory containing DICOM files (default: /inbox/DICOM)
        bids_dir: Directory for BIDS output (default: /inbox/BIDS)
        repronim_containers: Path to local ReproNim containers
        heuristic: Heuristic to use for conversion
        heudiconv_cmd: Base command for running heudiconv
        do_auto_create_ds: Whether to auto-create datasets
        do_auto_conversion: Whether to auto-run conversion
    """
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=False,
        extra="ignore"
    )
    
    # Directories
    dicom_dir: str = Field(
        default="/inbox/DICOM", 
        description="Directory containing DICOM files",
        alias="DICOM_DIR",
    )
    bids_dir: str = Field(
        default="/inbox/BIDS", 
        description="Directory for BIDS output",
        alias="BIDS_DIR",
    )
    repronim_containers: str = Field(
        default=os.path.expanduser("~/repronim-containers"), 
        description="Path to local ReproNim containers",
        alias="REPRONIM_CONTAINERS",
    )
    
    # Heudiconv configuration
    heuristic: str = Field(
        default="reproin", 
        description="Heuristic to use for conversion",
        alias="REPROIN_HEURISTIC",
    )
    
    # Auto actions
    do_auto_create_ds: bool = Field(
        default=True, 
        description="Whether to auto-create datasets",
        alias="REPROIN_AUTO_CREATE_DS",
    )
    do_auto_conversion: bool = Field(
        default=True, 
        description="Whether to auto-run conversion",
        alias="REPROIN_AUTO_CONVERSION",
    )
    
    # Internal paths
    @computed_field
    def list_dir(self) -> str:
        """Path to the lists directory."""
        return os.path.join(self.bids_dir, "reproin/lists")
    
    @computed_field
    def heudiconv_dir(self) -> str:
        """Path to the heudiconv directory."""
        return ".heudiconv"
    
    @computed_field
    def skip_file(self) -> str:
        """Path to the skip file."""
        return os.path.join(self.heudiconv_dir, "sid-skip")
    
    @computed_field
    def val_log(self) -> str:
        """Path to the validator log."""
        return os.path.join(self.heudiconv_dir, "bids-validator.log")
    
    @computed_field
    def val_config(self) -> str:
        """Path to the validator config."""
        return ".bids-validator-config.json"
    
    @computed_field
    def heudiconv_cmd(self) -> str:
        """Base command for running heudiconv."""
        return f"heudiconv -c dcm2niix --bids -o {self.bids_dir} -g accession_number"
    
    @computed_field
    def script_path(self) -> Path:
        """Path to the script directory."""
        return Path(__file__).resolve().parent
    
    @computed_field
    def resources_path(self) -> Path:
        """Path to the resources directory."""
        return self.script_path.parent.parent / "resources"


# Initial instance for global configuration
config = ReproInSettings()


# For backward compatibility
class Config:
    """Legacy configuration class for backward compatibility.
    
    This class provides compatibility with the old Config class.
    New code should use ReproInSettings directly.
    """
    
    def __init__(self):
        """Initialize configuration with default values."""
        self._settings = ReproInSettings()
        self._reload_from_settings()
    
    def _reload_from_settings(self):
        """Reload configuration from settings."""
        self.dicom_dir = self._settings.dicom_dir
        self.bids_dir = self._settings.bids_dir
        self.list_dir = self._settings.list_dir
        self.heudiconv_dir = self._settings.heudiconv_dir
        self.skip_file = self._settings.skip_file
        self.val_log = self._settings.val_log
        self.val_config = self._settings.val_config
        self.heuristic = self._settings.heuristic
        self.heudiconv_cmd = self._settings.heudiconv_cmd
        self.local_containers = self._settings.repronim_containers
        self.do_auto_create_ds = self._settings.do_auto_create_ds
        self.do_auto_conversion = self._settings.do_auto_conversion
        self.script_path = self._settings.script_path
        self.resources_path = self._settings.resources_path
    
    def update_from_env(self):
        """Update configuration from environment variables.
        
        This method is kept for backward compatibility.
        We recreate the Pydantic settings instance to read current env vars.
        """
        # Create a new settings instance that will read current env variables
        self._settings = ReproInSettings()
        
        # Update attributes from the refreshed config
        self._reload_from_settings()
        
        # Update the global config for other parts of code
        global config
        config = self._settings
        
        return self