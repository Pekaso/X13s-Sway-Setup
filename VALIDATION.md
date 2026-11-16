# Validation — 2026-11-15

Baseline: ThinkPad X13s, Debian forky/sid, arm64.

Passed:

- Six isolated tests: staged install and portable paths, backup/symlink restore,
  later-edit protection, preservation of Azote selections, wallpaper copy,
  dry-run without writes.
- Generated configuration validated with installed Sway 1.12 (headless/pixman),
  foot 1.28, GTK3 CSS/GLib keyfile parsing, Waybar JSON parsing and shell syntax.
- apt-get simulation resolved the package list against the current Debian cache.

The installed desktop and system configuration were not changed while building
this bundle. No real fresh-OS installation, root system-file installation,
login authentication, or suspend/resume was performed as part of bundle tests.
Check these on the destination machine using README.ja.md section 6.
