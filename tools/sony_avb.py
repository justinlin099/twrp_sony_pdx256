"""Use the exact Sony AVB layout for a stock or TWRP test-key control."""

import argparse
import hashlib
import importlib.util
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


STOCK_SHA256 = '895f8c76b4d4ae933344b83f461ffe4f8d7710597e62a590996b5dc371060246'
AVB_REVISION = 'c024b44b17db0d5dfeaf064aba8a46dbcf3f214d'
TWRP_OS0_SHA256 = '56016e8e4e40726e79b656ab59fc9835b67e326711a6bfbb7df32939ad8df222'


def update_recovery_descriptor(vbmeta, auxiliary_start, payload):
    descriptors_offset, descriptors_size = struct.unpack_from('>QQ', vbmeta, 96)
    cursor = auxiliary_start + descriptors_offset
    end = cursor + descriptors_size
    while cursor < end:
        tag, size = struct.unpack_from('>QQ', vbmeta, cursor)
        start = cursor + 16
        if tag == 2:
            algorithm = bytes(vbmeta[start + 8:start + 40]).split(b'\0', 1)[0]
            name_size, salt_size, digest_size = struct.unpack_from('>III', vbmeta, start + 40)
            name_start = start + 116
            salt_start = name_start + name_size
            digest_start = salt_start + salt_size
            if (algorithm != b'sha256' or digest_size != 32 or
                    vbmeta[name_start:salt_start] != b'recovery' or digest_start + digest_size > start + size):
                raise ValueError('Unexpected Sony recovery hash descriptor')
            salt = vbmeta[salt_start:digest_start]
            struct.pack_into('>Q', vbmeta, start, len(payload))
            digest = hashlib.sha256(salt)
            digest.update(payload)
            vbmeta[digest_start:digest_start + digest_size] = digest.digest()
            return ((start, 8), (digest_start, digest_size))
        cursor = start + size
    raise ValueError('Recovery hash descriptor was not found')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stock', type=Path)
    parser.add_argument('avb_source', type=Path)
    parser.add_argument('output', type=Path)
    variant = parser.add_mutually_exclusive_group()
    variant.add_argument('--twrp-os0', type=Path, help='Use the verified os_version=0 TWRP payload')
    variant.add_argument('--twrp-raw', type=Path, help='Use a newly built unsigned recovery payload')
    parser.add_argument('--raw-sha256', help='Expected SHA-256 of the unsigned build output')
    args = parser.parse_args()
    if bool(args.twrp_raw) != bool(args.raw_sha256):
        parser.error('--twrp-raw and --raw-sha256 must be used together')
    avb = args.avb_source.resolve(strict=True)
    source = args.stock.resolve(strict=True)
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != STOCK_SHA256 or original[-64:-60] != b'AVBf':
        raise ValueError('Expected the verified Sony XQ-FS72 71.2.A.2.35 recovery image')
    revision = subprocess.check_output(['git', '-C', avb, 'rev-parse', 'HEAD'], text=True).strip()
    if revision != AVB_REVISION:
        raise ValueError(f'Unexpected AVB source revision {revision}')
    output = args.output.resolve()
    if output.exists() or not output.parent.is_dir():
        raise ValueError('Use an unused output path in the lab directory')

    offset, size = struct.unpack_from('>QQ', original, len(original) - 44)
    factory = original[offset:offset + size]
    auth_size, = struct.unpack_from('>Q', factory, 12)
    hash_offset, hash_size, signature_offset, signature_size, key_offset, key_size = struct.unpack_from('>6Q', factory, 32)
    avbtool = avb / 'avbtool.py'
    key = avb / 'test/data/testkey_rsa4096.pem'
    spec = importlib.util.spec_from_file_location('avbtool', avbtool)
    avb_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(avb_module)
    algorithm_type, = struct.unpack_from('>I', factory, 28)
    algorithm, algorithm_info = avb_module.lookup_algorithm_by_type(algorithm_type)
    if algorithm != 'SHA256_RSA4096':
        raise ValueError(f'Unexpected signing algorithm {algorithm}')

    # Preserve descriptor order and padding exactly as Sony generated them.
    signer = avb_module.RSAPublicKey(str(key))
    encoded_key = signer.encode()
    if len(encoded_key) != key_size:
        raise ValueError('The replacement public key does not fit the original AVB layout')
    vbmeta = bytearray(factory)
    auxiliary_start = 256 + auth_size
    key_start = auxiliary_start + key_offset
    allowed = ((256 + hash_offset, hash_size), (256 + signature_offset, signature_size),
               (key_start, key_size))
    payload = original[:offset]
    if args.twrp_os0:
        twrp = args.twrp_os0.read_bytes()
        if hashlib.sha256(twrp).hexdigest() != TWRP_OS0_SHA256:
            raise ValueError('Expected the verified os_version=0 TWRP candidate')
        payload_size, = struct.unpack_from('>Q', twrp, len(twrp) - 52)
        payload = twrp[:payload_size]
    elif args.twrp_raw:
        raw = args.twrp_raw.read_bytes()
        if (hashlib.sha256(raw).hexdigest() != args.raw_sha256.lower() or
                not raw.startswith(b'ANDROID!') or len(raw) < 4096 or
                raw[-64:-60] == b'AVBf'):
            raise ValueError('Expected the checked unsigned Android recovery build')
        kernel_size, ramdisk_size, _, header_size = struct.unpack_from('<4I', raw, 8)
        version, = struct.unpack_from('<I', raw, 40)
        if (kernel_size, header_size, version) != (0, 1584, 4) or 4096 + ramdisk_size > len(raw):
            raise ValueError('Expected a standalone recovery boot header v4')
        payload = raw[:16] + original[16:20] + raw[20:]
    use_twrp = bool(args.twrp_os0 or args.twrp_raw)
    if use_twrp:
        allowed += update_recovery_descriptor(vbmeta, auxiliary_start, payload)
    vbmeta[key_start:key_start + key_size] = encoded_key
    signed_data = bytes(vbmeta[:256] + vbmeta[auxiliary_start:])
    digest = hashlib.new(algorithm_info.hash_name, signed_data).digest()
    signature = signer.sign(algorithm, signed_data)
    if len(digest) != hash_size or len(signature) != signature_size:
        raise ValueError('Re-signing changed the authentication field sizes')
    vbmeta[256 + hash_offset:256 + hash_offset + hash_size] = digest
    vbmeta[256 + signature_offset:256 + signature_offset + signature_size] = signature

    with tempfile.TemporaryDirectory(prefix='xperia-stock-key-') as folder:
        temp = Path(folder)
        for position, (before, after) in enumerate(zip(factory, vbmeta)):
            if before != after and not any(start <= position < start + length for start, length in allowed):
                raise ValueError(f'Unexpected change in AVB metadata at byte {position}')
        candidate = temp / 'recovery.img'
        if use_twrp:
            if any(original[offset + size:-64]) or len(payload) % 4096:
                raise ValueError('Unexpected original AVB padding or TWRP alignment')
            footer = bytearray(original[-64:])
            struct.pack_into('>QQ', footer, 12, len(payload), len(payload))
            padding = len(original) - len(payload) - len(vbmeta) - len(footer)
            candidate.write_bytes(payload + bytes(vbmeta) + bytes(padding) + footer)
        else:
            candidate.write_bytes(payload + bytes(vbmeta) + original[offset + size:])
        subprocess.run([sys.executable, avbtool, 'verify_image', '--image', candidate, '--key', key], check=True)
        with candidate.open('rb') as src, output.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if hashlib.sha256(output.read_bytes()).hexdigest() != digest:
            raise IOError('Output SHA-256 differs from the verified image')
        label = 'TWRP with Sony AVB layout' if use_twrp else 'stock test-key control'
        print(f'Verified {label}. SHA-256 {digest}')


if __name__ == '__main__':
    main()
