# Building TWRP for Xperia 1 VII

XQ-FS72 (pdx256) / firmware 71.2.A.2.35 / TWRP 3.7.1_14.

## Related repositories

| Repository | Purpose | Branch |
| --- | --- | --- |
| [Device tree](https://github.com/justinlin099/android_device_sony_pdx256/tree/twrp-14.1) | Xperia device configuration and recovery integration | `twrp-14.1` |
| [Vendor tree](https://github.com/justinlin099/android_vendor_sony_pdx256/tree/twrp-14.1) | Required Sony proprietary dependencies | `twrp-14.1` |
| [TWRP manifest](https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp/tree/twrp-14.1) | Upstream source manifest | `twrp-14.1` |
| [TWRP recovery](https://github.com/TeamWin/android_bootable_recovery/tree/android-14.1) | Upstream recovery source | `android-14.1` |

This repository contains the build scripts, patches and GitHub Actions workflow.
Exact build revisions are pinned in [trees.lock.json](trees.lock.json) and
[manifests/default.xml](manifests/default.xml).

## GitHub Actions

Open **Actions → Build TWRP → Run workflow**, select `twrp-14.1`, and start the run.
The workflow downloads the pinned sources, applies the patches, builds on a
standard `ubuntu-22.04` runner, and uploads a `twrp-pdx256-<run number>` artifact.
After a successful build, it also publishes a GitHub Release with the image,
SHA-256 file and packaging verification report. Image filenames include the TWRP
version, device and release date in Taiwan time, for example:
`twrp-3.7.1_14-pdx256-20261114.img`.
Download the `.img` asset from **Releases**. Full build logs remain in the Actions
artifact. Each release tag points to the exact source commit used for that build;
the tag uses the same date-based name as the image. A successful same-day rebuild
updates that release's three assets, notes and tag target to the new source commit.

For a fork, create a read-only SSH deploy key for each private companion repository
and save the corresponding private keys as Actions secrets in the build repository:

- `DEVICE_REPO_SSH_KEY`: read access to `android_device_sony_pdx256`.
- `VENDOR_REPO_SSH_KEY`: read access to `android_vendor_sony_pdx256`.

These secrets are already configured in this repository. The workflow uses a fresh
checkout on every run; it does not need a phone, a self-hosted runner, or a build cache.

[A complete standard-runner build passed](validation/standard-runner-20261113.md)
in about 1 hour 54 minutes and produced the same image as the device-tested build.
Actions artifacts are kept for 14 days. Release assets remain available until
the release or assets are deleted.

## Local build

## 1. Set up the environment

Use Ubuntu 22.04 or Ubuntu 22.04 on WSL2 with at least 150 GiB of free space.
Keep the source and build output on a Linux filesystem such as ext4.

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 gh

gh auth login
gh auth setup-git
```

Your GitHub account needs read access to this repository and both private device and vendor repositories.

## 2. Download the build and device files

Replace `/path/to/build` with your build directory. Run the following commands in the same shell.

```bash
export BUILD_ROOT=/path/to/build
export PORT="$BUILD_ROOT/pdx256-port"
export SOURCE="$BUILD_ROOT/twrp-source"
export OUTPUT="$BUILD_ROOT/artifacts/recovery.img"

mkdir -p "$BUILD_ROOT"
git clone -b twrp-14.1 https://github.com/justinlin099/twrp_sony_pdx256.git "$PORT"
python3 "$PORT/tools/checkout-trees.py"
sudo bash "$PORT/tools/install-build-deps.sh"
```

`checkout-trees.py` downloads the pinned device and vendor trees. The vendor tree includes all required factory dependencies.

## 3. Install the repo tool

```bash
mkdir -p "$HOME/.local/bin"
curl -fL https://storage.googleapis.com/git-repo-downloads/repo -o "$HOME/.local/bin/repo"
chmod +x "$HOME/.local/bin/repo"
export PATH="$HOME/.local/bin:$PATH"
```

## 4. Download the TWRP source

```bash
mkdir -p "$SOURCE"
cd "$SOURCE"
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git \
  -b twrp-14.1 --depth=1 --no-clone-bundle
cp "$PORT/manifests/default.xml" .repo/manifests/pdx256-pinned.xml
repo init -m pdx256-pinned.xml --no-clone-bundle
repo sync -c -j8 --no-clone-bundle
```

## 5. Apply patches and build

`build.sh` handles the following steps automatically; you do not need to run `git apply` manually:

1. Verify the hashes of the factory dependencies and ramdisk files.
2. Run `tools/prepare.py` to apply the patches listed in `patches/series.json` to `bootable/recovery`, `system/vold`, and `packages/modules/adb`, and install the device tree.
3. Run `lunch twrp_pdx256-ap2a-eng` and compile recovery and the required libraries.
4. Package and verify the final image.

```bash
bash "$PORT/build.sh" "$SOURCE" "$OUTPUT" 8
```

The final argument, `8`, sets the number of parallel build jobs. Adjust it for your machine.

To apply the patches and inspect the source before building, run this after syncing:

```bash
python3 "$PORT/tools/prepare.py" "$SOURCE"
```

Then run `build.sh` as usual. Already-applied patches are skipped. A revision mismatch or patch application failure stops preparation with an error.

## Build output

- `$BUILD_ROOT/artifacts/recovery.img`: the packaged recovery image.
- `$BUILD_ROOT/artifacts/recovery.json`: the image SHA-256 and packaging verification results.

Flash `artifacts/recovery.img`. The `recovery.img` under `twrp-source/out` is an intermediate image that has not completed the packaging step.

Use a new output filename for subsequent builds; the packager does not overwrite existing images:

```bash
bash "$PORT/build.sh" "$SOURCE" "$BUILD_ROOT/artifacts/recovery-v2.img" 8
```

## License

This project is licensed under [GPL-3.0-or-later](LICENSE). Third-party content
retains its original licenses and notices. See [LICENSING.md](LICENSING.md).
