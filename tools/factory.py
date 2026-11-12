"""Read hash-checked, individually extracted Sony recovery dependencies."""
import hashlib
import json
from pathlib import PurePosixPath


class FactoryFiles:
    def __init__(self, vendor):
        self.root = vendor / 'recovery'
        self.index = json.loads((self.root / 'files.json').read_text())

    def read(self, name):
        entry = self.index[name]
        if 'file' in entry:
            path = PurePosixPath(entry['file'])
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'Invalid factory path: {path}')
            data = (self.root / path).read_bytes()
        else:
            data = bytes.fromhex(entry['inline_hex'])
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError(f'Factory recovery checksum mismatch: {name}')
        return data

    def verify(self):
        for name in self.index:
            self.read(name)
