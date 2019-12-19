#!/bin/bash
#emacs: -*- mode: shell-script; c-basic-offset: 4; tab-width: 4; indent-tabs-mode: t -*- 
#ex: set sts=4 ts=4 sw=4 noet:
#
# A sample script to test correct operation for a prototypical/recommended
# setup etc
#
# COPYRIGHT: Yaroslav Halchenko 2019
#
# LICENSE: MIT
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#

set -eu

INPUT=( ~/datalad/dbic/QA/sourcedata/sub-qa/ses-20180904/ )

STUDY=$(mktemp -u /tmp/reproin.XXXXXX)

#HEUDICONV=datalad containers-run containers/reproin

# This a study oriented scenario.  Will override
# --locator

# requires datalad >= 0.12b*
datalad create -c text2git "$STUDY"
# requires datalad-neuroimaging
datalad create -c bids -d "$STUDY" "$STUDY/data/bids"

# Reuse our containers collection
# datalad install -d $STUDY/data/bids -s ///repronim/containers .containers

cd "$STUDY/data/bids"
HEUDICONV="docker run -it --workdir $PWD -v $HOME/datalad:$HOME/datalad -v $PWD:$PWD -u $(id -u):$(id -g) -e HOME=$HOME -v $HOME:$HOME 723a01d04689"

$HEUDICONV -f reproin --bids --datalad -o . --files "${INPUT[@]}"
