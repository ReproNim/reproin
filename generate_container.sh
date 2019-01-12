#!/bin/bash

set -eu

generate() {
  #neurodocker generate "$1" \
  docker run --rm kaczmarj/neurodocker:0.4.3 generate "$1" \
    --base=neurodebian:stretch \
    --pkg-manager=apt \
    --ndfreeze date=20190112 \
    --install vim wget strace time ncdu gnupg curl procps datalad pigz \
              git-annex-standalone python-nipype virtualenv \
              python-dcmstack python-configparser python-funcsigs \
              python-pytest dcmtk python-pip python-wheel python-setuptools python-datalad \
              heudiconv dcm2niix \
    --run "curl -sL https://deb.nodesource.com/setup_6.x | bash - "\
    --install nodejs npm \
    --run "npm install -g bids-validator@1.1.1" \
    --run "mkdir /afs /inbox" \
    --run "echo '#!/bin/bash' >> /neurodocker/heudiconv.sh && echo 'heudiconv \"\$@\"' >> /neurodocker/heudiconv.sh && chmod +x /neurodocker/heudiconv.sh" \
    --user=reproin \
    --entrypoint "/neurodocker/heudiconv.sh"
}

version=$(git describe)

generate docker > Dockerfile
generate singularity > Singularity

# Make versioned copy for Singularity Hub
cp Singularity Singularity.${version}

if echo $version | grep -e '-g'; then
    echo "ERROR: Evil Yarik disabled updates of the containers without releases"
    echo "       So this command will 'fail', and if output is alright, reset, tag "
    echo "       (should match frozen version of heudiconv) and redo"
    exit 1
fi
