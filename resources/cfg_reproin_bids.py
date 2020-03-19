"""Procedure to apply a sensible BIDS default setup to a dataset
"""

import sys
from datalad.distribution.dataset import require_dataset
from datalad.support import path as op

ds = require_dataset(
    sys.argv[1],
    check_installed=True,
    purpose='BIDS dataset configuration')

# unless taken care of by the template already, each item in here
# will get its own .gitattributes entry to keep it out of the annex
# give relative path to dataset root (use platform notation)
force_in_git = [
    'README',
    'CHANGES',
    'dataset_description.json',
    '.bidsignore',
    'code/**',
    # to not put participants or scan info into Git, might contain sensitive
    # information
    #'*.tsv',
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

# amend gitattributes, if needed
ds.repo.set_gitattributes([
    (path, {'annex.largefiles': 'nothing'})
    for path in force_in_git
    if '{} annex.largefiles=nothing'.format(path) not in attrs
])

# leave clean
ds.save(
    path=['.gitattributes'],
    message="Apply default BIDS dataset setup",
    to_git=True,
)

# run metadata type config last, will do another another commit
ds.run_procedure(
    spec=['cfg_metadatatypes', 'bids', 'nifti1'],
)
