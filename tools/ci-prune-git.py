"""Verify pinned revisions, then discard prebuilt Git objects on disposable CI."""
import os
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

if os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted':
    raise SystemExit('This cleanup is only for disposable GitHub-hosted runners')
source = Path(sys.argv[1]).resolve(strict=True)
actual = Path(sys.argv[2])
expected = Path(__file__).resolve().parents[1] / 'manifests/default.xml'


def pins(path):
    return {p.get('path', p.get('name')): (p.get('name'), p.get('revision'))
            for p in ET.parse(path).getroot().findall('project')}


if pins(actual) != pins(expected):
    raise SystemExit('Resolved source revisions do not match the pinned manifest')
base = (source / '.repo/project-objects/platform/prebuilts').resolve(strict=True)
if not base.is_relative_to(source / '.repo'):
    raise SystemExit('Unexpected Git object directory')
count = 0
for objects in base.glob('**/*.git/objects'):
    if objects.is_symlink() or not objects.resolve().is_relative_to(base):
        raise SystemExit(f'Unexpected object store: {objects}')
    for child in objects.iterdir():
        if child.is_symlink():
            raise SystemExit(f'Unexpected object symlink: {child}')
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    count += 1
print(f'Verified {len(pins(actual))} pinned projects; discarded {count} prebuilt object stores.')
