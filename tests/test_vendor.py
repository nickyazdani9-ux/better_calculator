import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urljoin
from scripts.vendor_pyodide import packages_for, vendor, CORE

class VendorTests(unittest.TestCase):
    def test_transitive_packages(self):
        lock={'packages':{
            'sympy':{'file_name':'sympy.whl','depends':['mpmath']},
            'mpmath':{'file_name':'mpmath.whl','depends':[]},
        }}
        self.assertEqual(set(packages_for(lock)),{'sympy','mpmath'})

    def test_missing_dependency_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing Pyodide package'):
            packages_for({'packages':{'sympy':{'file_name':'s.whl','depends':['absent']}}})

    def test_unsafe_path_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unsafe package'):
            packages_for({'packages':{'sympy':{'file_name':'../oops'}}})

    def test_local_fixture_downloads_and_verifies_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'source'; base.mkdir()
            for item in CORE: (base/item).write_bytes(b'dummy')
            (base/'sympy.whl').write_bytes(b'fake sympy bytes')
            (base/'mpmath.whl').write_bytes(b'fake mpmath bytes')
            lock={'packages':{
                'sympy':{'file_name':'sympy.whl','depends':['mpmath'],'sha256':hashlib.sha256(b'fake sympy bytes').hexdigest()},
                'mpmath':{'file_name':'mpmath.whl','depends':[],'sha256':hashlib.sha256(b'fake mpmath bytes').hexdigest()},
            }}
            (base/'pyodide-lock.json').write_text(json.dumps(lock))
            output=vendor(base.as_uri()+'/',Path(tmp)/'dest')
            self.assertEqual((output/'mpmath.whl').read_bytes(),b'fake mpmath bytes')
            self.assertEqual((output/'sympy.whl').read_bytes(),b'fake sympy bytes')
            vendor(base.as_uri()+'/',output)  # repeatable

if __name__=='__main__': unittest.main()
