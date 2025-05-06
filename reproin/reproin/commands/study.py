"""Commands for managing studies."""

import os
import re
import glob
import datetime
import subprocess
from pathlib import Path

import click

from ..utils import run_command, info, error, debug, infodir_sourcepath
from ..config import Config


def study_create(config, study):
    """Create a new study directory."""
    study_dir = os.path.join(config.bids_dir, study)
    
    if os.path.exists(study_dir):
        click.echo(f"{study} already exists, nothing todo")
        return 1
        
    # Create the BIDS directory if it doesn't exist
    if not os.path.exists(config.bids_dir):
        run_command(f"datalad create -c text2git {config.bids_dir}", check=True)
        
    # Change to the BIDS directory
    os.chdir(config.bids_dir)
    
    # Create each directory in the study path
    dirs = study.split("/")
    for i, d in enumerate(dirs):
        if not os.path.exists(d):
            if f"{config.bids_dir}/{'/'.join(dirs[:i+1])}" == study_dir:
                # This is the final study directory
                run_command(f"datalad create --fake-dates -d . {d}", check=True)
            else:
                # This is a parent directory
                run_command(f"datalad create -c text2git -d . {d}", check=True)
                
            # Add .nfs* to .gitignore if not already there
            gitignore_path = os.path.join(d, ".gitignore")
            if not os.path.exists(gitignore_path) or ".nfs*" not in open(gitignore_path).read():
                with open(gitignore_path, "a") as f:
                    f.write(".nfs*\n")
                run_command(f"datalad save -d {d} -m 'ignore .nfs* files' {gitignore_path}", check=True)
                
        # Change to the directory for the next iteration
        os.chdir(d)
        
    # Now in the study directory, set up the configuration
    resources_path = config.resources_path
    run_command(f"datalad -c datalad.locations.user-procedures={resources_path} run-procedure cfg_reproin_bids", check=True)
    
    # Tag the beginning
    run_command("git tag -m 'The beginning' 0.0.0", check=True)
    
    # Set up containers
    setup_containers(config)
    
    # Set up development version of reproin (if needed)
    setup_devel_reproin(config)
    
    # Save the study status
    study_show_save(config, study)
    
    return 0


def setup_containers(config):
    """Set up containers for the study."""
    if os.path.exists("code/containers"):
        error("There is already code/containers")
        return 1
        
    # Create code directory if it doesn't exist
    os.makedirs("code", exist_ok=True)
    
    # Clone containers
    run_command(f"datalad clone -d . --reckless=ephemeral {config.local_containers} code/containers", check=True)
    
    # Configure submodule URL
    run_command("git config --file ./.gitmodules submodule.\"code/containers\".url https://datasets.datalad.org/repronim/containers/.git", check=True)
    run_command("git config --file ./.gitmodules submodule.\"code/containers\".datalad-url https://datasets.datalad.org/repronim/containers/.git", check=True)
    
    # Freeze versions
    old_dir = os.getcwd()
    os.chdir("code/containers/")
    run_command("scripts/freeze_versions --save-dataset=../../ repronim-reproin", check=True)
    os.chdir(old_dir)
    
    # Configure bind mounts
    if "BIDS_DIR" in os.environ:
        bids_mount = '-B "$BIDS_DIR" --env "BIDS_DIR=$BIDS_DIR"'
    else:
        bids_mount = '-B "$bidsdir"'
    
    # Update datalad config
    cmd = f"""
    cfg=datalad."containers.repronim-reproin".cmdexec
    orig=$(git config -f .datalad/config "$cfg")
    modified=$(echo "$orig" | sed -e "s,{{img}},-B '{config.dicom_dir}' {bids_mount} {{img}},g")
    git config -f .datalad/config $cfg "$modified"
    """
    run_command(cmd, check=True)
    
    # Save configuration
    run_command("datalad save -m 'Saving tune ups to enable using the embedded container with reproin' .gitmodules .datalad/config", check=True)
    
    return 0


def setup_devel_reproin(config):
    """Set up development version of reproin."""
    if not os.path.exists("code/containers"):
        error("Must have setup_containers already")
        return 1
        
    # Clone reproin
    run_command("datalad clone -d . https://github.com/ReproNim/reproin code/reproin", check=True)
    
    # Configure datalad container
    cmd = f"""
    cfg=datalad."containers.repronim-reproin".cmdexec
    orig=$(git config -f .datalad/config "$cfg")
    modified=$(echo "$orig" | sed -e 's,{{img}} {{cmd}}.*,-B {{img_dspath}}/code/reproin/bin/reproin:/usr/local/bin/reproin {{img}} /usr/local/bin/reproin {{cmd}},g' -e 's, run , exec ,g')
    git config -f .datalad/config $cfg "$modified"
    """
    run_command(cmd, check=True)
    
    # Save configuration
    run_command("datalad save -m 'Bundle/use development version of reproin script for now inside the container' .gitmodules .datalad/config", check=True)
    
    return 0


