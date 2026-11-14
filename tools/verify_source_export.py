# SPDX-FileCopyrightText: 2026 Justin Lin and contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Apply exported patches to pristine upstream files in disposable directories."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('reference_source',type=Path)
args=ap.parse_args()
reports=[]
for entry in json.loads((ROOT/'patches/series.json').read_text()):
    repo=args.reference_source/entry['path']; patch=ROOT/entry['patch']
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    assert head==entry['revision']
    assert hashlib.sha256(patch.read_bytes()).hexdigest()==entry['sha256']
    tracked=subprocess.check_output(['git','-C',str(repo),'diff','--name-only','HEAD'],text=True).splitlines()
    untracked=subprocess.check_output(['git','-C',str(repo),'ls-files','--others','--exclude-standard'],text=True).splitlines()
    with tempfile.TemporaryDirectory(prefix='xperia-patch-check-') as td:
        root=Path(td)
        for name in tracked:
            data=subprocess.check_output(['git','-C',str(repo),'show',f'HEAD:{name}'])
            path=root/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
            mode=subprocess.check_output(['git','-C',str(repo),'ls-tree','HEAD','--',name],text=True).split()[0]
            path.chmod(int(mode,8)&0o777)
        subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True)
        subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
        for name in tracked+untracked:
            assert (root/name).read_bytes()==(repo/name).read_bytes(),name
        subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=root,check=True)
    reports.append({'project':entry['path'],'files_verified':len(tracked+untracked),'result':'PASS'})
print(json.dumps(reports,indent=2))
