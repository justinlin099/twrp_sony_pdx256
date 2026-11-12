# Repository export validation — 2026-11-12

## Device codename rename — 2026-11-13

Renamed device/vendor directories and product to pdx256; XQ-FS72 model and firmware
checks remain unchanged. Active WSL device tree was migrated; prepare.py and
lunch twrp_pdx256-ap2a-eng passed. This rename has not yet had a full rebuild or
device flash. Existing xq_fs72-named output images remain historical artifacts.

## Kernel dependency removal — 2026-11-13

- Removed the device-specific kernel tree and source-build experiment tools.
- Extraction succeeds with only stock recovery and the seven system runtime files.
- Fresh temporary checkouts pass prepare without any kernel tree or Image input.
- Recovery builds with TARGET_NO_KERNEL=true and PRODUCT_BUILD_RECOVERY_IMAGE=true.
- Ninja recovery target has no old prebuilt-kernel dependency; raw header kernel_size=0.
- New Sony AVB packaging passed and produced SHA-256
  `d9dbd069bffa6fe79d565c3841e742aadceeaffb4b5b21bb65d6c1fda9df55fb`,
  byte-identical to the earlier repository rebuild. No phone was flashed.

The phone was left in Android. Repository organization did not reboot or flash it.

## Passed

- Exported patches replayed on pristine upstream file contents; all 53 modified
  or added files match the working source (40 recovery, 12 vold, 1 adb).
- `prepare.py` applied all patches in fresh temporary Git clones of the pinned
  projects, installed device inputs, then ran again without duplicate
  application. The original build checkout was not changed by this test.
- Stock recovery and seven runtime inputs passed SHA-256 extraction
  checks. Their imported copies are excluded by `.gitignore`.
- Python tools compile and `build.sh` passes Bash syntax checking.
- Recovery and all six explicitly required runtime-library targets completed a
  build in the existing pinned checkout. Host checkpolicy/secilc output targets
  were separately checked through Ninja and were up to date.
- The new packager rebuilt a recovery using stock inputs and the existing current
  build output. It did not consume any historical custom recovery image.
- All 696 CPIO entries round-trip correctly. Every payload matches the validated
  reference except the recompiled SELinux binary. The complete normalized decoded
  CIL matches the reference; no rule differences are ignored.
- LZ4 round-trip and Sony-layout AVB signature/hash verification passed.

Reference device-tested image SHA-256:
`9c800a77069b78c646cb97cee904e2b6d7410091e4e6b96a821f245c115ad4a1`

Repository-rebuilt image SHA-256:
`d9dbd069bffa6fe79d565c3841e742aadceeaffb4b5b21bb65d6c1fda9df55fb`

Different SELinux binary ordering means the complete image is **not byte-identical**.
The rebuilt image has not been flashed; do not describe offline equivalence as a
new device boot test.

## Remaining validation

- Full download and clean build in an independent Linux environment. Current
  packaging tests use the existing compiler output, not a second clean build.
- A real personal Data restore remains untested. No personal Data was wiped to
  validate this export.

For maintainers, `tools/verify_source_export.py REFERENCE_SOURCE` checks that the
exported patches reproduce a known working checkout. `tools/package.py
--verify-reference ...` additionally requires reference-identical ramdisk payloads
(with explicitly checked CIL equivalence for the SELinux binary).
