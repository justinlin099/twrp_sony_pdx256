# Source and asset attribution

The patches modify TeamWin / AOSP source. Existing file copyright notices and
upstream licenses remain applicable; this repository does not relicense them.
Exact upstream projects and revisions are in `manifests/default.xml` and
`patches/series.json`. Keep upstream authorship when splitting these patches into
commits or submitting them to TeamWin.

Sony factory runtime binaries are user-supplied, hash checked, and Git ignored.
Stock-derived configuration and SELinux differences are included for this port.
The three MTP ICO assets are derived from Sony Xperia product photographs; no
claim is made that those photographs are under the source-code licenses.
Review asset distribution rights before publishing. No blanket open-source
license is asserted for Sony assets or firmware.

The public AOSP AVB test key is referenced from the pinned AOSP source tree. It
is not a private user key and provides no production signing identity.
