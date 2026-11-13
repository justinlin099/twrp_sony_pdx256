# Clean GitHub rebuild validation - 2026-11-13

A subsequent full build also passed on a standard GitHub-hosted runner and
produced the same image. See the [CI validation](validation/standard-runner-20261113.md).

**PASS:** a fresh Ubuntu userspace and fresh upstream download produced the same
100 MiB image as the latest device-tested build, byte for byte.

SHA-256:
`f7dc9fc2ed1e72217a81ad9f323d4e08abc5275238edda7f31ad7094a2453f05`

## Environment and inputs

- Fresh Ubuntu Base 22.04.5 amd64 rootfs; official archive checksum verified.
- Isolated chroot sharing the existing WSL2 kernel, not a separate physical PC
  or full virtual machine. Build sandboxing reported disabled under this setup.
- Dependencies installed from the repo script; Python 3.10.12.
- All three private GitHub repositories freshly cloned. Exact tested revisions
  and environment are recorded in [the evidence JSON](validation/clean-build-20261113.json).
- All 657 upstream projects freshly downloaded, with no reference checkout or
  compiler cache. Resolved project revisions exactly match the pinned manifest.
- Empty `out` before the full compile. No prior compiler output was imported.
- Factory dependencies came entirely from the cloned vendor tree. No phone,
  local factory image, or external blob directory was supplied to this build.
- All source trees, rootfs and build output were stored on the external ext4 disk.

## Issues found and fixed by this test

1. The minimal Ubuntu installation lacked the `python` command. Added
   `python-is-python3` to the dependency installer, then started with empty output.
2. Git normalized one line ending in a checksummed init.rc payload. The full
   compile succeeded but the packager correctly rejected the changed bytes.
   Added byte-preserving Git attributes for runtime overlays and checked all
   staged payload hashes. Fresh clones then passed all checks.
3. Added overlay verification before compilation so this type of checkout error
   fails immediately. Existing device files are no longer recopied when unchanged.

After the Git attribute correction, the repositories were cloned again and the
build/packaging command rerun in the same new environment. Compiled source code
was unchanged, so output from the full clean compile was retained for this
packaging-only correction; it was not an additional full recompilation.

The full compilation reported 17m34s. Start-to-final-package time including the
checkout repair was about 23 minutes, excluding upstream downloads. Intermittent
external-disk I/O retries occurred; one earlier Ninja status-FIFO timeout was
logged despite successful compilation. The final command exited successfully,
and the complete image hash matches the device-tested reference.

## Passed checks

- 488 extracted recovery records, seven runtime blobs and 23 overlay payloads
  passed SHA-256 checks after fresh GitHub download.
- Required recovery/runtime-library and host policy-compiler targets completed.
- All 696 final CPIO records round-tripped with their expected metadata/content.
- Recompiled SELinux policy matched the expected normalized CIL semantics.
- LZ4 round-trip, Android v4 image assembly, upstream AVB signature and recovery
  payload hash verification passed.
- Final image is byte-identical to the latest device-tested icon build above.
- Repeating source preparation preserved timestamps of all eight device files.
- All three repositories were confirmed private with default branch `twrp-14.1`.

## Scope and remaining limits

No phone was rebooted or flashed during this repository validation. The earlier
full-image reference in the packaging recipe has hash `9c800a...`; its report
lists policy ordering and service-launcher build-ID differences. That historical
comparison is distinct from the latest device-tested `f7dc9f...` image, which
matches this clean build exactly.

A real personal Data restore remains untested. Backup success is not evidence of
restore success. The remaining Sony init/ramdisk/policy integration is described
in [ARCHITECTURE.md](ARCHITECTURE.md); this is not a claim that plain upstream
`m recoveryimage` without the integration produces the final deployable image.
