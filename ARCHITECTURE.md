# Build simplification review

## Removed

- Whole stock recovery dependency: only the ramdisk records consumed by the
  recipe and the original policy are extracted into the vendor tree. No stock
  image, compressed stock image, original AVB signature, or padding is required.
- Custom AVB binary mutation and stock/test-candidate modes: upstream avbtool
  now generates and verifies the signature from explicit device parameters.
- Hand-built Android image header: upstream mkbootimg generates header v4.
- Unused backup sample and custom-volume executables: no production caller or
  recipe entry referenced them; native TWRP backup remains unchanged.
- External manual blob import as a build prerequisite: the private vendor tree
  now includes every pinned dependency. Extraction is a maintainer operation.
- Recopying unchanged device files on each build: prepare now preserves their
  timestamps, avoiding unnecessary build-rule regeneration on repeat runs.

Using the same compiler output, the split-input/upstream-tool package matched
the flashed icon build byte for byte:
`f7dc9fc2ed1e72217a81ad9f323d4e08abc5275238edda7f31ad7094a2453f05`.

## Remaining device-specific integration

This is still a staged Sony port, not a claim that unmodified upstream
`m recoveryimage` alone produces the final deployable image.

| Component | Why it remains |
| --- | --- |
| Pinned recovery/vold/ADB patches | Implement the tested FBE, storage, display and USB integration. |
| Ramdisk recipe | Combines the Android 14 TWRP build with the tested Sony init/runtime and exact file metadata. |
| Policy delta and CIL equivalence check | Preserves the factory security-service environment plus the reviewed recovery permissions. |
| Service launcher | Still referenced by active init services and the recovery integration. Its diagnostic name does not make it unused. |
| Factory input hash verification | Detects incompatible or modified runtime files before a long compile; package validation checks the final inputs again. |

AOSP provides recovery file installation, image-header and AVB settings; the
remaining recipe can be migrated into those build rules. Doing that safely also
requires checking file ownership, symlink layout, init ordering and policy
behavior on-device. Merely replacing the Sony init/policy with an Android 14
default would change the tested runtime and is not a cleanup-only operation.
The active service launcher and security startup have therefore not been
silently deleted during the repository/build reproducibility work.

Relevant upstream implementations:
- https://android.googlesource.com/platform/build/+/refs/tags/android-14.0.0_r67/core/Makefile
- https://source.android.com/docs/core/architecture/partitions/generic-boot

See VALIDATION.md for the independent clean-build result and its limits.
