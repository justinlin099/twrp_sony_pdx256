# SPDX-FileCopyrightText: 2026 Justin Lin and contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Android v4 / newc utilities shared by extraction and packaging."""
import hashlib
import struct
import subprocess
from pathlib import PurePosixPath

def aligned(size, unit=4):
    return (size + unit - 1) // unit * unit

def read_image(path, expected_sha256):
    image = path.read_bytes()
    if hashlib.sha256(image).hexdigest() != expected_sha256:
        raise ValueError(f'Unexpected input SHA-256 for {path}')
    kernel_size, ramdisk_size = struct.unpack_from('<II', image, 8)
    if not image.startswith(b'ANDROID!') or kernel_size or struct.unpack_from('<I', image, 40) != (4,):
        raise ValueError('Expected a kernelless Android boot v4 recovery image')
    archive = subprocess.check_output(['lz4', '-d', '-c'], input=image[4096:4096 + ramdisk_size])
    return image[:4096], archive

def records(archive):
    offset = 0
    while offset + 110 <= len(archive):
        header = archive[offset:offset + 110]
        if header[:6] != b'070701':
            raise ValueError('Expected a newc ramdisk archive without CRC')
        name_size = int(header[94:102], 16)
        name_end = offset + 110 + name_size
        name = archive[offset + 110:name_end - 1].decode().removeprefix('./')
        if name == 'TRAILER!!!':
            yield name, (archive[offset:name_end], b'')
            return
        start = aligned(name_end)
        end = start + int(header[54:62], 16)
        if end > len(archive) or '..' in PurePosixPath(name).parts or name.startswith('/'):
            raise ValueError(f'Invalid archive record {name}')
        yield name, (archive[offset:name_end], archive[start:end])
        offset = aligned(end)
    raise ValueError('Missing newc trailer')

def read_records(archive):
    items = list(records(archive))
    result = dict(items)
    if len(result) != len(items):
        raise ValueError('Duplicate CPIO path')
    return result

def write_records(entries):
    archive = bytearray()
    for header, data in entries.values():
        if int(header[54:62], 16) != len(data):
            raise ValueError('CPIO file size mismatch')
        archive.extend(header)
        archive.extend(bytes(aligned(len(header)) - len(header)))
        archive.extend(data)
        archive.extend(bytes(aligned(len(data)) - len(data)))
    return bytes(archive)

def replace_data(record, data):
    header, _ = record
    return header[:54] + f'{len(data):08x}'.encode() + header[62:], data
