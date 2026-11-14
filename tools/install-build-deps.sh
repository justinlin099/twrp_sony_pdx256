#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Justin Lin and contributors
# SPDX-License-Identifier: GPL-3.0-or-later

# Run as root inside a dedicated Ubuntu 22.04 build environment.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  bc binutils bison build-essential ca-certificates curl file flex g++-multilib \
  gcc-multilib git gnupg gperf lib32readline-dev lib32z1-dev libelf-dev \
  liblz4-tool libncurses5 libncurses5-dev libsdl1.2-dev libssl-dev libxml2-utils \
  lz4 openssl patch python3 python3-pip rsync unzip x11proto-core-dev xsltproc \
  zip zlib1g-dev locales fontconfig python-is-python3
locale-gen en_US.UTF-8
