"""Generate the checked-in legacy operation reference from the catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'assets/catalog.json'
OUTPUT = ROOT / 'docs/LEGACY_API.md'


def escape(value):
    return str('' if value is None else value).replace('|', r'\|').replace('\n', ' ')


def render(catalog):
    lines = [
        '# Legacy calculator API — generated operation catalog',
        '',
        'This reference is generated from `assets/catalog.json` by `python3 scripts/export_legacy_docs.py`. Do not edit this table by hand.',
        '',
        'The legacy calculator is the current **tab-based** interface. It is not the unified graph API. Calls use `{ "tab": "...", "operation": "...", "values": {...} }` through `engine.run_json`. Inputs to `values` are strings; blank fields and defaults depend on the operation. Use `{ "action": "catalog" }` to retrieve the machine-readable catalog.',
        '',
        'Success returns `ok`, `expr`, `text`, `latex`, `lines`, `extras`, `inputs` and `reusable`; failure returns `ok:false` and `error`. A result marked `reusable` only means its scalar text can be reparsed, **not** that tensor/chart context is preserved.',
        '',
        'For typed cross-domain workflows use the [unified API](API.md). For a first UI example see [Getting started](GETTING_STARTED.md).',
        '',
    ]
    for tab in catalog:
        lines.extend([
            f"## {tab['name']} (`{tab['id']}`)",
            '',
            '| Operation ID | What it does | Input fields and defaults |',
            '| --- | --- | --- |',
        ])
        for op in tab['operations']:
            fields = '; '.join(
                f"`{f['key']}` = `{escape(f.get('default'))}`"
                for f in op['fields']
            )
            lines.append(f"| `{op['id']}` | {escape(op['description'])} | {fields} |")
        lines.append('')
    return '\n'.join(lines) + '\n'


def main():
    data = json.loads(CATALOG.read_text(encoding='utf-8'))
    OUTPUT.write_text(render(data), encoding='utf-8')


if __name__ == '__main__':
    main()
