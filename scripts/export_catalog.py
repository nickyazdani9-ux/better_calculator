"""Regenerate the lightweight local UI catalog after changing Python plugins."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
from engine import operation_catalog
(ROOT/'assets/catalog.json').write_text(json.dumps(operation_catalog(),ensure_ascii=False,indent=2)+'\n')
print('Updated assets/catalog.json')
