[![DOI](https://zenodo.org/badge/120343858.svg)](https://zenodo.org/badge/latestdoi/120343858)

# ReproIn

This project is a part of the [ReproNim Center](http://ReproNim.org)
suite of tools and frameworks.  Its goal is to provide a
turnkey flexible setup for automatic generation of shareable,
version-controlled BIDS datasets from MR scanners.  To not reinvent the wheel,
all actual software development is largely done through contribution to
existing software projects:

- [HeuDiConv]:
  a flexible DICOM converter for organizing brain imaging data into structured
  directory layouts.
  ReproIn [heuristic] was developed and now is shipped within HeuDiConv,
  so it could be used independently of the ReproIn setup on any HeuDiConv
  installation (specify `-f reproin` to heudiconv call).
- [DataLad]:
  a modular version control platform and distribution for both code and
  data.  DataLad support was contributed to HeuDiConv, and could be
  enabled by adding `--datalad` option to the `heudiconv` call.

## Specification

The header of the [heuristic] file describes details of the
specification on how to organize and name study sequences at MR console.

## Overall workflow

Schematic description of the overall setup:

![Setup](docs/source/images/dbic-flow.png)

**Note:** for your own setup, [dcm2niix](https://github.com/rordenlab/dcm2niix)
[author](https://github.com/neurolabusc)
[recommends](https://github.com/neurolabusc/dcm_qa_agfa) to avoid dcm4che and
choose another PACS.

![Setup](docs/source/images/dbic-conversions.png)

## Tutorial/HOWTO

### Data collection

#### Making your sequence compatible with ReproIn heuristic

- [Walkthrough #1](docs/walkthrough-1.md): guides you through
ReproIn approach to organizing exam cards and managing canceled runs/sessions
on Siemens scanner(s)

#### Renaming sequences to conform the specification needed by ReproIn

TODO: Describe how sequences could be renamed per study by creating a derived
heuristic

### Conversion

1. Install [HeuDiConv] and [DataLad]: e.g.
   `apt-get update; apt-get install heudiconv datalad` in any NeuroDebian environment.
   If you do not have one, you could get either of
   - [NeuroDebian Virtual Machine](http://neuro.debian.net/vm.html)
   - ReproIn Docker image: `docker run -it --rm -v $PWD:$PWD repronim/reproin`
   - ReproIn Singularity image: you can either
     - convert from the docker image: `singularity pull docker://repronim/reproin`
     - download the most recent version from
       http://datasets.datalad.org/?dir=/repronim/containers/images/repronim
	   which is a DataLad dataset which you can install via `datalad install ///repronim/containers`
       (see/subscribe https://github.com/ReproNim/reproin/issues/64
       for HOWTO setup YODA style dataset)
2. Collect a subject/session (or multiple of them) while placing and
   naming sequences in the scanner following the [specification].
   But for now we will assume that you have no such dataset yet, and
   want to try on phantom data:

        datalad install -J3 -r -g ///dicoms/dartmouth-phantoms/bids_test4-20161014

   to get all subdatasets recursively, while getting the data as well
   in parallel 3 streams.
   This dataset is a sample of multi-session acquisition with anatomicals and
   functional sequences on a friendly phantom impersonating two different
   subjects (note: fieldmaps were deficient, without magnitude images).
   You could also try other datasets such as [///dbic/QA]

3. We are ready to convert all the data at once (heudiconv will sort
   into accessions) or one accession at a time.
   The recommended invocation for the heudiconv is

        heudiconv -f reproin --bids --datalad -o OUTPUT --files INPUT

   to convert all found in `INPUT` DICOMs and place then within the
   hierarchy of DataLad datasets rooted at `OUTPUT`.  So we will start
   with a single accession of `phantom-1/`

        heudiconv -f reproin --bids --datalad -o OUTPUT --files bids_test4-20161014/phantom-1

   and inspect the result under OUTPUT, probably best with `datalad ls`
   command:

        ... WiP ...



#### HeuDiConv options to overload autodetected variables:

- `--subject`
- `--session`
- `--locator`



## Sample converted datasets

You could find sample datasets with original DICOMs

- [///dbic/QA] is a publicly
  available DataLad dataset with historical data on QA scans from DBIC.
  You could use DICOM tarballs under `sourcedata/` for your sample
  conversions.
  TODO: add information from which date it is with scout DICOMs having
  session identifier
- [///dicoms/dartmouth-phantoms](http://datasets.datalad.org/?dir=/dicoms/dartmouth-phantoms)
  provides a collection of datasets acquired at [DBIC] to establish
  ReproIn specification.  Some earlier accessions might not be following
  the specification.
  [bids_test4-20161014](http://datasets.datalad.org/?dir=/dicoms/dartmouth-phantoms/bids_test4-20161014)
  provides a basic example of multi-subject and multi-session acquisition.

## Containers/Images etc

This repository provides a [Singularity](./Singularity) environment
definition file used to generate a complete environment needed to run
a conversion.  But also, since all work is integrated within the
tools, any environment providing them would suffice, such as
[NeuroDebian](https://neuro.debian.net) docker or Singularity images, virtual appliances, and
other Debian-based systems with NeuroDebian repositories configured,
which would provide all necessary for ReproIn setup components.

## Gotchas


## Complete setup at DBIC

It relies on the hardcoded ATM in `reproin` locations and organization
of DICOMs and location of where to keep converted BIDS datasets.

- `/inbox/DICOM/{YEAR}/{MONTH}/{DAY}/A00{ACCESSION}`
- `/inbox/BIDS/{PI}/{RESEARCHER}/{ID}_{name}/`

### Cron job

```
# m h  dom mon dow   command
55 */12 * * * $HOME/reproin-env-0.9.0 -c '~/proj/reproin/bin/reproin lists-update-study-shows' && curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/61dfdedd-SENSORED
```

NB: that `curl` at the end is to make use of https://healthchecks.io
to ensure that we do have CRON job ran as we expected.

ATM we reuse a singularity environment based on reproin 0.9.0 produced from this repo and shipped within ReproNim/containers. For the completeness sake

```shell
(reproin-3.8) [bids@rolando lists] > cat $HOME/reproin-env-0.9.0
#!/bin/sh

env -i /usr/local/bin/singularity exec -B /inbox -B /afs -H $HOME/singularity_home $(dirname $0)/reproin_0.9.0.simg /bin/bash "$@"
```

which produces emails with content like

```
Wager/Wager/1102_MedMap: new=92 todo=5 done=102 /inbox/BIDS/Wager/Wager/1102_MedMap/.git/study-show.sh 2023-03-30
PI/Researcher/ID_name: new=32 no studydir yet
Haxby/Jane/1073_MonkeyKingdom: new=4 todo=39 done=8  fixups=6 /inbox/BIDS/Haxby/Jane/1073_MonkeyKingdom/.git/study-show.sh 2023-03-30
```

where as you can see it updates on the status for each study which was scanned for from the
beginning of the current month. And it ends with the pointer to `study-show.sh` script which
would provide details on already converted or heudiconv line invocations for what yet to do.

### reproin study-create

For the "no studydir yet" we need first to generate study dataset (and
possibly all leading `PI/Researcher` super-datasets via 

```shell
reproin study-create PI/Researcher/ID_name
```

### reproin study-convert

Unless there are some warnings/conflicts (subject/session already
converted, etc) are found,

```shell
reproin study-convert PI/Researcher/ID_name
```

could be used to convert all new subject/sessions for that study.

### XNAT

Anonymization or other scripts might obfuscate "Study Description" thus ruining
"locator" assignment.  See 
[issue #57](https://github.com/ReproNim/reproin/issues/57) for more information.

## TODOs/WiP/Related

- [ ] add a pre-configured DICOM receiver for fully turnkey deployments
- [ ] [heudiconv-monitor] to fully automate conversion of the incoming
      data
- [ ] [BIDS dataset manipulation helper](https://github.com/INCF/bidsutils/issues/6)

[HeuDiConv]: https://github.com/nipy/heudiconv
[DataLad]: http://datalad.org
[heuristic]: https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py
[specification]: https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py
[heudiconv-monitor]: https://github.com/nipy/heudiconv/blob/master/heudiconv/cli/monitor.py
[DBIC]: http://dbic.dartmouth.edu
[///dbic/QA]: http://datasets.datalad.org/?dir=/dbic/QA
