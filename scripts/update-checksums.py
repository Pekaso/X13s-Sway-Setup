#!/usr/bin/env python3
"""Regenerate the release file manifest, excluding Git metadata and local backups."""
from pathlib import Path
import hashlib

BASE = Path(__file__).resolve().parents[1]

def update(base=BASE):
    candidates = []
    for name in ('bin', 'config', 'fonts', 'lightdm', 'scripts', 'tests'):
        candidates.extend((base / name).rglob('*'))
    candidates.extend(p for p in base.iterdir() if p.suffix in ('.md', '.sh', '.py') or p.name == '.gitignore')
    lines = []
    for p in sorted(set(candidates)):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        if '.backup-' in p.name or p.suffix in ('.pyc', '.bak', '.swp') or p.name.endswith('~'):
            continue
        lines.append(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(base).as_posix())
    (base / 'MANIFEST.sha256').write_text('\n'.join(lines) + '\n')

if __name__ == '__main__':
    update()
