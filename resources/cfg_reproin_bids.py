#!/usr/bin/env python3
"""Procedure for default configuration of ReproIn BIDS dataset

It slightly diverges from original datalad-neuroimaging cfg_bids in
assuring that .heudiconv/ content (which might be subdataset or not)
would go under git-annex.
"""

import os
import sys
from pathlib import Path  # for compatibility with older DataLad lacking .pathobj
from datalad.consts import DATASET_CONFIG_FILE
from datalad.distribution.dataset import require_dataset
from datalad.support import path as op
from datalad.utils import ensure_tuple_or_list
#from datalad.support.external_versions import external_versions as ev

ds = require_dataset(
    sys.argv[1],
    check_installed=True,
    purpose='ReproIn BIDS dataset configuration')

# unless taken care of by the template already, each item in here
# will get its own .gitattributes entry to keep it out of the annex
# give relative path to dataset root (use platform notation)
force_in_git = [
    'README*',
    'CHANGES*',
    'dataset_description.json',
    '.bidsignore',
    'code/**',
    '*.tsv',
    '*.json',
    '*.txt',
]
# just to be sure + _scans.tsv could contain dates
force_in_annex = [
    '*.nii.gz',
    '*.tgz',
    '*_scans.tsv',
]
# make an attempt to discover the prospective change in .gitattributes
# to decide what needs to be done, and make this procedure idempotent
# (for simple cases)
attr_fpath = op.join(ds.path, '.gitattributes')
if op.lexists(attr_fpath):
    with open(attr_fpath, 'rb') as f:
        attrs = f.read().decode()
else:
    attrs = ''

for paths, largefile in [
        (force_in_git, 'nothing'),
        (force_in_annex, 'anything'),
        # not sufficient since order matters (last match wins) and 
        # heudiconv ATM also would add a line
        # for * and base on the size and also the one for _scans.tsv
        # so we end up with _scans.tsv, small they are, being added
        # to git.... TODO: fix in heudiconv
    ]:
    # amend gitattributes, if needed
    ds.repo.set_gitattributes([
        (path, {'annex.largefiles': largefile})
        for path in paths
        if '{} annex.largefiles={}'.format(path, largefile) not in attrs
    ])


def add_line_to_file(subpath, line):
    pathobj = Path(ds.path)
    f = pathobj / subpath
    if not f.parent.exists():
        f.parent.mkdir()
    content = f.read_text().split(os.linesep) if f.exists() else []
    if line not in content:
        f.write_text(os.linesep.join(content + [line]))


# Everything under .heudiconv should go into annex.
# But it might be a subdataset or not, so we will
# just adjust it directly
for l in [
    "* annex.largefiles=anything",
    "**/.git* annex.largefiles=nothing",
    ]:
    add_line_to_file(
        op.join(".heudiconv", ".gitattributes"),
        l)
    
add_line_to_file(
    op.join(".heudiconv", ".gitignore"),
    "*.pyc")

# leave clean
ds.save(
    path=['.gitattributes',
          op.join(".heudiconv", ".gitattributes"),
          op.join(".heudiconv", ".gitignore")],
    message="Apply default ReproIn BIDS dataset setup",
)

existing_types = ensure_tuple_or_list(
    ds.config.get('datalad.metadata.nativetype', [], get_all=True))
for nt in 'bids', 'nifti1':
    if nt in existing_types:
        # do not duplicate
        continue
    ds.config.add(
        'datalad.metadata.nativetype',
        nt,
        scope='branch',
        reload=False)

ds.save(
    path=op.join(ds.path, DATASET_CONFIG_FILE),
    message="Configure metadata type(s)",
    result_renderer='disabled'
)
