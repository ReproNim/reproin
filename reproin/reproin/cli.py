"""Command line interface for ReproIn."""

import os
import sys
import datetime
import click

from .config import Config
from .utils import get_dcm2niix_version, get_heudiconv_version
from .commands.lists import lists_update, lists_check, lists_update_summary, lists_update_study_shows
from .commands.study import (
    study_create, study_show, study_convert, study_show_save, study_show_summary,
    setup_containers, setup_devel_reproin
)
from .commands.validator import validator, validator_save, validator_summary, validator_show


# Initialize configuration
config = Config()


@click.group()
@click.version_option()
def main():
    """ReproIn - automatic generation of shareable BIDS datasets from MR scanners."""
    # Update configuration from environment variables
    config.update_from_env()
    
    # If no arguments, show version information
    if len(sys.argv) == 1:
        heudiconv_version = get_heudiconv_version() or "unknown"
        dcm2niix_version = get_dcm2niix_version() or "unknown"
        click.echo(f"heudiconv: {heudiconv_version}")
        click.echo(f"dcm2niix: {dcm2niix_version}")
        return


# Lists commands
@main.group()
def lists():
    """Commands for managing lists of studies and accessions."""
    pass


@lists.command("update")
@click.argument("year", required=False, default=lambda: datetime.datetime.now().strftime("%Y"))
@click.argument("month", required=False, default=lambda: datetime.datetime.now().strftime("%m"))
@click.argument("day", required=False, default="*")
def lists_update_cmd(year, month, day):
    """Update the list of studies and accessions."""
    lists_update(config, year, month, day)


@lists.command("check")
@click.argument("year", required=False, default="20??")
@click.argument("month", required=False, default="??")
def lists_check_cmd(year, month):
    """Check if there are any accessions that are not in the lists."""
    exit_code = lists_check(config, year, month)
    sys.exit(exit_code)


@lists.command("update-summary")
def lists_update_summary_cmd():
    """Extract and summarize locator values from lists."""
    lists_update_summary(config)


@lists.command("update-study-shows")
def lists_update_study_shows_cmd():
    """Update lists and show study information."""
    lists_update_study_shows(config)


# Study commands
@main.group()
def study():
    """Commands for managing studies."""
    pass


@study.command("create")
@click.argument("study")
def study_create_cmd(study):
    """Create a new study directory."""
    exit_code = study_create(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@study.command("show")
@click.argument("study")
@click.argument("target_sub", required=False)
def study_show_cmd(study, target_sub):
    """Show information about a study."""
    exit_code = study_show(config, study, target_sub)
    if exit_code != 0:
        sys.exit(exit_code)


@study.command("convert")
@click.argument("study")
@click.argument("target_sub", required=False)
def study_convert_cmd(study, target_sub):
    """Convert a study's DICOM files to BIDS format."""
    exit_code = study_convert(config, study, target_sub)
    if exit_code != 0:
        sys.exit(exit_code)


@study.command("show-save")
@click.argument("study")
def study_show_save_cmd(study):
    """Save the output of study-show."""
    exit_code = study_show_save(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@study.command("show-summary")
@click.argument("study")
def study_show_summary_cmd(study):
    """Show summary information about a study."""
    exit_code = study_show_summary(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


# Setup commands
@main.command("setup-containers")
def setup_containers_cmd():
    """Set up containers for the study."""
    exit_code = setup_containers(config)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("setup-devel-reproin")
def setup_devel_reproin_cmd():
    """Set up development version of reproin."""
    exit_code = setup_devel_reproin(config)
    if exit_code != 0:
        sys.exit(exit_code)


# Validator commands
@main.group()
def validate():
    """Commands for validating BIDS datasets."""
    pass


@validate.command("run")
@click.argument("study", required=False)
def validator_cmd(study):
    """Run BIDS validator on a study."""
    exit_code = validator(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@validate.command("save")
@click.argument("study")
def validator_save_cmd(study):
    """Run validator and save output to a file."""
    exit_code = validator_save(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@validate.command("summary")
@click.argument("study")
def validator_summary_cmd(study):
    """Show summary of validator errors and warnings."""
    exit_code = validator_summary(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@validate.command("show")
@click.argument("study")
def validator_show_cmd(study):
    """Show validator output in a pager."""
    exit_code = validator_show(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


# Legacy command aliases
@main.command("lists-update")
@click.argument("year", required=False, default=lambda: datetime.datetime.now().strftime("%Y"))
@click.argument("month", required=False, default=lambda: datetime.datetime.now().strftime("%m"))
@click.argument("day", required=False, default="*")
def lists_update_legacy(year, month, day):
    """Update the list of studies and accessions (legacy command)."""
    lists_update(config, year, month, day)


@main.command("lists-check")
@click.argument("year", required=False, default="20??")
@click.argument("month", required=False, default="??")
def lists_check_legacy(year, month):
    """Check if there are any accessions that are not in the lists (legacy command)."""
    exit_code = lists_check(config, year, month)
    sys.exit(exit_code)


@main.command("lists-update-summary")
def lists_update_summary_legacy():
    """Extract and summarize locator values from lists (legacy command)."""
    lists_update_summary(config)


@main.command("lists-update-study-shows")
def lists_update_study_shows_legacy():
    """Update lists and show study information (legacy command)."""
    lists_update_study_shows(config)


@main.command("study-create")
@click.argument("study")
def study_create_legacy(study):
    """Create a new study directory (legacy command)."""
    exit_code = study_create(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-show")
@click.argument("study")
@click.argument("target_sub", required=False)
def study_show_legacy(study, target_sub):
    """Show information about a study (legacy command)."""
    exit_code = study_show(config, study, target_sub)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-convert")
@click.argument("study")
@click.argument("target_sub", required=False)
def study_convert_legacy(study, target_sub):
    """Convert a study's DICOM files to BIDS format (legacy command)."""
    exit_code = study_convert(config, study, target_sub)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-show-save")
@click.argument("study")
def study_show_save_legacy(study):
    """Save the output of study-show (legacy command)."""
    exit_code = study_show_save(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-show-summary")
@click.argument("study")
def study_show_summary_legacy(study):
    """Show summary information about a study (legacy command)."""
    exit_code = study_show_summary(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator")
@click.argument("study", required=False)
def validator_legacy(study):
    """Run BIDS validator on a study (legacy command)."""
    exit_code = validator(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator-save")
@click.argument("study")
def validator_save_legacy(study):
    """Run validator and save output to a file (legacy command)."""
    exit_code = validator_save(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator-summary")
@click.argument("study")
def validator_summary_legacy(study):
    """Show summary of validator errors and warnings (legacy command)."""
    exit_code = validator_summary(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator-show")
@click.argument("study")
def validator_show_legacy(study):
    """Show validator output in a pager (legacy command)."""
    exit_code = validator_show(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()