def study_show(config, study, target_sub=None):
    """Show information about a study."""
    study_dir = os.path.join(config.bids_dir, study)
    
    if not os.path.exists(study_dir):
        click.echo(f"I: no study directory yet - {study_dir}")
        return 1
        
    # Change to the study directory
    old_cwd = os.getcwd()
    os.chdir(study_dir)
    
    # Check dcm2niix version
    dcm2niixs_study = []
    result = run_command("git grep -h ConversionSoftwareVersion", capture_output=True)
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            match = re.search(r'"([^"]+)"', line)
            if match:
                version = match.group(1)
                if version and version not in dcm2niixs_study:
                    dcm2niixs_study.append(version)
    
    if dcm2niixs_study:
        if len(dcm2niixs_study) > 1:
            click.echo(f"W: Study already used multiple versions of dcm2niix: {', '.join(dcm2niixs_study)}")
        
        # Get current dcm2niix version
        result = run_command("dcm2niix -v", capture_output=True)
        current_version = ""
        for line in result.stdout.splitlines():
            if "version" in line:
                match = re.search(r'version v([^ ]+)', line)
                if match:
                    current_version = match.group(1)
                    break
        
        if current_version and current_version != dcm2niixs_study[-1]:
            click.echo(f"W: Wrong environment - dcm2niix {current_version} when study used {dcm2niixs_study[-1]}")
    
    # Use study-specific heuristic if available
    heuristic = config.heuristic
    if os.path.exists(f"{config.heudiconv_dir}/heuristic.py"):
        info("Will use study specific heuristic")
        heuristic = f"{config.heudiconv_dir}/heuristic.py"
    
    # Use study-specific anon-cmd if available
    heudiconv_cmd = config.heudiconv_cmd
    if os.path.exists(f"{config.heudiconv_dir}/anon-cmd"):
        info("Will use study specific anon-cmd")
        heudiconv_cmd = f"{heudiconv_cmd} --anon-cmd '{config.heudiconv_dir}/anon-cmd'"
    
    # Get all list files
    list_files = glob.glob(f"{config.list_dir}/*xx.txt")
    
    # Track already seen subject/session IDs
    subses_ids = []
    
    for list_file in list_files:
        with open(list_file, "r") as f:
            lines = f.readlines()
            
        # Process each line in the list file
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if the line contains the study
            if study in line:
                # Get the next line with subject/session info
                if i + 1 < len(lines) and "StudySess" in lines[i + 1]:
                    subses_line = lines[i + 1].strip()
                    
                    # Extract subject and session
                    sub_match = re.search(r"subject='([^']*)'", subses_line)
                    ses_match = re.search(r"session='([^']*)'", subses_line)
                    
                    if sub_match:
                        sub = sub_match.group(1)
                        ses = ses_match.group(1) if ses_match else None
                        
                        # Check if target subject is specified
                        if target_sub and sub != target_sub:
                            info(f"Skipping {sub} session={ses} since {sub} != {target_sub}")
                            i += 2
                            continue
                        
                        # Check if subject/session is in skip file
                        skip_file = os.path.join(config.heudiconv_dir, "sid-skip")
                        if os.path.exists(skip_file):
                            with open(skip_file, "r") as sf:
                                skip_content = sf.read()
                                if line in skip_content:
                                    info(f"{line} skip  # {sub} session={ses}")
                                    i += 2
                                    continue
                        
                        # Get the dicom directory
                        td = line.strip()
                        
                        # Check anonymization command
                        sub_orig = sub
                        anon_cmd = os.path.join(config.heudiconv_dir, "anon-cmd")
                        if os.path.exists(anon_cmd):
                            result = run_command(f"{anon_cmd} {sub}", capture_output=True)
                            if result.returncode == 0:
                                sub = result.stdout.strip()
                            else:
                                error(f"failed to get anonymized ID for {sub}, skipping")
                                i += 2
                                continue
                        
                        # Format subject/session for display
                        subses = f"{sub} "
                        if sub_orig != sub:
                            subses += f"({sub_orig}) "
                        subses += f"session={ses}"
                        
                        # Format subject/session options
                        subses_opts = f"-s '{sub}'"
                        if ses:
                            subses_opts += f" --ses '{ses}'"
                        
                        # Create subject/session ID
                        subses_id = sub
                        if ses:
                            subses_id += f"/ses-{ses}"
                        subsesheudiconvdir = os.path.join(config.heudiconv_dir, subses_id)
                        
                        # Check if already converted
                        srcdir = None
                        try:
                            srcdir = infodir_sourcepath(subses_id, config.heudiconv_dir)
                        except Exception:
                            pass
                        
                        alert = ""
                        if srcdir and srcdir != td:
                            alert = f" !!! came from {srcdir}"
                        
                        # Check if DICOM directory was converted into other subject/session
                        td_found_in = []
                        try:
                            for info_file in glob.glob(f"{config.heudiconv_dir}/*/info/*"):
                                with open(info_file, "r") as f:
                                    if td in f.read():
                                        dir_parts = info_file.split("/")
                                        if len(dir_parts) >= 3:
                                            found_subses = dir_parts[-3]
                                            if found_subses != subses_id and found_subses not in td_found_in:
                                                td_found_in.append(found_subses)
                        except Exception:
                            pass
                        
                        if td_found_in:
                            alert += f" !!! was converted into {' '.join(td_found_in)}"
                            # Skip as already converted into other subject/session
                            info(f"{td} done  {subses} {alert}")
                            i += 2
                            continue
                        elif subses_id in subses_ids:
                            info(f"WARNING: {subses_id} already known or converted")
                            i += 2
                            continue
                        
                        subses_ids.append(subses_id)
                        
                        # Check if already converted
                        if os.path.exists(os.path.join(subsesheudiconvdir, "info")):
                            info(f"{td} done  {subses} {alert}")
                            i += 2
                            continue
                        
                        # Show command to convert
                        cmd = f"{heudiconv_cmd} -f {heuristic} -l {study} --files {td}"
                        click.echo(f"{cmd} # {subses_opts}")
            
            i += 1
    
    # Return to original directory
    os.chdir(old_cwd)
    
    return 0


