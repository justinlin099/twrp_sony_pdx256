# Source and asset attribution

The patches modify TeamWin / AOSP source. Existing file copyright notices and
upstream licenses remain applicable; this repository does not relicense them.
Exact upstream projects and revisions are in `manifests/default.xml` and
`patches/series.json`. Keep upstream authorship when splitting these patches into
commits or submitting them to TeamWin.

The private vendor repository includes seven hash-checked factory runtime files
and individually extracted recovery dependencies from firmware 71.2.A.2.35.
No complete stock recovery image is included. These files retain their
original licenses; inclusion does not relicense Sony or third-party components.
Stock-derived configuration and SELinux differences are included for this port.
The reviewed SVG sources under assets/mtp-icons in the device tree include
third-party SONY/XPERIA vector wordmarks and a user-captured TWRP home screen.
See assets/mtp-icons/wordmark-sources.txt for wordmark provenance. The device
illustration is project artwork, but the wordmarks and UI are not. Current ICOs
use upper-rear artwork below 64 px and front/rear artwork at 64 px and above.
Earlier Git commits still contain photo-derived icons; this replacement does
not remove those historical assets. No blanket open-source license is asserted
for Sony assets or firmware.

The public AOSP AVB test key is referenced from the pinned AOSP source tree. It
is not a private user key and provides no production signing identity.
