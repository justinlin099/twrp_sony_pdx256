"""Clone pinned companion repositories; never overwrite an existing checkout."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
for entry in json.loads((root / 'trees.lock.json').read_text()):
    target = root / entry['path']
    if target.exists():
        head = subprocess.check_output(['git', '-C', str(target), 'rev-parse', 'HEAD'], text=True).strip()
        if head != entry['revision']:
            raise RuntimeError(f'Existing tree revision differs: {target}')
        if subprocess.check_output(['git', '-C', str(target), 'status', '--porcelain']):
            raise RuntimeError(f'Existing tree has local changes: {target}')
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'clone', '--branch', entry['branch'], entry['url'], str(target)], check=True)
    subprocess.run(['git', '-C', str(target), 'checkout', '--detach', entry['revision']], check=True)
print('Companion trees match pinned revisions.')
