"""Commands for validating BIDS datasets."""

import os
import re
import subprocess
from pathlib import Path

import click

from ..utils import run_command, info, error
from ..config import Config


def validator(config, study=None):
    """Run BIDS validator on a study."""
    # If study is specified, change to study directory
    old_cwd = None
    if study:
        study_dir = os.path.join(config.bids_dir, study)
        if os.path.exists(study_dir):
            old_cwd = os.getcwd()
            os.chdir(study_dir)
        else:
            error(f"Study directory {study_dir} does not exist")
            return 1
    
    # Determine config file path
    val_config = config.val_config
    if not os.path.exists(val_config):
        val_config = os.path.expanduser("~/heudiconv/heudiconv/heuristics/reproin_validator.cfg")
        if not os.path.exists(val_config):
            error(f"Validator config file {val_config} does not exist")
            return 1
    
    # Run validator
    cmd = f"bids-validator --verbose -c {val_config} {os.getcwd()}"
    result = run_command(cmd, capture_output=True)
    
    # Print output
    click.echo(result.stdout)
    
    # Return to original directory if needed
    if old_cwd:
        os.chdir(old_cwd)
    
    # Return success even if validator failed
    return 0


def validator_save(config, study):
    """Run validator and save output to a file."""
    if not study:
        error("Study must be specified")
        return 1
    
    study_dir = os.path.join(config.bids_dir, study)
    if not os.path.exists(study_dir):
        error(f"Study directory {study_dir} does not exist")
        return 1
    
    # Change to study directory
    old_cwd = os.getcwd()
    os.chdir(study_dir)
    
    # Remove existing validator log
    val_log = config.val_log
    if os.path.exists(val_log):
        os.remove(val_log)
    
    # Run validator and save output
    result = run_command(f"reproin validator {study}", capture_output=True)
    
    with open(val_log, "w") as f:
        f.write(result.stdout)
    
    # Log output location
    info(f"Validator output in {os.getcwd()}/{val_log}")
    
    # Save to datalad
    run_command(f"datalad save -d . -m 'New BIDS validator output' {val_log}")
    
    # Return to original directory
    os.chdir(old_cwd)
    
    return 0


def validator_summary(config, study):
    """Show summary of validator errors and warnings."""
    if not study:
        error("Study must be specified")
        return 1
    
    study_dir = os.path.join(config.bids_dir, study)
    val_log = os.path.join(study_dir, config.val_log)
    
    if not os.path.exists(val_log):
        error(f"Validator log file {val_log} does not exist")
        return 1
    
    # Log header
    info("Errors/warnings from current state of the validator:")
    
    # Extract errors and warnings
    with open(val_log, "r") as f:
        content = f.read()
    
    matches = re.findall(r'[0-9]+: \[[A-Z]+\]', content)
    
    if matches:
        for match in matches:
            click.echo(f"  {match}")
    else:
        click.echo("  no messages were found")
    
    return 0


def validator_show(config, study):
    """Show validator output in a pager."""
    if not study:
        error("Study must be specified")
        return 1
    
    study_dir = os.path.join(config.bids_dir, study)
    val_log = os.path.join(study_dir, config.val_log)
    
    if not os.path.exists(val_log):
        error(f"Validator log file {val_log} does not exist")
        return 1
    
    # Determine pager
    pager = os.environ.get("PAGER", "vim")
    
    # Run pager
    subprocess.run([pager, val_log])
    
    return 0