"""Commands for reconverting sourcedata."""

import os
import re
import glob
import subprocess
from pathlib import Path

import click

from ..utils import run_command, info, error, debug
from ..config import Config


def reconvert_sourcedata(config, paths):
    """Reconvert sourcedata for specific subject/session folders."""
    if not os.path.exists("dataset_description.json"):
        error("Run from the top directory of BIDS dataset")
        return 1
    
    # Process paths to strip "sourcedata/" prefix if present
    clean_paths = []
    for path in paths:
        if path.startswith("sourcedata/"):
            clean_paths.append(path[11:])
        else:
            clean_paths.append(path)
    
    # Sanity check - ensure all folders have *_scans.tsv
    for path in clean_paths:
        scans_files = glob.glob(f"{path}/*_scans.tsv")
        if not scans_files:
            error(f"{path} lacks a _scans.tsv file. Make sure to point to sub-[/ses-] folders")
            return 1
        
        if not os.path.exists(f"sourcedata/{path}"):
            error(f"{path} lacks entry under sourcedata/")
            return 1
    
    # Determine heuristic
    heuristic = config.heuristic
    if os.path.exists(".heudiconv/heuristic.py"):
        info("Will use study specific heuristic")
        heuristic = ".heudiconv/heuristic.py"
    
    info(f"Will reconvert {len(clean_paths)} subject session folders")
    
    for path in clean_paths:
        # Extract subject and session info
        if path.startswith("sub-"):
            sub_parts = path.split("/")
            sub = sub_parts[0][4:]  # Remove "sub-" prefix
            
            opts = ["-s", sub]
            heudiconv_f = f".heudiconv/{sub}"
            
            # Check for session
            if len(sub_parts) > 1 and sub_parts[1].startswith("ses-"):
                ses = sub_parts[1][4:]  # Remove "ses-" prefix
                opts.extend(["-ss", ses])
                heudiconv_f += f"/{sub_parts[1]}"
        else:
            error(f"Folder {path} is not sub-*")
            return 1
        
        # Get all files except physio
        rm_files = []
        for file in glob.glob(f"{path}/*"):
            if "physio" not in file:
                rm_files.append(file)
        
        # Create datalad run command
        cmd = (
            f"datalad run -m 'Reconvert {path}' --input sourcedata/{path} bash -x -c "
            f"\"rm -rf {' '.join(rm_files)} {heudiconv_f} && "
            f"mkdir -p '{heudiconv_f}' && "
            f"mv sourcedata/{path} sourcedata/{path}.src && "
            f"heudiconv -f {heuristic} -c dcm2niix --bids -o . -l . {' '.join(['-s', sub])}"
            f"{' -ss ' + ses if 'ses' in locals() else ''} --files sourcedata/{path}.src -g all "
            f">& {heudiconv_f}/heudiconv.log && "
            f"if [ -e sourcedata/{path}.src/physio ] ; then "
            f"mv sourcedata/{path}.src/physio sourcedata/{path}/; fi && "
            f"rm -rf sourcedata/{path}.src\""
        )
        
        # Run the command
        result = run_command(cmd)
        if result.returncode != 0:
            error(f"Failed to reconvert {path}: {result.stderr}")
            return 1
    
    return 0