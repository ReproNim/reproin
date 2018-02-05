# ReproIn

This project is a part of the ReproNim.org suite.  Its goal is to provide a
turnkey flexible setup for automatic generation of shareable,
version-controlled BIDS datasets from MR scanners.  To not reinvent the wheel,
all actual software development is largely done through contribution to
existing software projects:

- [HeuDiConv](https://github.com/nipy/heudiconv) -
  a flexible DICOM converter for organizing brain imaging data into structured
  directory layouts.
  ReproIn [heuristic] was developed and now is shipped within HeuDiConv,
  so it could be used independently of the ReproIn setup on any HeuDiConv
  installation (specify `-f reproin` to heudiconv call).
- [DataLad](http://datalad.org):
  a modular version control platform and distribution for both code and
  data.  DataLad support was contributed to HeuDiConv, and could be
  enabled by adding `--datalad` option to the `heudiconv` call.

The recommended invocation for the heudiconv is

```shell
$ heudiconv -c dcm2niix -f reproin --bids --datalad -o OUTPUT --files INPUT
```
to convert all found in `INPUT` DICOMs and place then within the
hierarchy of DataLad datasets rooted at `OUTPUT`.

## Specification

The header of the [heuristic] file describes details of the
specification on how to organize and name study sequences at MR console.

## Sample converted datasets

You could find sample datasets with original DICOMs

- [///dbic/QA](http://datasets.datalad.org/?dir=/dbic/QA) is a publicly
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

## Containers

This repository provides a [Singularity](./Singualarity) environment
definition file used to generate a complete environment needed to run
a conversion

## TODOs/WiP

- [ ] adding pre-configured DICOM received for fully turnkey deployments
- [ ] [heudiconv-monitor] to fully automate conversion of the incoming
      data
- [ ] [BIDS dataset manipulation helper](https://github.com/INCF/bidsutils/issues/6)

[heuristic]: https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/reproin.py
[heudiconv-monitor]: https://github.com/nipy/heudiconv/blob/master/heudiconv/cli/monitor.py