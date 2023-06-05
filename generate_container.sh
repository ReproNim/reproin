#!/bin/bash

set -eu

# Either to build against to-be-released heudiconv
dev_build=

generate() {
	if [ "$dev_build" = "1" ]; then
		apt_pkgs=python3-pip
		run_cmd="pip install git+https://github.com/nipy/heudiconv@master"
	else
		apt_pkgs="heudiconv=0.13.1-1~nd120+1"
		run_cmd=":"
	fi
	# more details might come on https://github.com/ReproNim/neurodocker/issues/330
	[ "$1" == singularity ] && add_entry=' "$@"' || add_entry=''
	#neurodocker generate "$1" \
	ndversion=0.7.0
	#ndversion=master
	docker run --rm repronim/neurodocker:$ndversion generate "$1" \
		--base=neurodebian:bookworm \
		--ndfreeze date=20230604 \
		--pkg-manager=apt \
		--install vim wget strace time ncdu gnupg curl procps datalad pigz less tree \
				  git-annex python3-nibabel \
				  python3-nipype virtualenv shellcheck \
				  python3-dcmstack python3-funcsigs python3-etelemetry \
				  python3-pytest dcmtk python3-pip python3-wheel \
				  python3-setuptools python3-datalad python3-filelock \
				  dcm2niix python3-pytest python3-nose python3-venv $apt_pkgs \
		--run "$run_cmd" \
		--run "apt-get update && apt-get -y dist-upgrade" \
		--run "curl -sL https://deb.nodesource.com/setup_16.x | bash - " \
		--install nodejs npm \
		--run "npm install -g bids-validator@1.11.0" \
		--run "mkdir /afs /inbox" \
		--copy bin/reproin /usr/local/bin/reproin \
		--run "chmod a+rx /usr/local/bin/reproin" \
		--user=reproin \
		--entrypoint "/usr/local/bin/reproin$add_entry"
}

generate docker > Dockerfile
generate singularity > Singularity
