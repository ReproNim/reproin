"""Commands for managing accessions and subject skipping."""

import os
import subprocess
from pathlib import Path

import click

from ..utils import run_command, info, error
from ..config import Config


def study_accession_skip(config, study, accession, reason=None):
    """Add an accession to the skip file."""
    study_dir = os.path.join(config.bids_dir, study)
    if not os.path.exists(study_dir):
        error(f"Study directory {study_dir} does not exist")
        return 1
    
    # Change to the study directory
    old_cwd = os.getcwd()
    os.chdir(study_dir)
    
    # Path to the skip file
    skip_file = config.skip_file
    
    # Check if skip file is a symlink, and unlock if needed
    if os.path.islink(skip_file):
        skip_file_dir = os.path.dirname(skip_file)
        skip_file_name = os.path.basename(skip_file)
        
        if os.path.exists(skip_file_dir):
            os.chdir(skip_file_dir)
            run_command(f"git annex unlock {skip_file_name}")
            os.chdir(study_dir)
    
    # Add the accession to the skip file
    skip_line = f"{accession}"
    if reason:
        skip_line += f" {reason}"
    
    # Create the skip file if it doesn't exist
    os.makedirs(os.path.dirname(skip_file), exist_ok=True)
    
    with open(skip_file, "a") as f:
        f.write(f"{skip_line}\n")
    
    # Add to git annex and save
    run_command(f"git annex add {skip_file}")
    run_command(f"datalad save -d. -m 'skip an accession' {skip_file}")
    
    # Return to original directory
    os.chdir(old_cwd)
    
    return 0


def study_remove_subject(config, study, sid, session=None):
    """Remove a subject from a study."""
    study_dir = os.path.join(config.bids_dir, study)
    if not os.path.exists(study_dir):
        error(f"Study directory {study_dir} does not exist")
        return 1
    
    # Change to the study directory
    old_cwd = os.getcwd()
    os.chdir(study_dir)
    
    # Build paths to remove
    paths = [f"sub-{sid}", f"sourcedata/sub-{sid}", f".heudiconv/{sid}"]
    
    # Remove the paths
    cmd = f"git rm -r {' '.join(paths)}"
    result = run_command(cmd)
    
    if result.returncode != 0:
        error(f"Failed to remove subject: {result.stderr}")
        return 1
    
    # Return to original directory
    os.chdir(old_cwd)
    
    return 0


def study_remove_subject2redo(config, study, sid, session=None):
    """Remove a subject from a study and add to skip file to redo later."""
    # First, try to figure out where the subject came from
    study_dir = os.path.join(config.bids_dir, study)
    if not os.path.exists(study_dir):
        error(f"Study directory {study_dir} does not exist")
        return 1
    
    # Change to the study directory
    old_cwd = os.getcwd()
    os.chdir(study_dir)
    
    # Get the source path for the subject
    subses_id = sid
    if session:
        subses_id += f"/ses-{session}"
    
    # Import here to avoid circular imports
    from ..utils import infodir_sourcepath
    
    src_path = infodir_sourcepath(subses_id, config.heudiconv_dir)
    
    if not src_path:
        error(f"Could not determine source path for {subses_id}")
        return 1
    
    # Remove the subject
    study_remove_subject(config, study, sid, session)
    
    # Add to skip file
    study_accession_skip(config, study, src_path, "to redo")
    
    # Return to original directory
    os.chdir(old_cwd)
    
    return 0