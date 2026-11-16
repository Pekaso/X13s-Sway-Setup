#!/usr/bin/env bash
set -euo pipefail
base=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
lightdm=0; packages=1; stage=''; wallpaper=''; dark=1; dry=0
usage() {
  cat <<'HELP'
Usage: ./install.sh [--lightdm] [--wallpaper FILE] [--skip-packages]
                    [--no-dark] [--dry-run] [--stage DIRECTORY]
  --lightdm       Install LightDM GTK greeter theme as well
  --wallpaper     Copy a wallpaper and restore it on login (default: navy)
  --skip-packages Use already installed packages
  --no-dark       Do not change GSettings appearance preferences
  --dry-run       Print plan; do not write, install or contact sudo
  --stage DIR     Render user files into an empty absolute directory only
HELP
}
while (($#)); do
  case "$1" in
    --lightdm) lightdm=1; shift;;
    --skip-packages) packages=0; shift;;
    --no-dark) dark=0; shift;;
    --dry-run) dry=1; shift;;
    --stage|--wallpaper)
      (($# >= 2)) || { usage; exit 2; }
      case "$1" in --stage) stage=$2;; --wallpaper) wallpaper=$2;; esac
      shift 2;;
    -h|--help) usage; exit 0;;
    *) usage; exit 2;;
  esac
done
if [[ -n "$stage" ]]; then
  [[ "$stage" = /* && ! -e "$stage" ]] || { echo '--stage requires a new absolute directory' >&2; exit 2; }
  packages=0; dark=0
fi
command -v python3 >/dev/null || { echo 'Install python3 first.' >&2; exit 1; }
[[ -z "$wallpaper" || -f "$wallpaper" ]] || { echo 'Wallpaper not found' >&2; exit 2; }
if ((dry)); then
  printf 'User target: %s\nPackages: %s\nLightDM theme: %s\nDark preference: %s\nWallpaper: %s\n' "${stage:-$HOME}" "$packages" "$lightdm" "$dark" "${wallpaper:-existing Azote selection, otherwise navy}"
  exit 0
fi
((EUID != 0)) || { echo 'Run as your normal desktop user, not sudo ./install.sh' >&2; exit 1; }
# Paths are embedded in Sway commands; refuse ambiguous shell/config characters.
[[ "${stage:-$HOME}" =~ ^/[a-zA-Z0-9_./-]+$ ]] || { echo 'Home/staging path must use letters, digits, _, -, / and .' >&2; exit 2; }
if ((packages)); then
  pkgs=(sway swaybg swayidle swaylock gtklock waybar kitty foot fuzzel mako-notifier
        grim slurp wl-clipboard brightnessctl playerctl pulseaudio-utils libnotify-bin
        xdg-desktop-portal xdg-desktop-portal-wlr xdg-desktop-portal-gtk
        fonts-jetbrains-mono fonts-noto-cjk adwaita-icon-theme
        fcitx5 fcitx5-mozc fcitx5-frontend-gtk3 fcitx5-frontend-qt6
        azote pavucontrol xdg-utils network-manager dbus dbus-user-session
        libglib2.0-bin gsettings-desktop-schemas python3-gi gir1.2-gtk-3.0)
  if ((lightdm)); then pkgs+=(lightdm lightdm-gtk-greeter); fi
  sudo apt-get update
  sudo apt-get install "${pkgs[@]}"
fi
args=(--home "${stage:-$HOME}")
[[ -z "$wallpaper" ]] || args+=(--wallpaper "$wallpaper")
((dark)) && args+=(--dark)
python3 "$base/scripts/apply.py" "${args[@]}"
if [[ -n "$stage" ]]; then
  echo "Staged user files only: $stage (no packages, GSettings or system files changed)"
  exit 0
fi
fc-cache -f "$HOME/.local/share/fonts/X13s-NerdSymbols"
WLR_BACKENDS=headless WLR_RENDERER=pixman sway --validate --config "$HOME/.config/sway/config"
foot --check-config
sudo bash "$base/scripts/install-system.sh" "$base" "$HOME" "$lightdm"
printf '\nInstalled. Save your work and log out, then choose Sway (X13s Tokyo Night).\n'
printf 'Existing sessions have not been restarted. See README.ja.md for verification and rollback.\n'
