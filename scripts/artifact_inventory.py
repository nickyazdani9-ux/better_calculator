#!/usr/bin/env python3
"""Inventory existing bundle bytes without executing or extracting package code.

This receipt is evidence for review, not authenticated provenance or licence
clearance. Run only against a quiescent build directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile


REQUIRED_NOTICES = ('LICENSE', 'licenses/KATEX-LICENSE', 'licenses/PYODIDE-LICENSE')
REQUIRED_WHEEL_EVIDENCE = ('METADATA', 'RECORD', 'WHEEL')
MAX_MEMBERS = 10000
MAX_EVIDENCE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_EVIDENCE_BYTES = 32 * 1024 * 1024


def digest_stream(stream):
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
        size += len(block)
    return size, digest.hexdigest()


def notice_path(name):
    parts = name.lower().split('/')
    basename = parts[-1]
    return ('licenses' in parts[:-1] or 'licences' in parts[:-1]
            or re.match(r'^(licen[cs]e|copying|copyright|notice)([._-]|$)', basename) is not None)


def wheel_evidence(path, relative):
    evidence = []
    required_found = set()
    notice_found = False
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > MAX_MEMBERS:
                raise ValueError(f'Wheel member count limit exceeded: {relative}')
            seen = set()
            dist_info_directories = set()
            total = 0
            for member in sorted(members, key=lambda entry: entry.filename):
                name = member.filename
                clean = name[:-1] if member.is_dir() else name
                if (not clean or '\\' in name or ':' in name or '\x00' in name
                        or any(part in ('', '.', '..') for part in clean.split('/'))):
                    raise ValueError(f'Unsafe wheel member path: {relative}: {name}')
                if name in seen:
                    raise ValueError(f'Duplicate wheel member: {relative}: {name}')
                seen.add(name)
                top_level = clean.split('/')[0]
                if top_level.endswith('.dist-info'):
                    dist_info_directories.add(top_level)
                    if len(dist_info_directories) > 1:
                        raise ValueError(f'Ambiguous wheel dist-info directories: {relative}')
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f'Wheel symlink rejected: {relative}: {name}')
                if member.is_dir():
                    continue
                parts = name.split('/')
                required = (len(parts) == 2 and parts[0].endswith('.dist-info')
                            and parts[1] in REQUIRED_WHEEL_EVIDENCE)
                notice = notice_path(name)
                if not required and not notice:
                    continue
                total += member.file_size
                if member.file_size > MAX_EVIDENCE_BYTES or total > MAX_TOTAL_EVIDENCE_BYTES:
                    raise ValueError(f'Wheel evidence size limit exceeded: {relative}: {name}')
                with archive.open(member) as stream:
                    size, digest = digest_stream(stream)
                evidence.append({'path': name, 'size': size, 'sha256': digest})
                if required and (size or parts[1] == 'RECORD'):
                    required_found.add(parts[1])
                notice_found = notice_found or notice
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError) as exc:
        raise ValueError(f'Unreadable wheel: {relative}: {exc}') from exc
    return {'path': relative, 'evidence_members': evidence,
            'missing_required_evidence': sorted(set(REQUIRED_WHEEL_EVIDENCE) - required_found),
            'notice_members_found': notice_found, 'notice_review': 'required'}


def inventory(root, source_revision):
    root = Path(root)
    if not re.fullmatch(r'[0-9a-fA-F]{40}', source_revision):
        raise ValueError('source revision must be a full 40-character Git SHA')
    if root.is_symlink():
        raise ValueError('Artifact root symlink rejected')
    if not root.is_dir():
        raise ValueError('Artifact directory does not exist')
    files = []
    wheels = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f'Artifact symlink rejected: {relative}')
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f'Nonregular artifact file rejected: {relative}')
        with path.open('rb') as stream:
            size, digest = digest_stream(stream)
        files.append({'path': relative, 'size': size, 'sha256': digest})
        if path.suffix.lower() == '.whl':
            wheels.append(wheel_evidence(path, relative))
    file_sizes = {entry['path']: entry['size'] for entry in files}
    return {'schema_version': 1, 'source_revision': source_revision.lower(),
            'provenance_authenticated': False, 'licence_clearance': False,
            'files': files, 'wheels': wheels,
            'missing_required_notices': [name for name in REQUIRED_NOTICES if not file_sizes.get(name)],
            'review_required': ['Runtime, stdlib, font and native-shell obligations',
                                'Wheel notices and source obligations',
                                'Source-to-artifact provenance and upstream authenticity']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    temp = None
    try:
        root = args.artifact.resolve()
        output = args.output.resolve()
        if output == root or root in output.parents:
            raise ValueError('Inventory output must be outside the artifact directory')
        report = inventory(args.artifact, args.source_revision)
        # Write only after every input validates. Atomic replacement also avoids a
        # partial receipt if serialization or the filesystem write fails.
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=output.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
        os.replace(temp, output)
        temp = None
        gaps = report['missing_required_notices'] or any(
            wheel['missing_required_evidence'] for wheel in report['wheels'])
        return 2 if gaps else 0
    except (ValueError, OSError) as exc:
        print(f'Artifact inventory failed: {exc}', file=sys.stderr)
        return 1
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


if __name__ == '__main__':
    raise SystemExit(main())
