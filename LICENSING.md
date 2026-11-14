# Licensing

This build-integration project is licensed under **GPL-3.0-or-later**:
GNU GPL version 3, or (at your option) any later version. See [LICENSE](LICENSE).

This is the default license for the project's original contributions, including
build scripts, tools, workflows, configuration, manifests, metadata and documentation,
unless a file explicitly states otherwise. It is not limited to files with SPDX
headers or to an enumerated list of source files.

## Third-party content

Third-party content retains its original licenses, copyright notices and attribution
requirements. The project's GPL license does not remove or replace those terms.
GPL-compatible third-party content may be included in the GPL-licensed project
subject to its applicable conditions.

- Patches modify TeamWin/AOSP source. Preserve upstream notices and comply with
  the applicable upstream licenses when applying or distributing those changes.
  Exact base revisions are recorded in `patches/series.json` and
  `manifests/default.xml`; the CI-only Soong patch is under `patches/ci/`.
- Manifest entries identify external repositories and pinned revisions. Listing
  or downloading a dependency does not relicense that dependency. Any upstream
  material retained in a manifest keeps its applicable original terms.
- The separate device and vendor repositories retain their own licensing scopes.
  Their firmware binaries, artwork and other third-party materials are not
  relicensed by this build repository or by the packaging process.

See [NOTICE.md](NOTICE.md) for source attribution. The GPL license text is reproduced
verbatim from [SPDX license-list-data](https://github.com/spdx/license-list-data/blob/main/text/GPL-3.0-or-later.txt).
