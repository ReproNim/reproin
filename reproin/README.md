# ReproIn Python CLI

This is a refactored Python-based version of the ReproIn command-line tool, originally written in Bash.

## Features

- Modern Python CLI built with Click
- Maintains compatibility with the original ReproIn bash script
- Organized code structure with modular commands
- Improved error handling and logging

## Installation

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

## Usage

The `reproin` command provides the following functionality:

```bash
# Show version information
reproin

# Show help
reproin --help

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
```

### Legacy Command Support

All original commands from the bash script are supported with the same syntax:

```bash
reproin lists-update
reproin study-create <study>
reproin study-convert <study>
```

## Configuration

The tool uses environment variables for configuration:

- `DICOM_DIR`: Directory containing DICOM files (default: `/inbox/DICOM`)
- `BIDS_DIR`: Directory for BIDS output (default: `/inbox/BIDS`)
- `REPRONIM_CONTAINERS`: Path to local ReproNim containers (default: `~/repronim-containers`)

## Project Structure

```
reproin/
├── reproin/
│   ├── __init__.py
│   ├── cli.py            # Main CLI entry point
│   ├── config.py         # Configuration handling
│   ├── utils.py          # Utility functions
│   ├── commands/         # Command implementations
│   │   ├── __init__.py
│   │   ├── lists.py      # Lists and accessions commands
│   │   ├── study.py      # Study management commands
│   │   ├── validator.py  # BIDS validation commands
│   │   ├── reconvert.py  # Commands for reconverting data
│   │   └── accessions.py # Accession management commands
│   └── resources/        # Static resources
├── tests/
│   ├── test_basic.py     # Basic unit tests
│   └── test_cli.py       # CLI interface tests
├── setup.py              # Package setup
├── pyproject.toml        # Python project configuration
└── MANIFEST.in           # Package manifest
```

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
```