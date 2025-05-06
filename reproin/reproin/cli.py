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
from .commands.reconvert import reconvert_sourcedata
from .commands.accessions import study_accession_skip, study_remove_subject, study_remove_subject2redo


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
    if exit_code != 0:
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


@study.command("accession-skip")
@click.argument("study")
@click.argument("accession")
@click.argument("reason", required=False)
def study_accession_skip_cmd(study, accession, reason=None):
    """Add an accession to the skip file."""
    exit_code = study_accession_skip(config, study, accession, reason)
    if exit_code != 0:
        sys.exit(exit_code)


@study.command("remove-subject")
@click.argument("study")
@click.argument("sid")
@click.argument("session", required=False)
def study_remove_subject_cmd(study, sid, session=None):
    """Remove a subject from a study."""
    exit_code = study_remove_subject(config, study, sid, session)
    if exit_code != 0:
        sys.exit(exit_code)


@study.command("remove-subject2redo")
@click.argument("study")
@click.argument("sid")
@click.argument("session", required=False)
def study_remove_subject2redo_cmd(study, sid, session=None):
    """Remove a subject from a study and add to skip file to redo later."""
    exit_code = study_remove_subject2redo(config, study, sid, session)
    if exit_code != 0:
        sys.exit(exit_code)


# Reconvert commands
@main.group()
def reconvert():
    """Commands for reconverting data."""
    pass


@reconvert.command("sourcedata")
@click.argument("paths", nargs=-1, required=True)
def reconvert_sourcedata_cmd(paths):
    """Reconvert sourcedata for specific subject/session folders."""
    exit_code = reconvert_sourcedata(config, paths)
    if exit_code != 0:
        sys.exit(exit_code)


# Setup commands
@main.group()
def setup():
    """Commands for setting up the study environment."""
    pass


@setup.command("containers")
def setup_containers_cmd():
    """Set up containers for the study."""
    exit_code = setup_containers(config)
    if exit_code != 0:
        sys.exit(exit_code)


@setup.command("devel-reproin")
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


# Maintain legacy command aliases for backward compatibility
@main.command("lists-update", hidden=True)
@click.argument("year", required=False, default=lambda: datetime.datetime.now().strftime("%Y"))
@click.argument("month", required=False, default=lambda: datetime.datetime.now().strftime("%m"))
@click.argument("day", required=False, default="*")
def lists_update_legacy(year, month, day):
    """Update the list of studies and accessions (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin lists update' instead")
    lists_update(config, year, month, day)


@main.command("lists-check", hidden=True)
@click.argument("year", required=False, default="20??")
@click.argument("month", required=False, default="??")
def lists_check_legacy(year, month):
    """Check if there are any accessions that are not in the lists (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin lists check' instead")
    exit_code = lists_check(config, year, month)
    sys.exit(exit_code)


@main.command("lists-update-summary", hidden=True)
def lists_update_summary_legacy():
    """Extract and summarize locator values from lists (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin lists update-summary' instead")
    lists_update_summary(config)


@main.command("lists-update-study-shows", hidden=True)
def lists_update_study_shows_legacy():
    """Update lists and show study information (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin lists update-study-shows' instead")
    lists_update_study_shows(config)


@main.command("study-create", hidden=True)
@click.argument("study")
def study_create_legacy(study):
    """Create a new study directory (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study create' instead")
    exit_code = study_create(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-show", hidden=True)
@click.argument("study")
@click.argument("target_sub", required=False)
def study_show_legacy(study, target_sub):
    """Show information about a study (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study show' instead")
    exit_code = study_show(config, study, target_sub)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-convert", hidden=True)
@click.argument("study")
@click.argument("target_sub", required=False)
def study_convert_legacy(study, target_sub):
    """Convert a study's DICOM files to BIDS format (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study convert' instead")
    exit_code = study_convert(config, study, target_sub)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-show-save", hidden=True)
@click.argument("study")
def study_show_save_legacy(study):
    """Save the output of study-show (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study show-save' instead")
    exit_code = study_show_save(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-show-summary", hidden=True)
@click.argument("study")
def study_show_summary_legacy(study):
    """Show summary information about a study (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study show-summary' instead")
    exit_code = study_show_summary(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator", hidden=True)
@click.argument("study", required=False)
def validator_legacy(study):
    """Run BIDS validator on a study (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin validate run' instead")
    exit_code = validator(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator-save", hidden=True)
@click.argument("study")
def validator_save_legacy(study):
    """Run validator and save output to a file (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin validate save' instead")
    exit_code = validator_save(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator-summary", hidden=True)
@click.argument("study")
def validator_summary_legacy(study):
    """Show summary of validator errors and warnings (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin validate summary' instead")
    exit_code = validator_summary(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("validator-show", hidden=True)
@click.argument("study")
def validator_show_legacy(study):
    """Show validator output in a pager (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin validate show' instead")
    exit_code = validator_show(config, study)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("reconvert-sourcedata", hidden=True)
@click.argument("paths", nargs=-1, required=True)
def reconvert_sourcedata_legacy(paths):
    """Reconvert sourcedata for specific subject/session folders (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin reconvert sourcedata' instead")
    exit_code = reconvert_sourcedata(config, paths)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("setup-containers", hidden=True)
def setup_containers_legacy():
    """Set up containers for the study (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin setup containers' instead")
    exit_code = setup_containers(config)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("setup-devel-reproin", hidden=True)
def setup_devel_reproin_legacy():
    """Set up development version of reproin (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin setup devel-reproin' instead")
    exit_code = setup_devel_reproin(config)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-accession-skip", hidden=True)
@click.argument("study")
@click.argument("accession")
@click.argument("reason", required=False)
def study_accession_skip_legacy(study, accession, reason=None):
    """Add an accession to the skip file (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study accession-skip' instead")
    exit_code = study_accession_skip(config, study, accession, reason)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-remove-subject", hidden=True)
@click.argument("study")
@click.argument("sid")
@click.argument("session", required=False)
def study_remove_subject_legacy(study, sid, session=None):
    """Remove a subject from a study (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study remove-subject' instead")
    exit_code = study_remove_subject(config, study, sid, session)
    if exit_code != 0:
        sys.exit(exit_code)


@main.command("study-remove-subject2redo", hidden=True)
@click.argument("study")
@click.argument("sid")
@click.argument("session", required=False)
def study_remove_subject2redo_legacy(study, sid, session=None):
    """Remove a subject from a study and add to skip file to redo later (legacy command)."""
    click.echo("DEPRECATED: Use 'reproin study remove-subject2redo' instead")
    exit_code = study_remove_subject2redo(config, study, sid, session)
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()