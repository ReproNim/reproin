"""Commands for managing lists of studies and accessions."""

import os
import re
import glob
import datetime
import subprocess
from pathlib import Path

import click

from ..utils import run_command, info, error, debug
from ..config import Config


def lists_update(config, year=None, month=None, day=None):
    """Update the list of studies and accessions."""
    if year is None:
        year = datetime.datetime.now().strftime("%Y")
    if month is None:
        month = datetime.datetime.now().strftime("%m")
    if day is None:
        day = "*"

    day_suffix = "xx" if day == "*" else day
    
    # Create the list directory if it doesn't exist
    os.makedirs(config.list_dir, exist_ok=True)
    
    # Create the list file path
    list_file = os.path.join(config.list_dir, f"{year}{month}{day_suffix}.txt")
    
    click.echo(f"INFO: updating {list_file}")
    
    # Run heudiconv command to list the files
    scout_pattern = f"{config.dicom_dir}/{year}/{month}/{day}/*/00*cout*"
    cmd = f"{config.heudiconv_cmd} -f {config.heuristic} --command ls --files {scout_pattern}"
    
    try:
        result = run_command(cmd, capture_output=True)
        
        # Write the output to the list file
        with open(list_file, "w") as f:
            f.write(result.stdout)
            
        return list_file
    except Exception as e:
        error(f"Failed to update lists: {e}")
        return None


def lists_check(config, year="20??", month="??"):
    """Check if there are any accessions that are not in the lists."""
    todo = {}
    groups = {}
    
    for d in glob.glob(f"{config.dicom_dir}/{year}/{month}"):
        m = os.path.basename(d)
        y = os.path.basename(os.path.dirname(d))
        
        if y == "2016":  # Skip early data
            continue
            
        list_file = os.path.join(config.list_dir, f"{y}{m}xx.txt")
        if not os.path.exists(list_file):
            click.echo(f"I: no {list_file}")
            
            # Check if there are any scout files
            scout_pattern = f"{config.dicom_dir}/{y}/{m}/*/*/00*cout*"
            result = run_command(f"ls -d {scout_pattern}", capture_output=True)
            
            if result.returncode == 0 and result.stdout.strip():
                click.echo("E: there were legitimatish accession folders with scouts!")
                todo[f"{m}_{y}"] = "scouts"
                
            continue
            
        missing = []
        
        for a in glob.glob(f"{config.dicom_dir}/{y}/{m}/*/*"):
            # Skip backup folders where original exists
            if a.endswith("_backup") and os.path.exists(a[:-7]):
                click.echo(f"skip odd backup {a} for which original also exists")
                continue
                
            # Check if there are any scout files
            scout_pattern = f"{a}/00*cout*"
            result = run_command(f"ls -1 {scout_pattern}", capture_output=True)
            
            if result.returncode != 0 or not result.stdout.strip():
                debug(f"no scouts under {a}")
                continue
                
            # Check if the accession is in the list file
            with open(list_file, "r") as f:
                content = f.read()
                
            if not content.startswith(a):
                scouts = result.stdout.split("\n")[0]
                
                if "permission" in scouts.lower():
                    # Permission issue
                    result = run_command(f"ls -dl {a}", capture_output=True)
                    reason = f"permissions? {result.stdout.strip()}"
                    
                    # Get the group
                    result = run_command(f"stat -c '%G' {a}", capture_output=True)
                    group = result.stdout.strip()
                    
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(a)
                else:
                    reason = "unknown"
                    missing.append(a)
                    
                click.echo(f"{a} is missing: {reason}")
                
        if missing:
            todo[f"{m}_{y}"] = "missing"
            
    # Return todo items
    exit_code = 0
    
    if todo:
        click.echo("List of TODOs:")
        for my, reason in todo.items():
            y = my.split("_")[1]
            m = my.split("_")[0]
            cmd = f"reproin lists-update {y} {m}"
            click.echo(cmd)
        exit_code += 1
        
    if groups:
        click.echo(f"List of groups for which permissions fail: {', '.join(groups.keys())}")
        for g, accessions in groups.items():
            click.echo(f"  {g}: {' '.join(accessions)}")
        exit_code += 2
        
    return exit_code


def lists_update_summary(config, input_data=None):
    """Extract and summarize locator values from lists."""
    if input_data is None:
        # If no input is provided, run lists-update
        result = run_command(f"reproin lists-update", capture_output=True)
        input_data = result.stderr
    
    # Extract locator values from the input
    pattern = r"StudySes.*locator='([^']*)'.*"
    locators = re.findall(pattern, input_data)
    
    # Count and sort locators
    locator_counts = {}
    for loc in locators:
        if loc in locator_counts:
            locator_counts[loc] += 1
        else:
            locator_counts[loc] = 1
    
    # Sort by count in descending order
    sorted_locators = sorted(locator_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Format output
    for count, locator in sorted_locators:
        click.echo(f"{count} {locator}")
    
    return sorted_locators


def lists_update_study_shows(config):
    """Update lists and show study information."""
    # Run lists-update and capture output
    result = run_command("reproin lists-update", capture_output=True)
    
    # Process the output with lists-update-summary
    summary = lists_update_summary(config, result.stderr)
    
    # For each study, show study information
    for count, study in summary:
        click.echo(f"{study}: new={count} ", nl=False)
        study_show_save(config, study)
    
    return 0