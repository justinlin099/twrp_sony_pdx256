"""Apply pinned source patches and install the recovery device tree."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def run(*args,**kwargs): return subprocess.run(args,check=True,**kwargs)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    args=ap.parse_args()
    source=args.source.resolve(strict=True)
    series=json.loads((ROOT/'patches/series.json').read_text())
    pending=[]
    for entry in series:
        repo=source/entry['path']; patch=ROOT/entry['patch']
        if hashlib.sha256(patch.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError(f'Patch checksum changed: {patch}')
        head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
        if head!=entry['revision']: raise ValueError(f'Wrong upstream revision: {repo}: {head}')
        if subprocess.run(['git','-C',str(repo),'apply','--reverse','--check',str(patch)],capture_output=True).returncode==0:
            print('Already applied:',entry['path']); continue
        run('git','-C',str(repo),'apply','--check',str(patch))
        pending.append((repo,patch))
    copies=[]
    for tree in ('device/sony/pdx256',):
        for path in (ROOT/tree).rglob('*'):
            if '.git' in path.relative_to(ROOT/tree).parts or path.name in ('.gitignore', '.gitattributes', 'NOTICE.md'): continue
            if not path.is_file() or path.name=='README.md': continue
            if 'ramdisk-overlay' in path.parts or 'sepolicy' in path.parts or 'assets' in path.relative_to(ROOT/tree).parts or path.name in ('ramdisk-recipe.json', 'image-config.json'): continue
            target=source/path.relative_to(ROOT)
            if target.exists():
                if target.read_bytes()!=path.read_bytes():
                    raise ValueError(f'Existing tree differs; use a clean checkout: {target}')
                continue
            copies.append((path,target))
    for repo,patch in pending: run('git','-C',str(repo),'apply',str(patch))
    for path,target in copies:
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,target)
    print('Prepared pinned sources. No device was contacted.')
if __name__=='__main__': main()
