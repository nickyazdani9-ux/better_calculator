import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

from scripts.artifact_inventory import inventory


REVISION = 'a' * 40
SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/artifact_inventory.py'


class ArtifactInventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'dist'
        self.root.mkdir()
        for name in ('LICENSE', 'licenses/PYODIDE-LICENSE', 'licenses/KATEX-LICENSE'):
            path = self.root / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(b'synthetic notice')

    def wheel(self, entries=None):
        path = self.root / 'synthetic-1.0-py3-none-any.whl'
        if entries is None:
            entries = [('synthetic.dist-info/METADATA', b'Name: synthetic\nVersion: 1.0\n'),
                       ('synthetic.dist-info/WHEEL', b'Wheel-Version: 1.0\n'),
                       ('synthetic.dist-info/RECORD', b''),
                       ('synthetic.dist-info/licenses/MIT.txt', b'synthetic licence'),
                       ('synthetic/__init__.py', b'raise RuntimeError("do not execute")')]
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in entries:
                archive.writestr(name, data)
        return path

    def test_deterministic_sorted_files_and_supplied_revision(self):
        (self.root / 'z.wasm').write_bytes(b'wasm')
        first = inventory(self.root, REVISION)
        self.assertEqual(first, inventory(self.root, REVISION))
        self.assertEqual([x['path'] for x in first['files']],
                         sorted(x['path'] for x in first['files']))
        self.assertEqual(first['source_revision'], REVISION)
        self.assertFalse(first['provenance_authenticated'])
        self.assertFalse(first['licence_clearance'])

    def test_changes_in_actual_file_bytes_change_hash(self):
        path = self.root / 'runtime.wasm'
        path.write_bytes(b'first')
        first = inventory(self.root, REVISION)
        path.write_bytes(b'other')
        second = inventory(self.root, REVISION)
        a = next(x for x in first['files'] if x['path'] == 'runtime.wasm')
        b = next(x for x in second['files'] if x['path'] == 'runtime.wasm')
        self.assertNotEqual(a['sha256'], b['sha256'])
        self.assertEqual(b['sha256'], hashlib.sha256(b'other').hexdigest())

    def test_wheel_evidence_hashes_without_executing_or_extracting(self):
        self.wheel()
        report = inventory(self.root, REVISION)
        wheel = report['wheels'][0]
        self.assertEqual(wheel['missing_required_evidence'], [])
        self.assertEqual(wheel['notice_review'], 'required')
        members = {x['path']: x for x in wheel['evidence_members']}
        self.assertEqual(len(members), 4)
        self.assertEqual(members['synthetic.dist-info/licenses/MIT.txt']['sha256'],
                         hashlib.sha256(b'synthetic licence').hexdigest())
        self.assertFalse((self.root / 'synthetic.dist-info').exists())

    def test_missing_and_empty_notices_are_explicit(self):
        (self.root / 'LICENSE').unlink()
        (self.root / 'licenses/KATEX-LICENSE').write_bytes(b'')
        self.assertEqual(inventory(self.root, REVISION)['missing_required_notices'],
                         ['LICENSE', 'licenses/KATEX-LICENSE'])

    def test_missing_wheel_metadata_and_notice_are_explicit(self):
        self.wheel([('synthetic/__init__.py', b'')])
        wheel = inventory(self.root, REVISION)['wheels'][0]
        self.assertEqual(wheel['missing_required_evidence'], ['METADATA', 'RECORD', 'WHEEL'])
        self.assertFalse(wheel['notice_members_found'])

    def test_split_dist_info_directories_rejected(self):
        self.wheel([('first.dist-info/METADATA', b'Name: first\n'),
                    ('second.dist-info/WHEEL', b'Wheel-Version: 1.0\n'),
                    ('second.dist-info/RECORD', b'')])
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            inventory(self.root, REVISION)

    def test_extra_dist_info_directory_rejected(self):
        self.wheel([('first.dist-info/METADATA', b'Name: first\n'),
                    ('first.dist-info/WHEEL', b'Wheel-Version: 1.0\n'),
                    ('first.dist-info/RECORD', b''),
                    ('second.dist-info/', b'')])
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            inventory(self.root, REVISION)

    def test_empty_metadata_and_wheel_remain_missing_evidence(self):
        self.wheel([('synthetic.dist-info/METADATA', b''),
                    ('synthetic.dist-info/WHEEL', b''),
                    ('synthetic.dist-info/RECORD', b'')])
        wheel = inventory(self.root, REVISION)['wheels'][0]
        self.assertEqual(wheel['missing_required_evidence'], ['METADATA', 'WHEEL'])

    def test_missing_directory_rejected(self):
        with self.assertRaises(ValueError):
            inventory(self.root / 'absent', REVISION)

    def test_bad_revision_rejected(self):
        for value in ('main', 'a'*39, 'x'*40, ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                inventory(self.root, value)

    def test_filesystem_symlink_rejected(self):
        try:
            (self.root / 'linked').symlink_to(self.root / 'LICENSE')
        except OSError as exc:
            self.skipTest(str(exc))
        with self.assertRaisesRegex(ValueError, 'symlink'):
            inventory(self.root, REVISION)

    def test_directory_symlink_rejected(self):
        try:
            (self.root / 'linked').symlink_to(self.root / 'licenses', target_is_directory=True)
        except OSError as exc:
            self.skipTest(str(exc))
        with self.assertRaisesRegex(ValueError, 'symlink'):
            inventory(self.root, REVISION)

    def test_corrupt_wheel_rejected(self):
        (self.root / 'bad.whl').write_bytes(b'not a zip')
        with self.assertRaisesRegex(ValueError, 'wheel'):
            inventory(self.root, REVISION)

    def test_archive_unsafe_paths_rejected(self):
        for name in ('../outside', '/absolute', 'a\\b', 'C:/bad', './LICENSE', 'a//b'):
            with self.subTest(name=name):
                self.wheel([(name, b'not extracted')])
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    inventory(self.root, REVISION)

    def test_archive_duplicates_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            self.wheel([('LICENSE', b'a'), ('LICENSE', b'b')])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            inventory(self.root, REVISION)

    def test_archive_symlink_rejected(self):
        member = zipfile.ZipInfo('linked')
        member.create_system = 3
        member.external_attr = 0o120777 << 16
        self.wheel([(member, b'/outside')])
        with self.assertRaisesRegex(ValueError, 'symlink'):
            inventory(self.root, REVISION)

    def test_evidence_member_size_is_bounded(self):
        self.wheel([('LICENSE', b'x' * (8 * 1024 * 1024 + 1))])
        with self.assertRaisesRegex(ValueError, 'limit'):
            inventory(self.root, REVISION)

    def run_cli(self, output):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root),
                               '--output', str(output), '--source-revision', REVISION],
                              capture_output=True, text=True)

    def test_cli_refuses_output_inside_artifact_without_writing(self):
        output = self.root / 'inventory.json'
        result = self.run_cli(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_cli_writes_outside_artifact(self):
        self.wheel()
        output = Path(self.tmp.name) / 'inventory.json'
        result = self.run_cli(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text()), inventory(self.root, REVISION))

    def test_cli_reports_missing_evidence_and_nonzero_status(self):
        self.wheel([('synthetic/__init__.py', b'')])
        output = Path(self.tmp.name) / 'inventory.json'
        result = self.run_cli(output)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(json.loads(output.read_text())['wheels'][0]['missing_required_evidence'])


if __name__ == '__main__':
    unittest.main()
