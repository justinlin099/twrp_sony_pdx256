"""Sign recovery using unmodified upstream avbtool and explicit device settings."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AVB_REVISION = 'c024b44b17db0d5dfeaf064aba8a46dbcf3f214d'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('avb_source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--twrp-raw', type=Path, required=True)
    parser.add_argument('--raw-sha256', required=True)
    args = parser.parse_args()
    avb = args.avb_source.resolve(strict=True)
    revision = subprocess.check_output(['git', '-C', str(avb), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != AVB_REVISION:
        raise ValueError(f'Unexpected AVB revision: {revision}')
    payload = args.twrp_raw.read_bytes()
    if hashlib.sha256(payload).hexdigest() != args.raw_sha256:
        raise ValueError('Unsigned recovery checksum mismatch')
    config = json.loads(args.config.read_text())
    key = avb / 'test/data/testkey_rsa4096.pem'
    command = [sys.executable, str(avb / 'avbtool.py')]
    with tempfile.TemporaryDirectory(prefix='pdx256-avb-') as folder:
        candidate = Path(folder) / 'recovery.img'
        candidate.write_bytes(payload)
        options = []
        for name in ('partition_size', 'partition_name', 'algorithm', 'rollback_index', 'salt'):
            options += ['--' + name, str(config[name])]
        for name, value in config['properties'].items():
            options += ['--prop', name + ':' + value]
        subprocess.run(command + ['add_hash_footer', '--image', str(candidate), '--key', str(key),
            '--internal_release_string', config['release_string']] + options, check=True)
        subprocess.run(command + ['verify_image', '--image', str(candidate), '--key', str(key)], check=True)
        with candidate.open('rb') as src, args.output.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        print('Verified upstream AVB:', hashlib.sha256(args.output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
