FROM debian:stretch

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends ca-certificates apt-utils dcmtk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /dicoms
