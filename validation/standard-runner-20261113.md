# Standard GitHub runner build - 2026-11-13 UTC

**PASS:** [Build TWRP #6](https://github.com/justinlin099/twrp_sony_pdx256/actions/runs/43466474712)
completed a fresh source download, full compilation and image verification on a
standard private-repository `ubuntu-22.04` runner. The downloaded image is
byte-identical to the latest device-tested build and the local clean rebuild.

SHA-256: `f7dc9fc2ed1e72217a81ad9f323d4e08abc5275238edda7f31ad7094a2453f05`

## Measured result

| Measurement | Result |
| --- | ---: |
| Runner | Ubuntu 22.04.5, image `20261111.360.2`, 2 vCPU |
| RAM / total swap | 7.75 GiB / 7 GiB |
| Source download | 9m 45s |
| Compile and verify step | 1h 36m 38s |
| Job duration, including setup and finalization | 1h 53m 30s |
| Free disk after runner cleanup | 49.7 GiB |
| Lowest sampled free disk during build | 2.33 GiB |
| Highest sampled swap use | 4.05 GiB |
| Output image | 100 MiB |

Resources were sampled every 30 seconds. These are observed samples, not
guaranteed instantaneous peaks. The workflow checks available disk space before
downloading and compiling because hosted runner images can change.

## Build inputs and checks

- Integration revision: `ad11c1b5a32634634cc55eba65e47e9a943aa4bc`.
- Device and vendor revisions came from `trees.lock.json`.
- All 657 resolved upstream revisions matched `manifests/default.xml`.
- Fresh checkout and empty build output; no compiler cache or phone-supplied files.
- All 23,363 Ninja tasks completed; `build.sh` exited with status 0.
- Factory/runtime hashes, 696 final CPIO records, policy equivalence, LZ4
  round-trip and AVB signature/payload checks passed.
- The downloaded image hash matches both `recovery.img.sha256` and `recovery.json`.

## Changes needed for this runner

The CI manifest sparsely checks out the required Clang, Rust, Linux JDK and
arm64 ABI-dump files while retaining their build definitions and Soong plugins.
After verifying all revisions, CI removes prebuilt Git objects. Runner cleanup
and object pruning are restricted to disposable GitHub-hosted builds.

Soong analysis exceeded the original RAM and swap capacity. The workflow adds
4 GiB swap to the runner's existing 3 GiB and keeps it throughout the build.
A CI-only Soong patch forwards `GOMEMLIMIT=8GiB` through Blueprint's cleared
environment. Recovery sources and the final image are unchanged by that patch.
The final workflow invokes the existing `build.sh` once.

The `twrp-pdx256-6` artifact contains the image, SHA-256, package report, resolved
manifest, full logs and resource samples. Artifacts are retained for 14 days.
Permanent measurements and input hashes are in
[standard-runner-20261113.json](standard-runner-20261113.json).
