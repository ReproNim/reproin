#!/bin/bash

HEUDICONV_DICOMDIR="/dicoms"
HEUDICONV_OUTDIR="/output"
HEUDICONV_XARGS=${HEUDICONV_XARGS:-""}
HEUDICONV_HISTORY="${HEUDICONV_OUTDIR}/.heudiconv.history"

set -eu

if [ ! -d ${HEUDICONV_DICOMDIR} ]; then
    echo "DICOM directory ${HEUDICONV_DICOMDIR} not properly set or mounted"
    exit 1
elif [ ! -d ${HEUDICONV_OUTDIR} ]; then
    echo "Output directory ${HEUDICONV_OUTDIR} not properly set or mounted"
    exit 1
elif [ ! -f ${HEUDICONV_HISTORY} ]; then
    touch ${HEUDICONV_HISTORY}
fi

for DICOMS in $(ls ${HEUDICONV_DICOMDIR}); do
   if grep "${DICOMS}" ${HEUDICONV_HISTORY} > /dev/null; then
      # existing conversion was found
      continue
   fi

   CMD="heudiconv -f reproin --bids --datalad -o ${HEUDICONV_OUTDIR}/${DICOMS} --files ${HEUDICONV_DICOMDIR}/${DICOMS} ${HEUDICONV_XARGS}"
   ${CMD}
done
