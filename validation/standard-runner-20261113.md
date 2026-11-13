# Standard GitHub runner feasibility - 2026-11-13

Selective toolchain downloads passed on a standard private-repository
`ubuntu-22.04` runner. A complete recovery build has **not** been tested there.

## Measured runner capacity

Image: `ubuntu22 20261111.360.2`; Ubuntu 22.04.5.

| Measurement | Result |
| --- | ---: |
| Available disk before cleanup | 13.6 GiB |
| Available disk after removing unused preinstalled tools | 46.5 GiB |
| RAM | 7.75 GiB |
| Existing swap | 3 GiB |
| Selected Rust checkout including Git objects | 2.32 GiB |
| Selected Clang checkout including Git objects | 3.61 GiB |
| Available disk after both toolchain downloads | 40.6 GiB |

Cleanup removed preinstalled .NET, Android SDK, hosted tool caches, PowerShell,
Swift, ghcup, global Node modules and Chromium only on the disposable hosted VM.
These measurements are specific to this image; a build workflow must check free
space rather than assume that future runners provide the same amount.

## Toolchain download test

Both repositories were cloned with `--filter=blob:none --no-checkout --depth=1`,
then checked out using Git sparse checkout at the existing pinned revisions:

- Rust: `4ebcd0d4c717e312c2773f4019e0874b994ac2b8`, keeping `linux-x86/1.75.0`.
- Clang: `7154d3eddcb62ff7909a6ae2bf0c03e445e65bc4`, keeping `clang-r510928`.

The Git revisions matched, and both `rustc --version` and `clang --version`
executed successfully. The combined download occupied 5.93 GiB including Git
objects, compared with about 30 GiB of worktree files alone in the full local
Rust/Clang checkouts. The successful local build's Ninja dependency graph uses
these same toolchain versions.

Runs:
- [Initial capacity measurement](https://github.com/justinlin099/twrp_sony_pdx256/actions/runs/43440925387)
- [Cleanup and selective download test](https://github.com/justinlin099/twrp_sony_pdx256/actions/runs/43442201989)

## Remaining work before a full CI build

The full local source, Git objects and output occupy about 90 GiB. In addition
to sparse Rust/Clang downloads, a CI profile would need to reduce unused JDKs,
ABI dump architectures/versions and misc prebuilts, and discard unneeded
prebuilt Git objects after recording and verifying their revisions. Keep the
Git metadata needed by patch preparation and AVB verification.

A preliminary target is roughly 40-45 GiB including build output. This is an
estimate, not a measured full-build peak. The slim checkout must retain build
definitions and be tested through fresh Soong analysis and a complete build;
the existing Ninja input list alone does not prove that pruning is safe.

Start with two compile jobs, preserve swap, measure peak disk/memory use and
verify the final image against the known build. The workflow also needs scoped
read access to the two private companion repositories: the default
`GITHUB_TOKEN` only covers the integration repository. No account token was
copied into Actions secrets during this investigation.

The one-off probe workflow was removed after collecting these results. The
existing build scripts and manifest were not changed by this investigation.

References:
- [GitHub-hosted runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Checkout authentication for private companion repositories](https://github.com/actions/checkout#checkout-multiple-repos-private)
- [Git sparse checkout](https://git-scm.com/docs/git-sparse-checkout)
