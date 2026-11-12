"""Import only pinned factory inputs. No ADB, mounting, or flashing."""
import argparse
import hashlib
import json
from pathlib import Path

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
    recovery = checked(args.recovery, firmware['recovery_sha256'])
    blobs = json.loads((vendor/'proprietary-files.json').read_text())
    inputs = [(entry, checked(args.system_root/entry['source'], entry['sha256'])) for entry in blobs]
    # Validate everything before writing anything; never silently overwrite changed inputs.
    outputs = [(vendor/'stock-recovery.img', recovery)]
    outputs += [(vendor/'proprietary'/e['destination'],data) for e,data in inputs]
    for path,data in outputs:
        if path.exists() and path.read_bytes() != data:
            raise ValueError(f'Refusing to replace different existing input: {path}')
    for path,data in outputs:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    print(f'Imported verified stock recovery and {len(inputs)} runtime files.')

if __name__ == '__main__': main()
