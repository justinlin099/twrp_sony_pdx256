# Licensing

The original project code listed below is licensed under **GPL-3.0-or-later**:
GNU GPL version 3, or (at your option) any later version. See [LICENSE](LICENSE).
The grant applies to the project contributions identified by their SPDX headers,
not to every file stored in this repository or to the packaged firmware image.

## Original code covered

- `build.sh`
- `.github/workflows/build.yml`
- `tools/checkout-trees.py`
- `tools/ci-prune-git.py`
- `tools/ci-source.sh`
- `tools/extract.py`
- `tools/factory.py`
- `tools/image.py`
- `tools/install-build-deps.sh`
- `tools/package.py`
- `tools/prepare-factory.py`
- `tools/prepare-release.py`
- `tools/prepare.py`
- `tools/sony_avb.py`
- `tools/verify_source_export.py`

## Third-party content

- `patches/` contains changes to TeamWin/AOSP projects. The modified upstream
  files and their existing copyright/license notices govern these patches;
  they are not blanket-relicensed by this repository's GPL grant. Exact base
  revisions are in `patches/series.json` and `manifests/default.xml`.
- `manifests/default.xml` is an upstream-derived dependency manifest; preserve
  upstream terms. Build metadata, validation reports and documents are not
  included in the original-code grant above.
- Device and vendor repositories have their own licensing scope. Their binaries,
  firmware-derived content, artwork and third-party materials do not acquire
  this repository's GPL license through the build process.

The license text is the verbatim GPL-3.0-or-later text from
[SPDX license-list-data](https://github.com/spdx/license-list-data/blob/main/text/GPL-3.0-or-later.txt).
