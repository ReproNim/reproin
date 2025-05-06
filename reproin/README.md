# ReproIn Python CLI

This is a refactored Python-based version of the ReproIn command-line tool, originally written in Bash.

## Features

- Modern Python CLI built with Click
- Hierarchical command structure for better organization
- Type-safe configuration using Pydantic
- Maintains backward compatibility with the original ReproIn bash script
- Improved error handling and logging

## Installation

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

The `reproin` command provides the following functionality:

```bash
# Show version information
reproin

# Show help
reproin --help

# List commands
reproin lists --help
reproin study --help
reproin validate --help
reproin setup --help
reproin reconvert --help

# Update lists of studies
reproin lists update

# Create a new study
reproin study create <study>

# Show study information
reproin study show <study>

# Convert a study's DICOM files to BIDS format
reproin study convert <study>

# Validate a study
reproin validate run <study>

# Set up containers for a study
reproin setup containers
```

## Configuration

The tool uses environment variables for configuration, defined in the `ReproInSettings` class:

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `DICOM_DIR` | Directory containing DICOM files | `/inbox/DICOM` |
| `BIDS_DIR` | Directory for BIDS output | `/inbox/BIDS` |
| `REPRONIM_CONTAINERS` | Path to local ReproNim containers | `~/repronim-containers` |
| `REPROIN_HEURISTIC` | Heuristic to use for conversion | `reproin` |
| `REPROIN_AUTO_CREATE_DS` | Whether to auto-create datasets | `True` |
| `REPROIN_AUTO_CONVERSION` | Whether to auto-run conversion | `True` |

Example:
```bash
# Set configuration variables
export DICOM_DIR=/data/dicom
export BIDS_DIR=/data/bids

# Run the command
reproin lists update
```

## Command Groups

The commands are organized into logical groups:

1. **lists**: Commands for managing lists of studies and accessions
   - `lists update`: Update the list of studies and accessions
   - `lists check`: Check accessions not in the lists
   - `lists update-summary`: Summarize locator values
   - `lists update-study-shows`: Update lists and show study information

2. **study**: Commands for managing studies
   - `study create`: Create a new study directory
   - `study show`: Show information about a study
   - `study convert`: Convert DICOM files to BIDS format
   - `study show-save`: Save the output of study-show
   - `study show-summary`: Show summary information about a study
   - `study accession-skip`: Add an accession to the skip file
   - `study remove-subject`: Remove a subject from a study
   - `study remove-subject2redo`: Remove subject and add to skip file

3. **validate**: Commands for validating BIDS datasets
   - `validate run`: Run BIDS validator on a study
   - `validate save`: Run validator and save output to a file
   - `validate summary`: Show summary of validator errors and warnings
   - `validate show`: Show validator output in a pager

4. **setup**: Commands for setting up the study environment
   - `setup containers`: Set up containers for the study
   - `setup devel-reproin`: Set up development version of reproin

5. **reconvert**: Commands for reconverting data
   - `reconvert sourcedata`: Reconvert sourcedata for specific subject/session folders

## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`

## Testing

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest

# Run tests with verbose output
pytest -xvs

# Run tests with coverage
pytest --cov=reproin
```