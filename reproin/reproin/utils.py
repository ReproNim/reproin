"""Utility functions for ReproIn."""

import os
import re
import json
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger("reproin")

def infodir_sourcepath(subject_id, heudiconv_dir=".heudiconv"):
    """Extract the source path from HeuDiConv's info directory.
    
    Python equivalent of the bash script's infodir_sourcepath function.
    """
    info_dir = Path(heudiconv_dir) / subject_id / "info"
    if not info_dir.exists():
        return None

    common_paths = []
    for file in info_dir.glob("filegroup*.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                for item in data:
                    if isinstance(item, dict) and "/" in str(item.get("value", "")):
                        common_paths.append(item["value"])
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    if not common_paths:
        return None

    # Find the common path prefix
    common_prefix = os.path.commonpath(common_paths) if common_paths else None
    return common_prefix

def run_command(cmd, capture_output=True, check=False):
    """Run a command and return its output."""
    logger.debug(f"Running command: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=capture_output, 
        text=True, 
        check=check
    )
    return result

def info(message):
    """Log an informational message."""
    logger.info(message)
    return f"# {message}"

def error(message):
    """Log an error message."""
    logger.error(message)
    return f"# ERROR: {message}"

def debug(message):
    """Log a debug message."""
    logger.debug(message)

def get_dcm2niix_version():
    """Get the version of dcm2niix."""
    try:
        result = run_command("dcm2niix -v", capture_output=True)
        output = result.stdout or result.stderr
        match = re.search(r'version v(\S+)', output)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error getting dcm2niix version: {e}")
        return None

def get_heudiconv_version():
    """Get the version of heudiconv."""
    try:
        result = run_command("heudiconv --version", capture_output=True)
        output = result.stdout or result.stderr
        return output.strip()
    except Exception as e:
        logger.error(f"Error getting heudiconv version: {e}")
        return None