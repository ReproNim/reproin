#!/bin/bash

set -eu

# Either to build against to-be-released heudiconv
dev_build=

generate() {
	if [ "$dev_build" = "1" ]; then
		apt_pkgs=python3-pip
		run_cmd="pip install git+https://github.com/nipy/heudiconv@master"
	else
		apt_pkgs="heudiconv=0.8.0-2~nd100+1"
		run_cmd=":"
	fi
	# more details might come on https://github.com/ReproNim/neurodocker/issues/330
	[ "$1" == singularity ] && add_entry=' "$@"' || add_entry=''
	#neurodocker generate "$1" \
	ndversion=0.7.0
	#ndversion=master
	docker run --rm repronim/neurodocker:$ndversion generate "$1" \
		--base=neurodebian:buster \
	    --ndfreeze date=20200421 \
		--pkg-manager=apt \
		--install vim wget strace time ncdu gnupg curl procps datalad pigz less tree \
				  git-annex-standalone python3-nipype virtualenv shellcheck \
				  python3-dcmstack python3-funcsigs python3-etelemetry \
				  python3-pytest dcmtk python3-pip python3-wheel \
				  python3-setuptools python3-datalad python3-filelock \
				  dcm2niix python3-pytest python3-nose $apt_pkgs \
		--run "$run_cmd" \
		--run "curl -sL https://deb.nodesource.com/setup_9.x | bash - " \
		--install nodejs npm \
		--run "npm install -g bids-validator@1.5.1" \
		--run "mkdir /afs /inbox" \
		--user=reproin \
		--entrypoint "/usr/bin/heudiconv$add_entry"
}

version=$(git describe)

generate docker > Dockerfile
generate singularity > Singularity

# Make versioned copy for Singularity Hub
cp Singularity Singularity.${version}

if [ "$dev_build" != "1" ] && echo $version | grep -e '-g'; then
	echo "ERROR: Evil Yarik disabled updates of the containers without releases"
	echo "		 So this command will 'fail', and if output is alright, reset, tag "
	echo "		 (should match frozen version of heudiconv) and redo"
	exit 1
fi
