# Source attribution

Original build tools and workflow: see [LICENSING.md](LICENSING.md) and [LICENSE](LICENSE).

Patches target TeamWin recovery, AOSP-derived vold/adb and Soong. Retain each
upstream file's notices and license. `patches/series.json` and
`manifests/default.xml` identify the exact source revisions; the CI Soong patch
is under `patches/ci/`. No third-party file is relicensed by adding GPL here.

The AOSP AVB test key is referenced from the pinned upstream source; it is a
public test key, not a private project credential.

Factory binaries and icon assets are tracked in the companion repositories.
Their licensing/source records are maintained there rather than duplicated here.