def study_convert(config, study, target_sub=None):
    """Convert a study's DICOM files to BIDS format."""
    # First, show the study to get commands
    result = run_command(f"reproin study-show {study} {target_sub if target_sub else ''}", capture_output=True)
    
    if result.returncode != 0:
        click.echo(result.stdout)
        return result.returncode
    
    # Extract conversion commands
    commands = []
    for line in result.stdout.splitlines():
        if line.startswith("heudiconv "):
            commands.append(line.split(" # ")[0])
    
    # Run each conversion command
    for cmd in commands:
        click.echo(f"INFO: Running {cmd}")
        result = run_command(cmd, check=False)
        
        if result.returncode != 0:
            error(f"Conversion failed: {result.stderr}")
            return result.returncode
    
    # Run validator
    run_command(f"reproin validator-save {study}", check=False)
    
    # Run validator summary
    run_command(f"reproin validator-summary {study}", check=False)
    
    return 0


def study_show_save(config, study):
    """Save the output of study-show."""
    study_dir = os.path.join(config.bids_dir, study)
    
    do_study_show = True
    if not os.path.exists(os.path.join(study_dir, ".git")):
        if config.do_auto_create_ds:
            click.echo("creating study directory")
            study_create(config, study)
    
    if not os.path.exists(os.path.join(study_dir, ".git")):
        click.echo("no studydir yet")
        do_study_show = False
    
    if do_study_show:
        study_show_script = os.path.join(study_dir, ".git", "study-show.sh")
        study_show_stderr = os.path.join(study_dir, ".git", "study-show.stderr")
        
        # Run study-show and save output
        result = run_command(f"reproin study-show {study}", capture_output=True)
        
        with open(study_show_script, "w") as f:
            f.write(result.stdout)
        
        with open(study_show_stderr, "w") as f:
            f.write(result.stderr)
        
        # Remove stderr file if empty
        if os.path.getsize(study_show_stderr) == 0:
            os.remove(study_show_stderr)
        
        # Show summary
        study_show_summary(config, study)
    
    return 0


def study_show_summary(config, study):
    """Show summary information about a study."""
    study_dir = os.path.join(config.bids_dir, study)
    study_show_script = os.path.join(study_dir, ".git", "study-show.sh")
    study_show_stderr = os.path.join(study_dir, ".git", "study-show.stderr")
    
    # Count commands, warnings, fixups, and done
    todo = 0
    warnings = 0
    fixups = 0
    done = 0
    
    if os.path.exists(study_show_script):
        with open(study_show_script, "r") as f:
            content = f.read()
            
            todo = content.count("heudiconv ")
            warnings = content.count("WARNING: ")
            fixups = content.count("!!!")
            done = content.count("# done ")
    
    # Format output
    output = f"todo={todo} done={done}"
    
    if fixups > 0:
        output += f" fixups={fixups}"
    
    if warnings > 0:
        output += f" warnings={warnings}"
    
    if os.path.exists(study_show_stderr) and os.path.getsize(study_show_stderr) > 0:
        with open(study_show_stderr, "r") as f:
            stderr_lines = len(f.readlines())
            output += f" stderrs={stderr_lines}"
    
    # Get modification date
    if os.path.exists(study_show_script):
        mod_time = os.path.getmtime(study_show_script)
        date_modified = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d")
        output += f" {study_show_script} {date_modified}"
    
    click.echo(output)
    
    return 0