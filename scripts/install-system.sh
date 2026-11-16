#!/usr/bin/env bash
set -euo pipefail
((EUID == 0)) || { echo 'This helper requires sudo.' >&2; exit 1; }
base=$1; target_home=$2; lightdm=$3
install -d -m 700 /var/lib/x13s-sway/backups
backup=$(mktemp -d /var/lib/x13s-sway/backups/install.XXXXXXXX)
chmod 700 "$backup"
# Keep a root-owned restore plan for every file changed.
restore="$backup/restore.sh"
printf '#!/bin/bash\nset -euo pipefail\n((EUID == 0)) || exit 1\n' > "$restore"
keep() {
  local dest=$1 saved="$backup/files$1"
  if [[ -e "$dest" || -L "$dest" ]]; then
    mkdir -p "$(dirname "$saved")"
    cp -a -- "$dest" "$saved"
    printf 'cp -a -- %q %q\n' "$saved" "$dest" >> "$restore"
  else
    printf 'rm -f -- %q\n' "$dest" >> "$restore"
  fi
}
session=/usr/share/wayland-sessions/x13s-sway.desktop
keep "$session"
install -D -m 644 "$target_home/.local/share/x13s-sway/session.desktop" "$session"
if [[ "$lightdm" == 1 ]]; then
  test -f /etc/lightdm/lightdm-gtk-greeter.conf || { echo 'LightDM GTK greeter configuration missing' >&2; exit 1; }
  theme=/usr/share/themes/X13s-Tokyo-Night/gtk-3.0/gtk.css
  conf=/etc/lightdm/lightdm-gtk-greeter.conf
  keep "$theme"
  keep "$conf"
  install -D -m 644 "$base/lightdm/X13s-Tokyo-Night/gtk-3.0/gtk.css" "$theme"
  python3 - "$base/lightdm/greeter.ini" "$conf" <<'PY'
import configparser, os, sys
from pathlib import Path
p=Path(sys.argv[2]); c=configparser.ConfigParser(interpolation=None,strict=False);c.read(p)
o=configparser.ConfigParser(interpolation=None);o.read(sys.argv[1])
if not c.has_section('greeter'):c.add_section('greeter')
for k,v in o.items('greeter'):c.set('greeter',k,v)
tmp=p.with_name(p.name+'.x13s-new')
with tmp.open('w') as f:c.write(f)
os.chmod(tmp,0o644);os.replace(tmp,p)
PY
fi
chmod 700 "$restore"
printf 'System backup: %s\nRestore command: sudo bash %s\n' "$backup" "$restore"
