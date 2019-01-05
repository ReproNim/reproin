#!/bin/bash

generate() {
  #neurodocker generate "$1" \
  docker run --rm kaczmarj/neurodocker:master generate "$1" \
    --base=neurodebian:stretch \
    --pkg-manager=apt \
    --install vim wget strace time ncdu gnupg curl procps datalad pigz \
              git-annex-standalone python-nipype virtualenv \
              python-dcmstack python-configparser python-funcsigs \
              python-pytest dcmtk python-pip python-wheel python-setuptools python-datalad \
    --run "curl -sL https://deb.nodesource.com/setup_6.x | bash - "\
    --install nodejs npm \
    --run "npm install -g bids-validator@1.1.1" \
    --run "mkdir /afs /inbox" \
    --run "pip install heudiconv" \
    --dcm2niix version="v1.0.20181125" method="source" \
    --run "echo '#!/bin/bash' >> /neurodocker/heudiconv.sh && echo 'heudiconv \"\$@\"' >> /neurodocker/heudiconv.sh && chmod +x /neurodocker/heudiconv.sh" \
    --user=reproin \
    --entrypoint "/neurodocker/heudiconv.sh"
}

generate docker > Dockerfile
generate singularity > Singularity
