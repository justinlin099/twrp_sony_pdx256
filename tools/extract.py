# SPDX-FileCopyrightText: 2026 Justin Lin and contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Import only pinned factory inputs. No ADB, mounting, or flashing."""
import argparse
import hashlib
import json
from pathlib import Path
from image import read_image, read_records

ROOT = Path(__file__).resolve().parents[1]
def checked(path, digest):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f'Wrong firmware/content: {path}')
    return data

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--recovery', type=Path, required=True)
    ap.add_argument('--system-root', type=Path, required=True,
                    help='Extracted stock root containing system/bin and system/lib64')
    args = ap.parse_args()
    vendor = ROOT/'vendor/sony/pdx256'
    firmware = json.loads((vendor/'firmware.json').read_text())
    _, archive = read_image(args.recovery, firmware['recovery_sha256'])
    stock = read_records(archive)
    recipe = json.loads((ROOT/'device/sony/pdx256/ramdisk-recipe.json').read_text())
    names = sorted({e['path'] for e in recipe if e['source'] == 'stock'} | {'sepolicy'})
    blobs = json.loads((vendor/'proprietary-files.json').read_text())
    inputs = [(entry, checked(args.system_root/entry['source'], entry['sha256'])) for entry in blobs]
    # Validate everything before writing anything; never silently overwrite changed inputs.
    outputs = [(vendor/'proprietary'/e['destination'],data) for e,data in inputs]
    index = {}
    for name in names:
        header, data = stock[name]
        entry = {'sha256': hashlib.sha256(data).hexdigest()}
        mode = int(header[14:22], 16)
        if data and mode & 0o170000 == 0o100000:
            entry['file'] = 'root/' + name
            outputs.append((vendor/'recovery'/entry['file'], data))
        else:
            # Directories and symlink targets retain CPIO metadata in the recipe.
            entry['inline_hex'] = data.hex()
        index[name] = entry
    outputs.append((vendor/'recovery/files.json', (json.dumps(index, indent=2)+'\n').encode()))
    for path,data in outputs:
        if path.exists() and path.read_bytes() != data:
            raise ValueError(f'Refusing to replace different existing input: {path}')
    for path,data in outputs:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    print(f'Extracted {len(index)} recovery records and {len(inputs)} runtime files; no image copied.')

if __name__ == '__main__': main()
