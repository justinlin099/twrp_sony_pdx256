"""Build Sony recovery from factory inputs + fresh build, without a prior custom image."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from image import read_image,read_records,write_records,replace_data,aligned

ROOT=Path(__file__).resolve().parents[1]
def sha(data): return hashlib.sha256(data).hexdigest()
def run(*args,**kwargs): return subprocess.run(args,check=True,**kwargs)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--product-out',type=Path,required=True)
    ap.add_argument('--host-out',type=Path,help='Defaults to SOURCE/out/host/linux-x86')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--verify-reference',action='store_true',help='Require reference ramdisk content; SELinux may be binary-different with identical decoded CIL')
    args=ap.parse_args()
    source=args.source.resolve(strict=True); product=args.product_out.resolve(strict=True)
    host=args.host_out or source/'out/host/linux-x86'
    device=ROOT/'device/sony/pdx256'; vendor=ROOT/'vendor/sony/pdx256'
    firmware=json.loads((vendor/'firmware.json').read_text())
    stockpath=vendor/'stock-recovery.img'
    header,archive=read_image(stockpath,firmware['recovery_sha256']); stock=read_records(archive)
    rawpath=product/'recovery.img'
    _,archive=read_image(rawpath,sha(rawpath.read_bytes())); raw=read_records(archive)
    recipe=json.loads((device/'ramdisk-recipe.json').read_text())
    if args.output.exists(): raise ValueError('Refusing to overwrite output')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='xperia-package-') as tmp:
        tmp=Path(tmp)
        policy=stock['sepolicy'][1]
        (tmp/'stock.policy').write_bytes(policy)
        run(str(host/'bin/checkpolicy'),'-b','-C','-M',str(tmp/'stock.policy'),'-o',str(tmp/'stock.cil'))
        lines=(tmp/'stock.cil').read_text().splitlines()
        remove=set((device/'sepolicy/remove.cil').read_text().splitlines())-{''}
        if not remove<=set(lines): raise ValueError('SELinux base does not match source delta')
        (tmp/'modified.cil').write_text('\n'.join(line for line in lines if line not in remove)+'\n'+(device/'sepolicy/add.cil').read_text())
        version=struct.unpack_from('<I',policy,8+struct.unpack_from('<I',policy,4)[0])[0]
        run(str(host/'bin/secilc'),'-M','true','-c',str(version),'-f','/dev/null','-o',str(tmp/'sepolicy'),str(tmp/'modified.cil'))
        run(str(host/'bin/checkpolicy'),'-b','-C','-M',str(tmp/'sepolicy'),'-o',str(tmp/'rebuilt.cil'))
        normalized=('\n'.join(sorted(set((tmp/'rebuilt.cil').read_text().splitlines())))+'\n').encode()
        if sha(normalized)!=(device/'sepolicy/expected-cil.sha256').read_text().strip():
            raise ValueError('Recompiled policy does not match validated CIL semantics')
        assembled={}; differences=[]
        for e in recipe:
            name=e['name']; kind=e['source']; path=e['path']
            if kind=='stock': data=stock[path][1]
            elif kind=='build-ramdisk': data=raw[path][1]
            elif kind=='build-file': data=(product/path).read_bytes()
            elif kind=='vendor': data=(vendor/'proprietary'/path).read_bytes()
            elif kind=='overlay': data=(device/'ramdisk-overlay'/path).read_bytes()
            elif kind=='policy': data=(tmp/'sepolicy').read_bytes()
            elif kind=='empty': data=b''
            else: raise ValueError(kind)
            if sha(data)!=e['reference_sha256']:
                if kind in ('stock','vendor','overlay','empty'): raise ValueError(f'Input changed: {name}')
                differences.append(name)
            assembled[name]=replace_data((bytes.fromhex(e['header']),b''),data)
        if args.verify_reference and set(differences)-{'sepolicy'}:
            raise ValueError(f'Not reference-identical: {differences}')
        archive=write_records(assembled)
        if read_records(archive)!=assembled: raise ValueError('CPIO round trip failed')
        packed=subprocess.check_output(['lz4','-l','-12','--favor-decSpeed','-c'],input=archive)
        if subprocess.check_output(['lz4','-d','-c'],input=packed)!=archive: raise ValueError('LZ4 round trip failed')
        payload=header[:12]+struct.pack('<I',len(packed))+header[16:]+packed
        payload=payload.ljust(aligned(len(payload),4096),b'\0')
        (tmp/'unsigned.img').write_bytes(payload)
        run(sys.executable,str(ROOT/'tools/sony_avb.py'),str(stockpath),str(source/'external/avb'),str(args.output),
            '--twrp-raw',str(tmp/'unsigned.img'),'--raw-sha256',sha(payload))
        _,archive=read_image(args.output,sha(args.output.read_bytes()))
        if read_records(archive)!=assembled: raise ValueError('Final ramdisk differs')
        report={'sha256':sha(args.output.read_bytes()),'ramdisk_entries':len(assembled),
                'reference_content_differences':differences,'reference_identical':not differences,
                'policy_cil_equivalent':True,
                'reference_image_sha256':firmware['reference_recovery_sha256']}
        args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
if __name__=='__main__': main()
