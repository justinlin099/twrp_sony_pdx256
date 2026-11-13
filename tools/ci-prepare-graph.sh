#!/usr/bin/env bash
# Give Soong temporary swap, then reclaim that disk before compiling targets.
set -euo pipefail
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
port=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_dir=$(realpath -- "${1:?Source directory required}")
python3 "$port/tools/prepare-factory.py"
python3 "$port/tools/prepare.py" "$source_dir"
python3 - "$RUNNER_TEMP" <<'PY'
import shutil, sys
free = shutil.disk_usage(sys.argv[1]).free
if free < 11 * 1024**3:
    raise SystemExit('Need 11 GiB free for temporary Soong swap and graph output')
PY
swapfile=$(mktemp --tmpdir="$RUNNER_TEMP" soong-swap.XXXXXX)
cleanup() {
  if swapon --show=NAME --noheadings | grep -Fxq "$swapfile"; then
    sudo swapoff "$swapfile" || return
  fi
  rm -f -- "$swapfile"
}
trap cleanup EXIT
sudo fallocate -l 8G "$swapfile"
sudo chmod 600 "$swapfile"
sudo mkswap "$swapfile"
sudo swapon "$swapfile"
free -h
cd "$source_dir"
export ALLOW_MISSING_DEPENDENCIES=true
set +u
source build/envsetup.sh
lunch twrp_pdx256-ap2a-eng
m -j2 nothing
set -u
cleanup
trap - EXIT
echo 'Soong graph ready; temporary swap removed before target compilation.'
df -h .
free -h
