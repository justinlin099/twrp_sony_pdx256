# SPDX-FileCopyrightText: 2026 Justin Lin and contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Verify and name CI release assets without changing the image bytes."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('artifacts', type=Path)
parser.add_argument('--version', required=True)
args = parser.parse_args()
env = {key: os.environ[key] for key in (
    'GITHUB_REPOSITORY', 'GITHUB_SHA', 'GITHUB_RUN_ID',
    'GITHUB_RUN_NUMBER', 'GITHUB_RUN_ATTEMPT')}
if not re.fullmatch(r'[0-9A-Za-z._-]+', args.version):
    raise SystemExit('Invalid version')
if not re.fullmatch(r'[0-9a-f]{40}', env['GITHUB_SHA']):
    raise SystemExit('Expected full source commit SHA')
for key in ('GITHUB_RUN_ID', 'GITHUB_RUN_NUMBER', 'GITHUB_RUN_ATTEMPT'):
    if not env[key].isdigit():
        raise SystemExit(f'Invalid {key}')

root = args.artifacts
image = root / 'recovery.img'
report_path = root / 'recovery.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
digest = hashlib.sha256(image.read_bytes()).hexdigest()
if image.stat().st_size != 104857600 or digest != report['sha256']:
    raise SystemExit('Image size or SHA-256 does not match the verified build')
if not report.get('policy_cil_equivalent'):
    raise SystemExit('Policy verification did not pass')

build = f"{env['GITHUB_RUN_NUMBER']}.{env['GITHUB_RUN_ATTEMPT']}"
date = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
name = f'twrp-{args.version}-pdx256-{date}'
tag = name
targets = [root / f'{name}{suffix}' for suffix in ('.img', '.img.sha256', '.json')]
if any(path.exists() for path in targets):
    raise SystemExit('Release assets already exist; refusing to overwrite')
image.rename(targets[0])
report_path.rename(targets[2])
targets[1].write_text(f'{digest}  {name}.img\n', encoding='utf-8')
(root / 'recovery.img.sha256').unlink(missing_ok=True)
run_url = f"https://github.com/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}"
(root / 'release-notes.md').write_text(
    f'TWRP {args.version} for Xperia 1 VII (pdx256 / XQ-FS72).\n\n'
    'Firmware base: 71.2.A.2.35.\n\n'
    f'- Build: [{build}]({run_url})\n'
    f"- Source commit: `{env['GITHUB_SHA']}`\n"
    f'- Image: `{name}.img` (100 MiB)\n'
    f'- SHA-256: `{digest}`\n\n'
    'Download the `.img` asset to flash recovery. The matching `.img.sha256` '
    'and `.json` files contain its checksum and packaging verification report.\n',
    encoding='utf-8')
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        print(f'name={name}', file=output)
        print(f'tag={tag}', file=output)
print(name)
