#!/usr/bin/env python3
"""Copy live configuration into this repository. Preview by default; use --apply to save."""
import argparse
import importlib.util
from pathlib import Path
import stat

BASE = Path(__file__).resolve().parent

def collect(repo, home, skip_system=False):
    sources = []
    # Only files already represented in the repository are eligible. Never sweep
    # all of ~/.config (browser profiles, tokens and histories do not belong here).
    for directory, live in [('config', home / '.config'), ('bin', home / '.local/bin')]:
        for target in sorted((repo / directory).rglob('*')):
            if target.is_file() and '.backup-' not in target.name and not target.name.endswith(('.bak', '~')):
                sources.append((live / target.relative_to(repo / directory), target))
    if not skip_system:
        sources.extend([
            (Path('/etc/lightdm/lightdm-gtk-greeter.conf'), repo / 'lightdm/greeter.ini'),
            (Path('/usr/share/themes/X13s-Tokyo-Night/gtk-3.0/gtk.css'),
             repo / 'lightdm/X13s-Tokyo-Night/gtk-3.0/gtk.css'),
        ])
    return sources

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true', help='save copies and regenerate MANIFEST.sha256')
    p.add_argument('--home', type=Path, default=Path.home(), help='source home directory')
    p.add_argument('--skip-system', action='store_true', help='skip system LightDM files')
    a = p.parse_args()
    home = a.home.expanduser().absolute()
    updates = []
    # Read and validate everything before any write. File symlinks are read as
    # content, so e.g. a kitty.conf link becomes a portable regular file.
    for source, target in collect(BASE, home, a.skip_system):
        if not source.is_file():
            print('SKIP (missing):', source)
            continue
        data = (source.read_text().replace(str(home), '@HOME@').rstrip('\n') + '\n').encode()
        if data != target.read_bytes():
            print('UPDATE:', target.relative_to(BASE), '<-', source)
            updates.append((target, data))
    if not a.apply:
        print(f'{len(updates)} file(s) would change. Run with --apply to save. No files changed.')
        return
    for target, data in updates:
        mode = stat.S_IMODE(target.stat().st_mode)
        if target.is_symlink():
            target.unlink()
        target.write_bytes(data)
        target.chmod(mode)
    spec = importlib.util.spec_from_file_location('checksums', BASE / 'scripts/update-checksums.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.update(BASE)
    print(f'Copied {len(updates)} file(s); regenerated MANIFEST.sha256. Nothing staged or committed.')

if __name__ == '__main__':
    main()
