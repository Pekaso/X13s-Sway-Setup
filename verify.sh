#!/usr/bin/env bash
set -euo pipefail
target_home=${1:-$HOME}
# Validation only: does not lock the display or restart anything.
HOME="$target_home" XDG_CONFIG_HOME="$target_home/.config" WLR_BACKENDS=headless WLR_RENDERER=pixman \
  sway --validate --config "$target_home/.config/sway/config"
HOME="$target_home" XDG_CONFIG_HOME="$target_home/.config" foot --check-config
python3 - "$target_home" <<'PY'
import json,sys,configparser
from pathlib import Path
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
h=Path(sys.argv[1])
json.loads((h/'.config/waybar/config.jsonc').read_text())
c=configparser.ConfigParser(interpolation=None);c.read(h/'.config/gtklock/config.ini')
assert c.getboolean('main','idle-hide') is False
css=Gtk.CssProvider();css.load_from_path(str(h/'.config/gtklock/style.css'))
for name in ('start-sway','x13s-lock','sway-shot'):
 import subprocess
 subprocess.run(['sh','-n',str(h/'.local/bin'/name)],check=True)
print('Sway, foot, Waybar JSON, gtklock CSS/INI and shell syntax: OK')
PY
printf 'Nerd icon font: '
fc-match 'Symbols Nerd Font Mono'
printf '\nLive-session checks: Super+Return, Super+D, Super+Ctrl+L, IME, audio and brightness keys.\n'
