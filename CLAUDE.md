# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Build containers: `./generate_container.sh`
- Run basic test: `tests/test_run.sh`
- Convert DICOM to BIDS: `heudiconv -f reproin --bids --datalad -o OUTPUT --files INPUT`
- Update lists: `reproin lists-update`
- Show study status: `reproin study-show STUDY`
- Convert study: `reproin study-convert STUDY`

## Environment Setup
- Use conda/mamba: `mamba create -n reproin -y datalad datalad-container singularity`
- Activate: `mamba activate reproin`

## Code Style
- Python: Follow PEP8 conventions; use pathlib for path handling
- Shell scripts: Use `-eu -o pipefail` for error handling
- Error handling: Use descriptive info/error messages with prefix (info/error)
- Naming: Use snake_case for functions
- Documentation: Document functions with clear comments
- Git: Commit messages should be descriptive and follow repository conventions
- Datalad: Use git-annex for data files, git for code/metadata (see .gitattributes)