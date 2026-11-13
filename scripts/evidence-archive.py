#!/usr/bin/env python3
"""List, read or restore checksummed historical evidence from the cleanup index."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import os
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATTERN = 'cleanup-handoff-*.json'


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def file_digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def safe_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Archive path must stay inside .analysis')
    return Path(*path.parts)


def records(analysis):
    rows = []
    seen = set()
    indexes = sorted(analysis.glob(INDEX_PATTERN))
    if not indexes:
        raise ValueError('No evidence cleanup index found')
    for path in indexes:
        index = json.loads(path.read_text())
        if index['status'] != 'complete':
            raise ValueError('Evidence cleanup is not complete')
        for row in index['records']:
            if row['path'] in seen:
                raise ValueError('Duplicate evidence path in cleanup indexes')
            seen.add(row['path'])
            rows.append(row)
    return rows


def local_path(analysis, name):
    path = analysis
    for part in safe_path(name).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Evidence path contains a symlink')
    return path


def payloads(analysis, record):
    archive = local_path(analysis, record['archive'])
    if file_digest(archive) != record['archive_sha256']:
        raise ValueError('Archive checksum differs from the verified cleanup index')
    if record['kind'] == 'file':
        with gzip.open(archive, 'rb') as stream:
            data = stream.read()
        if digest(data) != record['sha256']:
            raise ValueError('Decompressed file checksum differs')
        yield record['path'], data, record
    else:
        expected = {m['path']: m for m in record['members']}
        root = safe_path(record['path'])
        with tarfile.open(archive, 'r:gz') as stream:
            members = stream.getmembers()
            if len(members) != len(expected) or {m.name for m in members} != set(expected):
                raise ValueError('Archive members differ from the verified index')
            for member in members:
                path = safe_path(member.name)
                if (not member.isfile() or len(path.parts) <= len(root.parts) or
                        path.parts[:len(root.parts)] != root.parts):
                    raise ValueError('Archive contains an unsupported member')
                data = stream.extractfile(member).read()
                metadata = expected[member.name]
                if digest(data) != metadata['sha256']:
                    raise ValueError('Archived member checksum differs')
                yield member.name, data, metadata


def restore(analysis, record):
    target = local_path(analysis, record['path'])
    if target.exists() or target.is_symlink():
        raise ValueError('Restore destination already exists; existing evidence will not be overwritten')
    with tempfile.TemporaryDirectory(prefix='.restore-evidence-', dir=analysis) as temporary:
        stage = Path(temporary)
        for name, data, metadata in payloads(analysis, record):
            path = stage / safe_path(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(metadata['mode'])
            os.utime(path, ns=(metadata['mtime_ns'], metadata['mtime_ns']))
        root = safe_path(record['path'])
        for metadata in reversed(record.get('directories', [])):
            relative = safe_path(metadata['path'])
            if relative.parts[:len(root.parts)] != root.parts:
                raise ValueError('Directory metadata escapes the evidence root')
            path = stage / relative
            path.mkdir(parents=True, exist_ok=True)
            path.chmod(metadata['mode'])
            os.utime(path, ns=(metadata['mtime_ns'], metadata['mtime_ns']))
        target.parent.mkdir(parents=True, exist_ok=True)
        os.rename(stage / safe_path(record['path']), target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'show', 'restore'])
    parser.add_argument('path', nargs='?', default='')
    args = parser.parse_args()
    analysis = ROOT / '.analysis'
    name = args.path.removeprefix('.analysis/').rstrip('/')
    rows = records(analysis)
    if args.action == 'list':
        for row in rows:
            if name in row['path']:
                print(f"{row['path']}  {row['original_bytes']:,} -> {row['archive_bytes']:,} bytes  {row['archive']}")
        return
    selected = next((r for r in rows if name == r['path'] or
                     args.action == 'show' and any(m['path'] == name for m in r.get('members', []))), None)
    if selected is None:
        raise ValueError('No indexed evidence matches this path; use list')
    if args.action == 'restore':
        print(restore(analysis, selected))
    else:
        for member, data, _ in payloads(analysis, selected):
            if member == name:
                sys.stdout.buffer.write(data)
                return
        raise ValueError('show requires one file path within the archived directory')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
