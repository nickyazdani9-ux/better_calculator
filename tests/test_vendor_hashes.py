"""Offline integrity regressions through the real vendoring entry point."""
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import vendor_pyodide as mirror


@pytest.fixture
def distribution(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    for filename in mirror.CORE:
        (source / filename).write_bytes(b'synthetic runtime')
    packages = {}
    for name in ('sympy', 'mpmath'):
        data = f'synthetic {name} wheel'.encode()
        (source / f'{name}.whl').write_bytes(data)
        packages[name] = {
            'file_name': f'{name}.whl',
            'sha256': hashlib.sha256(data).hexdigest(),
            'depends': ['mpmath'] if name == 'sympy' else [],
        }
    return source, tmp_path / 'dest', {'packages': packages}


def run(distribution):
    source, dest, lock = distribution
    (source / 'pyodide-lock.json').write_text(json.dumps(lock))
    return mirror.vendor(source.as_uri() + '/', dest)


@pytest.mark.parametrize('package', ['sympy', 'mpmath'])
@pytest.mark.parametrize('invalid', [None, '', 'a' * 63, 'g' * 64, 123, ['a' * 64]])
def test_invalid_hash_rejected_before_any_wheel_download(distribution, package, invalid):
    source, dest, lock = distribution
    lock['packages'][package]['sha256'] = invalid
    with patch.object(mirror, 'download', wraps=mirror.download) as download:
        with pytest.raises(ValueError, match='Invalid SHA256'):
            run(distribution)
    assert all(Path(call.args[1]).suffix != '.whl' for call in download.call_args_list)
    assert not list(dest.glob('*.whl'))


@pytest.mark.parametrize('package', ['sympy', 'mpmath'])
def test_missing_hash_rejected_before_any_wheel_download(distribution, package):
    source, dest, lock = distribution
    del lock['packages'][package]['sha256']
    with patch.object(mirror, 'download', wraps=mirror.download) as download:
        with pytest.raises(ValueError, match='Invalid SHA256'):
            run(distribution)
    assert all(Path(call.args[1]).suffix != '.whl' for call in download.call_args_list)
    assert not list(dest.glob('*.whl'))


def test_mismatched_wheel_is_not_installed(distribution):
    source, dest, _ = distribution
    (source / 'sympy.whl').write_bytes(b'corrupted source wheel')
    with pytest.raises(ValueError, match='Checksum mismatch'):
        run(distribution)
    assert not (dest / 'sympy.whl').exists()


def test_corrupted_cached_wheel_is_replaced_with_verified_bytes(distribution):
    source, dest, _ = distribution
    run(distribution)
    (dest / 'sympy.whl').write_bytes(b'corrupted cache')
    run(distribution)
    assert (dest / 'sympy.whl').read_bytes() == (source / 'sympy.whl').read_bytes()


def test_uppercase_hex_hash_is_accepted_and_normalized(distribution):
    source, dest, lock = distribution
    for entry in lock['packages'].values():
        entry['sha256'] = entry['sha256'].upper()
    run(distribution)
    assert (dest / 'sympy.whl').read_bytes() == (source / 'sympy.whl').read_bytes()
