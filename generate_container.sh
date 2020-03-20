#!/bin/bash

set -eu

# Either to build against to-be-released heudiconv
dev_build=

generate() {
	if [ "$dev_build" = "1" ]; then
		apt_pkgs=python-pip
		run_cmd="pip install git+https://github.com/nipy/heudiconv@master"
	else
		apt_pkgs=heudiconv
		run_cmd=":"
	fi
	#neurodocker generate "$1" \
	docker run --rm kaczmarj/neurodocker:master generate "$1" \
		--base=neurodebian:buster \
		--pkg-manager=apt \
		--ndfreeze date=20191217 \
		--install vim wget strace time ncdu gnupg curl procps datalad pigz less tree \
				  git-annex-standalone python-nipype virtualenv shellcheck \
				  python-dcmstack python-configparser python-funcsigs \
				  python-pytest dcmtk python-pip python-wheel \
				  python-setuptools python-datalad python-filelock \
				  dcm2niix python-pytest python3-pytest python3-nose $apt_pkgs \
		--run "$run_cmd" \
		--run "curl -sL https://deb.nodesource.com/setup_6.x | bash - " \
		--install nodejs npm \
		--run "npm install -g bids-validator@1.3.12" \
		--run "mkdir /afs /inbox" \
		--run "echo '#!/bin/bash' >> /neurodocker/heudiconv.sh && echo 'set -eu; heudiconv \"\$@\"' >> /neurodocker/heudiconv.sh && chmod +x /neurodocker/heudiconv.sh" \
		--user=reproin \
		--entrypoint '/neurodocker/heudiconv.sh "$@"'
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
