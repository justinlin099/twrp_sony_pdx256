"""Verify factory dependencies already included in the private vendor tree."""
import hashlib
import json
from pathlib import Path
from factory import FactoryFiles

root = Path(__file__).resolve().parents[1]
vendor = root / 'vendor/sony/pdx256'
factory = FactoryFiles(vendor)
factory.verify()
entries = json.loads((vendor / 'proprietary-files.json').read_text())
for entry in entries:
    path = vendor / 'proprietary' / entry['destination']
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError(f'Factory runtime checksum mismatch: {path}')

print(f'Verified {len(factory.index)} recovery records and {len(entries)} runtime files.')
