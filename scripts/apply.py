#!/usr/bin/env python3
"""Render portable templates and back up every user file before replacement."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--home', type=Path, required=True)
p.add_argument('--wallpaper', type=Path)
p.add_argument('--dark', action='store_true')
a = p.parse_args()
if a.wallpaper and (not a.wallpaper.is_file() or a.wallpaper.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp')):
    p.error('Use an existing PNG/JPEG/WebP wallpaper')
h = a.home.absolute()
h.mkdir(parents=True, exist_ok=True)
state = h / '.local/state/x13s-sway/backups'
state.mkdir(parents=True, exist_ok=True)
backup = Path(tempfile.mkdtemp(prefix='install-', dir=state))
manifest = {'home': str(h), 'files': [], 'gsettings': {}}
manifest_path = backup / 'manifest.json'

def record():
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')

def put(rel, data, mode=0o644):
    target = h / rel
    # Do not follow pre-existing symlink directories into another config tree.
    for parent in target.parents:
        if parent == h:
            break
        if parent.is_symlink():
            raise RuntimeError(f'Refusing symlink directory: {parent}')
    if target.is_dir():
        raise RuntimeError(f'Expected a file, found directory: {target}')
    original = target.exists() or target.is_symlink()
    if original:
        saved = backup / 'files' / rel
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved, follow_symlinks=False)
    manifest['files'].append({'path': rel, 'existed': original, 'sha256': hashlib.sha256(data).hexdigest()})
    record()  # Keep partial installations recoverable, too.
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        target.unlink()
    target.write_bytes(data)
    target.chmod(mode)

for src in sorted((BASE / 'config').rglob('*')):
    if src.is_file():
        rel = '.config/' + src.relative_to(BASE / 'config').as_posix()
        put(rel, src.read_text().replace('@HOME@', str(h)).encode())
for src in sorted((BASE / 'bin').iterdir()):
    put('.local/bin/' + src.name, src.read_bytes(), 0o755)
for src in sorted((BASE / 'fonts').iterdir()):
    put('.local/share/fonts/X13s-NerdSymbols/' + src.name, src.read_bytes())
# Reproducible portal routing without relying on a distribution-specific default.
put('.config/xdg-desktop-portal/sway-portals.conf', b'''[preferred]
default=gtk
org.freedesktop.impl.portal.ScreenCast=wlr
org.freedesktop.impl.portal.Screenshot=wlr
org.freedesktop.impl.portal.Settings=gtk
''')
# Preserve an existing Azote choice unless a replacement was explicitly supplied.
if a.wallpaper:
    suffix = a.wallpaper.suffix.lower()
    if suffix not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise RuntimeError('Use a PNG/JPEG/WebP wallpaper')
    rel = '.local/share/backgrounds/x13s-wallpaper' + suffix
    put(rel, a.wallpaper.read_bytes())
    command = f'exec swaybg -m fill -i {shlex.quote(str(h / rel))}\n'
else:
    command = "exec swaybg -c '#1a1b26'\n"
if a.wallpaper or not (h / '.azotebg').exists():
    put('.azotebg', ('#!/bin/sh\npkill -u "$(id -u)" -x swaybg || true\n' + command).encode(), 0o755)
# A system-wide desktop file must point at the actual user's home.
put('.local/share/x13s-sway/session.desktop', f'''[Desktop Entry]
Name=Sway (X13s Tokyo Night)
Comment=Tokyo Night desktop for ThinkPad X13s
Exec={h}/.local/bin/start-sway
Type=Application
DesktopNames=sway
'''.encode())
if a.dark:
    # Bare TTY installs may have no session bus yet. Use a temporary D-Bus
    # session for persistent dconf writes, or reuse the systemd user bus.
    env = os.environ.copy()
    user_bus = Path(env.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')) / 'bus'
    if not env.get('DBUS_SESSION_BUS_ADDRESS') and user_bus.exists():
        env['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=' + str(user_bus)
    prefix = [] if env.get('DBUS_SESSION_BUS_ADDRESS') else ['dbus-run-session', '--']
    for key, value in [('color-scheme', 'prefer-dark'), ('gtk-theme', 'Adwaita-dark')]:
        previous = subprocess.check_output(prefix + ['gsettings', 'get', 'org.gnome.desktop.interface', key], text=True, env=env).strip()
        manifest['gsettings'][key] = previous
        record()
        subprocess.run(prefix + ['gsettings', 'set', 'org.gnome.desktop.interface', key, value], check=True, env=env)
record()
print('User backup / restore manifest:', manifest_path)
