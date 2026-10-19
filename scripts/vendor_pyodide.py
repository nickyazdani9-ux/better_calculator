#!/usr/bin/env python3
"""Mirror just the pinned Pyodide runtime + transitive SymPy wheels for offline use.

Always uses metadata returned by the matching pinned distribution's lockfile.
No dynamic evaluation, network calls from tests, or unpinned pip resolution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.parse
import urllib.request

VERSION = '0.29.5'
BASE_URL = f'https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/'
CORE = ('pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm',
        'python_stdlib.zip', 'pyodide-lock.json')
ROOT = Path(__file__).resolve().parent.parent


def packages_for(lock, roots=('sympy',)):
    packages = lock['packages']
    discovered = {}

    def visit(name):
        if name in discovered:
            return
        if name not in packages:
            raise ValueError(f'Missing Pyodide package: {name}')
        entry = packages[name]
        name_on_disk = entry['file_name']
        if Path(name_on_disk).name != name_on_disk or not name_on_disk:
            raise ValueError('Unsafe package path in lockfile')
        discovered[name] = entry
        for dependency in entry.get('depends', entry.get('dependencies', [])):
            visit(dependency)

    for name in roots:
        visit(name)
    return discovered


def download(url, destination, sha256=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.stat().st_size:
        if sha256 is None or hashlib.sha256(destination.read_bytes()).hexdigest() == sha256:
            return
    with urllib.request.urlopen(url, timeout=90) as resp:
        data = resp.read()
    if not data:
        raise ValueError(f'Empty download: {url}')
    if sha256 and hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError(f'Checksum mismatch: {url}')
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as file:
        file.write(data)
        temp = Path(file.name)
    os.replace(temp, destination)


def vendor(base_url=BASE_URL, dest=ROOT / 'vendor/pyodide'):
    dest = Path(dest)
    for item in CORE:
        download(urllib.parse.urljoin(base_url, item), dest / item)
    lock = json.loads((dest/'pyodide-lock.json').read_text())
    for name, entry in packages_for(lock).items():
        filename = entry['file_name']
        download(urllib.parse.urljoin(base_url, filename), dest/filename, entry.get('sha256'))
        print(f'Bundled {name}: {filename}')
    return dest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default=BASE_URL)
    parser.add_argument('--dest', type=Path, default=ROOT/'vendor/pyodide')
    args=parser.parse_args()
    vendor(args.base_url, args.dest)
