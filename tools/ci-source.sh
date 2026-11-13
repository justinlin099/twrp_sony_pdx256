#!/usr/bin/env bash
set -euo pipefail
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
port=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_dir=${1:?Source directory required}
artifacts=${2:?Artifact directory required}
mkdir -p "$source_dir" "$artifacts" "$HOME/.local/bin"
curl -fL --retry 3 https://storage.googleapis.com/git-repo-downloads/repo -o "$HOME/.local/bin/repo"
chmod +x "$HOME/.local/bin/repo"
export PATH="$HOME/.local/bin:$PATH"
git config --global user.name 'github-actions[bot]'
git config --global user.email '41898282+github-actions[bot]@users.noreply.github.com'
cd "$source_dir"
test ! -d .repo
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git \
  -b twrp-14.1 --depth=1 --no-clone-bundle --repo-rev=v2.73
cp "$port/manifests/default.xml" .repo/manifests/pdx256-pinned.xml
cp "$port/manifests/ci.xml" .repo/manifests/pdx256-ci.xml
repo init -m pdx256-ci.xml --no-clone-bundle --repo-rev=v2.73
repo sync -c -j4 --jobs-network=4 --jobs-checkout=2 --no-clone-bundle --fail-fast --retry-fetches=3
repo manifest -r -o "$artifacts/source-manifest.xml"
python3 "$port/tools/ci-prune-git.py" "$source_dir" "$artifacts/source-manifest.xml"
df -h .
