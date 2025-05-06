"""Configuration for the ReproIn package."""

import os
from pathlib import Path

class Config:
    """Configuration for the ReproIn package."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Directories
        self.dicom_dir = os.environ.get("DICOM_DIR", "/inbox/DICOM")
        self.bids_dir = os.environ.get("BIDS_DIR", "/inbox/BIDS")
        self.list_dir = os.path.join(self.bids_dir, "reproin/lists")
        
        # Paths for heudiconv configuration
        self.heudiconv_dir = ".heudiconv"
        self.skip_file = os.path.join(self.heudiconv_dir, "sid-skip")
        self.val_log = os.path.join(self.heudiconv_dir, "bids-validator.log")
        self.val_config = ".bids-validator-config.json"
        
        # HeuDiConv command configuration
        self.heuristic = "reproin"
        self.heudiconv_cmd = (
            f"heudiconv -c dcm2niix --bids -o {self.bids_dir} -g accession_number"
        )
        
        # Container configuration
        self.local_containers = os.environ.get(
            "REPRONIM_CONTAINERS", 
            os.path.expanduser("~/repronim-containers")
        )
        
        # Auto actions
        self.do_auto_create_ds = True
        self.do_auto_conversion = True
        
        # Store the script path to find resources
        self.script_path = Path(__file__).resolve().parent
        self.resources_path = self.script_path.parent.parent / "resources"

    def update_from_env(self):
        """Update configuration from environment variables."""
        self.dicom_dir = os.environ.get("DICOM_DIR", self.dicom_dir)
        self.bids_dir = os.environ.get("BIDS_DIR", self.bids_dir)
        self.list_dir = os.path.join(self.bids_dir, "reproin/lists")
        self.local_containers = os.environ.get(
            "REPRONIM_CONTAINERS", 
            self.local_containers
        )
        
        # Update heudiconv command with new bids_dir
        self.heudiconv_cmd = (
            f"heudiconv -c dcm2niix --bids -o {self.bids_dir} -g accession_number"
        )
        
        return self