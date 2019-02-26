# Generated by Neurodocker version 0.4.3-2-g01cdd22
# Timestamp: 2019-02-26 20:19:06 UTC
# 
# Thank you for using Neurodocker. If you discover any issues
# or ways to improve this software, please submit an issue or
# pull request on our GitHub repository:
# 
#     https://github.com/kaczmarj/neurodocker

Bootstrap: docker
From: neurodebian:stretch

%post
apt-get update -qq
apt-get install -y -q --no-install-recommends \
    neurodebian-freeze
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
nd_freeze  20190225

export ND_ENTRYPOINT="/neurodocker/startup.sh"
apt-get update -qq
apt-get install -y -q --no-install-recommends \
    apt-utils \
    bzip2 \
    ca-certificates \
    curl \
    locales \
    unzip
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
dpkg-reconfigure --frontend=noninteractive locales
update-locale LANG="en_US.UTF-8"
chmod 777 /opt && chmod a+s /opt
mkdir -p /neurodocker
if [ ! -f "$ND_ENTRYPOINT" ]; then
  echo '#!/usr/bin/env bash' >> "$ND_ENTRYPOINT"
  echo 'set -e' >> "$ND_ENTRYPOINT"
  echo 'if [ -n "$1" ]; then "$@"; else /usr/bin/env bash; fi' >> "$ND_ENTRYPOINT";
fi
chmod -R 777 /neurodocker && chmod a+s /neurodocker

apt-get update -qq
apt-get install -y -q --no-install-recommends \
    vim \
    wget \
    strace \
    time \
    ncdu \
    gnupg \
    curl \
    procps \
    datalad \
    pigz \
    git-annex-standalone \
    python-nipype \
    virtualenv \
    python-dcmstack \
    python-configparser \
    python-funcsigs \
    python-pytest \
    dcmtk \
    python-pip \
    python-wheel \
    python-setuptools \
    python-datalad \
    heudiconv \
    dcm2niix \
    python-pytest
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

curl -sL https://deb.nodesource.com/setup_6.x | bash - 

apt-get update -qq
apt-get install -y -q --no-install-recommends \
    nodejs \
    npm
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

npm install -g bids-validator@1.1.1

mkdir /afs /inbox

echo '#!/bin/bash' >> /neurodocker/heudiconv.sh && echo 'heudiconv "$@"' >> /neurodocker/heudiconv.sh && chmod +x /neurodocker/heudiconv.sh

useradd --no-user-group --create-home --shell /bin/bash reproin
su - reproin

echo '{
\n  "pkg_manager": "apt",
\n  "instructions": [
\n    [
\n      "base",
\n      "neurodebian:stretch"
\n    ],
\n    [
\n      "ndfreeze",
\n      {
\n        "date": "20190225"
\n      }
\n    ],
\n    [
\n      "_header",
\n      {
\n        "version": "generic",
\n        "method": "custom"
\n      }
\n    ],
\n    [
\n      "install",
\n      [
\n        "vim",
\n        "wget",
\n        "strace",
\n        "time",
\n        "ncdu",
\n        "gnupg",
\n        "curl",
\n        "procps",
\n        "datalad",
\n        "pigz",
\n        "git-annex-standalone",
\n        "python-nipype",
\n        "virtualenv",
\n        "python-dcmstack",
\n        "python-configparser",
\n        "python-funcsigs",
\n        "python-pytest",
\n        "dcmtk",
\n        "python-pip",
\n        "python-wheel",
\n        "python-setuptools",
\n        "python-datalad",
\n        "heudiconv",
\n        "dcm2niix",
\n        "python-pytest"
\n      ]
\n    ],
\n    [
\n      "run",
\n      "curl -sL https://deb.nodesource.com/setup_6.x | bash - "
\n    ],
\n    [
\n      "install",
\n      [
\n        "nodejs",
\n        "npm"
\n      ]
\n    ],
\n    [
\n      "run",
\n      "npm install -g bids-validator@1.1.1"
\n    ],
\n    [
\n      "run",
\n      "mkdir /afs /inbox"
\n    ],
\n    [
\n      "run",
\n      "echo '"'"'#!/bin/bash'"'"' >> /neurodocker/heudiconv.sh && echo '"'"'heudiconv \"$@\"'"'"' >> /neurodocker/heudiconv.sh && chmod +x /neurodocker/heudiconv.sh"
\n    ],
\n    [
\n      "user",
\n      "reproin"
\n    ],
\n    [
\n      "entrypoint",
\n      "/neurodocker/heudiconv.sh"
\n    ]
\n  ]
\n}' > /neurodocker/neurodocker_specs.json

%environment
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export ND_ENTRYPOINT="/neurodocker/startup.sh"

%runscript
/neurodocker/heudiconv.sh
