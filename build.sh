#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Justin Lin and contributors
# SPDX-License-Identifier: GPL-3.0-or-later

set -euo pipefail
port_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_dir=$(realpath -- "${1:?Usage: bash build.sh SOURCE_DIR OUTPUT_IMG [JOBS]}")
output_img=$(realpath -m -- "${2:?Output image required}")
jobs=${3:-8}
python3 "$port_dir/tools/prepare-factory.py"
python3 "$port_dir/tools/prepare.py" "$source_dir"
cd "$source_dir"
export ALLOW_MISSING_DEPENDENCIES=true
# AOSP envsetup scripts are not nounset-clean.
set +u
source build/envsetup.sh
lunch twrp_pdx256-ap2a-eng
host_out=$(get_build_var HOST_OUT)
m -j"$jobs" recoveryimage "$host_out/bin/checkpolicy" "$host_out/bin/secilc" \
  android.hardware.gatekeeper-V1-ndk android.hardware.security.keymint-V3-ndk \
  android.security.aaid_aidl-cpp android.system.keystore2-V4-ndk libresetprop libsysutils
product_out=$(get_build_var PRODUCT_OUT)
set -u
python3 "$port_dir/tools/package.py" --source "$source_dir" \
  --product-out "$product_out" --host-out "$host_out" --output "$output_img"
