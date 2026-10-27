"""Catalog generation must not depend on a Windows user's legacy code page."""
import json
import runpy
from pathlib import Path


def test_catalog_export_preserves_unicode_under_a_legacy_default(monkeypatch):
    script=Path(__file__).resolve().parents[1]/'scripts/export_catalog.py'
    writes=[]
    def write_with_windows_default(path,data,encoding=None,errors=None,newline=None):
        # A Windows locale defaults to cp1252, which cannot encode Greek Gamma.
        encoded=data.encode(encoding or 'cp1252',errors or 'strict')
        writes.append(json.loads(encoded.decode('utf-8')))
        return len(data)
    monkeypatch.setattr(Path,'write_text',write_with_windows_default)
    runpy.run_path(str(script),run_name='__main__')
    assert len(writes)==1
    assert any(tab['id']=='geometry' for tab in writes[0])
