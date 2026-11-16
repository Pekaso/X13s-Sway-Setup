#!/usr/bin/env python3
"""Restore user files from one installation manifest; retain later edits by default."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('manifest', type=Path)
p.add_argument('--force', action='store_true', help='also replace files edited after installation')
a=p.parse_args()
m=json.loads(a.manifest.read_text()); h=Path(m['home'])
backup=a.manifest.resolve().parent
skipped=[]
for item in reversed(m['files']):
    rel=Path(item['path'])
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('Invalid backup path')
    target=h/rel
    exists=target.exists() or target.is_symlink()
    edited=exists and (target.is_symlink() or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256'])
    if edited and not a.force:
        skipped.append(str(target));continue
    if target.is_dir() and not target.is_symlink():
        raise RuntimeError(f'Refusing to remove a directory: {target}')
    if exists:target.unlink()
    if item['existed']:
        source=backup/'files'/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target,follow_symlinks=False)
for key,value in m.get('gsettings',{}).items():
    subprocess.run(['gsettings','set','org.gnome.desktop.interface',key,value],check=True)
if skipped:
    print('Kept later edits (use --force only to discard them):\n'+'\n'.join(skipped))
    raise SystemExit(1)
print('Restored user files. Packages and system files were not changed.')
