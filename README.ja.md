# ThinkPad X13s / Debian Sway — Tokyo Night セットアップ

2026-11-15の実機設定を基にした、設定ファイル・導入スクリプト・復元スクリプトのセットです。
ユーザー名は固定せず、実行したユーザーのホームへパスを置換します。
現在の環境へは自動適用していません。

## 1. 前提

- 対象はDebianのARM64版を導入済みのThinkPad X13s。
- 基準環境はDebian forky/sid。sway 1.12、gtklock 4.0、Waybar 0.15で確認。
- カーネル、ファームウェア、GPU、内蔵画面、キーボードが既に動作していること。
- 通常ユーザーのホームとsudo権限、apt用のネットワーク接続が必要。
- 最小構成からなら、先に `sudo apt install sudo python3` を実行する。
  sudoがまだ使えない場合はrootで導入・ユーザー権限を準備する。
- ホームのパスは英数字と `_`、`-`、`.`、`/` のみをサポート。
- Debianの他リリースではgtklock等の提供状況が異なる。Ubuntuや他ディストリビューション用の導入スクリプトではない。

OS導入、X13s専用カーネル／ファームウェア／音声UCM調整は含みません。
サスペンドや蓋を閉じたときの動作は、OSのlogind設定に従います。
今回の実機では蓋の開閉は正常でしたが、他のカーネルでの動作は保証しません。

## 2. まとめて導入

このフォルダをホームなどへ展開して、**通常ユーザーとして**実行します。
`sudo ./install.sh` では実行しないでください。必要な箇所だけスクリプトがsudoを使います。

```bash
cd ~/x13s-sway-setup
./install.sh --dry-run --lightdm
./install.sh --lightdm
```

LightDMテーマが不要なら、`./install.sh` だけで導入できます。
SDDM/GDM等を使用している場合は `--lightdm` を付けないでください。
LightDMを新規導入すると、aptから既定のディスプレイマネージャーを質問されることがあります。
LightDMを使う場合はlightdmを選びます。スクリプト自体は既定DMを強制変更しません。
GUIセッションを再起動したり、作業中のウィンドウを閉じたりはしません。

最初から壁紙も設定する場合：

```bash
./install.sh --lightdm --wallpaper "$HOME/Pictures/wallpaper.jpg"
```

壁紙はPNG/JPEG/WebPを指定できます。導入先の共有データディレクトリへコピーされ、
元ファイルを移動しても表示できます。画像は本セットには同梱していません。
未指定なら既存のAzote設定を維持し、設定がなければネイビー単色にします。

完了したら作業を保存してログアウトし、ログイン画面のセッションメニューから
**Sway (X13s Tokyo Night)** を選択します。
既存のXFCEや他のデスクトップは削除しません。
LightDMが未起動の最小環境では必要に応じて再起動してください。
TTYから試す場合は以下でも起動できます。

```bash
dbus-run-session ~/.local/bin/start-sway
```

### オプション

| オプション | 用途 |
| --- | --- |
| `--lightdm` | LightDM GTK Greeterの導入とテーマ適用 |
| `--wallpaper FILE` | 指定画像をコピーして自動復元 |
| `--skip-packages` | パッケージ導入済み環境でaptを省略 |
| `--no-dark` | GSettingsのダーク設定変更を省略 |
| `--dry-run` | 実行予定を表示。ファイル変更・sudo・apt通信なし |
| `--stage /tmp/new-directory` | 新しいディレクトリへユーザー設定だけ生成。システム変更なし |

`--stage` は新規の絶対パスを指定します。パッケージ導入・GSettings・システム側の適用はしません。
`--dry-run` はパッケージ依存関係の解決までは実行しません。

## 3. 何が導入されるか

| 対象 | 内容 |
| --- | --- |
| sway | Tokyo Night、細い枠、タイル、内蔵画面1.25倍、Caps→Ctrl、US配列 |
| Kitty | Super+Enterで起動する端末。透明度0.8、Tokyo Night、12pt |
| foot | 補助端末。ネットワーク設定等から使用 |
| Waybar | CPU・メモリ・Wi-Fi・音量・輝度・バッテリーのアイコン＋数値 |
| Nerd Fonts | Symbols Nerd Font Monoをユーザー領域へ導入。ライセンス同梱 |
| Fuzzel / Mako | アプリ検索・通知を同系色へ統一 |
| fcitx5 / Mozc | USキーボード＋日本語入力。既存のMozcユーザー辞書は含まない |
| Azote / swaybg | 選択した壁紙を `~/.azotebg` からログイン時に復元 |
| gtklock | ネイビー背景、大きな時計・日付・パスワード欄・解除ボタン |
| swaylock | gtklock未導入または起動失敗時の予備ロック |
| ポータル | 画面共有・撮影はwlr、設定・ファイル選択等はGTKへ振り分け |
| ダーク設定 | `color-scheme=prefer-dark` と `gtk-theme=Adwaita-dark` |
| LightDM（任意） | ネイビー、JetBrains Mono 14、中央配置、入力欄最小幅360px |

aptでは上記に加え、音量・輝度・メディアキー操作、撮影、フォント、日本語入力の依存パッケージ、
NetworkManager、pavucontrolを導入します。
音声サーバーやブラウザー、zsh、Starship、tmux自体の新規設定は行いません。
既存のシェル設定・履歴・認証情報・個人辞書は配布物に含めていません。

最小環境で音声サーバーが未導入なら、別途構成が必要です。例えばPipeWireを使う場合：

```bash
sudo apt install pipewire-pulse wireplumber
```

Firefox等のブラウザーは必要に応じて導入し、既定ブラウザーを設定してください。
Firefoxのテーマを「システムのテーマ — 自動」、Webサイトの外観を「自動」にすると
システムのダーク指定に追従できます。Qtアプリ独自のテーマは別途設定が必要な場合があります。
GSettingsの外観設定は同じユーザーの他のデスクトップセッションにも影響します。

## 4. キー操作

SuperはWindowsロゴキーです。

| キー | 操作 |
| --- | --- |
| Super+Enter | Kitty |
| Super+D | Fuzzelでアプリ検索 |
| Super+1〜0 | ワークスペース1〜10 |
| Super+Shift+1〜0 | ウィンドウを別ワークスペースへ移動 |
| Super+H/J/K/L、矢印 | フォーカス移動 |
| Super+Shift+H/J/K/L | ウィンドウ移動 |
| Super+V / Super+- | 次のウィンドウの分割方向を上下 / 左右へ |
| Super+E | タイル配置の切替（現在の実機設定を採用） |
| Super+W / Super+S | タブ / スタック配置 |
| Super+F | 全画面 |
| Super+Shift+Space | フローティング切替 |
| Super+R → H/J/K/L → Enter | サイズ変更 |
| Super+Ctrl+L | gtklockでロック |
| Super+Shift+C | sway設定の再読込 |
| Super+Shift+Q | 現在のウィンドウを閉じる |
| Super+Shift+E | ログアウト確認 |
| Print / Super+Print | 全画面 / 範囲撮影。保存してクリップボードへ |
| Ctrl+Space | fcitx5標準の入力方式切替 |

5分無操作でロック、10分で画面消灯、復帰時は画面を再点灯します。
スリープ前にもロックします。自動サスペンドや蓋スイッチ用の新規ルールは追加しません。

## 5. ハードウェアと見た目の調整

`~/.config/sway/local.conf` は本体設定の最後に読み込まれます。

```ini
# 読みやすくしたい場合
output eDP-1 scale 1.5

# JIS配列の場合
input type:keyboard xkb_layout jp
```

X13s実機のデバイス名をWaybarに設定しています。
別個体・別機種で必要なら `~/.config/waybar/config.jsonc` の次を変更します。

- バッテリー: `qcom-battmgr-bat`（`ls /sys/class/power_supply` で確認）
- 輝度: `backlight`（`ls /sys/class/backlight` で確認）
- 内蔵画面: `eDP-1`（`swaymsg -t get_outputs` で確認）

マウスはTrackPoint向けの中ボタン押下中スクロールを設定しています。
通常の外付けマウスで合わない場合は `input "type:pointer" scroll_method on_button_down` と
`scroll_button 274` を削除するか、対象のデバイス識別子を限定してください。

壁紙の変更は `azote` を起動して適用します。`exec ~/.azotebg` は設定済みなので、
以後はログインのたびに復元します。別の `output * bg ...` と併用しないでください。

フォント・色・入力欄の調整先：

- 端末: `~/.config/kitty/kitty.conf`、`~/.config/foot/foot.ini`
- バー: `~/.config/waybar/config.jsonc`、`style.css`
- ロック画面: `~/.config/gtklock/config.ini`、`style.css`
- LightDM: `/etc/lightdm/lightdm-gtk-greeter.conf`
- LightDM CSS: `/usr/share/themes/X13s-Tokyo-Night/gtk-3.0/gtk.css`

輝度の表示はspanタグを使わずCSSでアイコンフォントを指定しています。
これによりツールチップにspanタグが文字として表示される問題を回避しています。
LightDMの中央配置は `position=50%,center 50%,center`、入力幅はCSSの `min-width: 360px` です。

## 6. 確認

```bash
./verify.sh
```

sway・footの構文、Waybar JSON、gtklockのCSSとINI、補助シェルの構文を確認します。
フォント確認結果は `SymbolsNerdFontMono-Regular.ttf` が目安です。
構文確認では画面をロックしません。インストーラーも実行中のswayやswayidleを再起動しません。
変更をすべて反映するため、導入後に一度ログアウトして入り直してください。

ログイン後は以下を実際に確認します。

1. Super+Enterで端末、Super+Dでアプリ検索。
2. Ctrl+SpaceでMozcへ切替、日本語を入力できること。
3. Waybarのアイコンが欠けず、音量・輝度キーが機能すること。
4. Super+Ctrl+Lで時計と入力欄を表示し、パスワードで解除できること。
5. Azoteで変更後に再ログインして壁紙を復元できること。
6. 保存後、蓋の開閉・スリープ復帰と解除を確認。
7. LightDMを適用した場合は、次のログイン画面で中央位置と入力幅を確認。

ポータルが返すダーク設定の確認：

```bash
gdbus call --session --dest org.freedesktop.portal.Desktop \
  --object-path /org/freedesktop/portal/desktop \
  --method org.freedesktop.portal.Settings.Read \
  org.freedesktop.appearance color-scheme
```

`(<uint32 1>,)` ならダーク指定です。

## 7. バックアップ・復元

適用先に同名ファイルがあれば、毎回別のバックアップへ保存します。
ユーザー設定はコピーして配置するので、展開したフォルダを後で移動しても動作します。
導入スクリプトを再実行すると、このセットの内容へ設定を再配置します。
以後の手修正を残したい場合は先にセット側へ取り込んでください。

### ユーザー設定

導入時に表示される次のmanifestを使います。

```text
~/.local/state/x13s-sway/backups/install-XXXXXXXX/manifest.json
```

```bash
python3 restore.py "$HOME/.local/state/x13s-sway/backups/install-XXXXXXXX/manifest.json"
```

導入前のファイルは復元し、新規に作ったファイルは削除します。既存シンボリックリンクも復元します。
導入後に編集したファイルは保護して残します。編集内容を破棄して戻す場合だけ `--force` を付けます。
ダーク指定を変更した場合は元のGSettings値も復元します。復元はそのユーザーの通常端末で行ってください。
複数回導入した場合は、新しいバックアップから順に戻します。

### システム設定

ログインセッション定義、LightDM設定、テーマCSSの元ファイルは以下へ保存されます。

```text
/var/lib/x13s-sway/backups/install.XXXXXXXX/
```

導入時に表示されるコマンドで戻します。

```bash
sudo bash /var/lib/x13s-sway/backups/install.XXXXXXXX/restore.sh
```

システム側の復元は導入後の手修正も上書きします。必要なら先に保存してください。
パッケージのアンインストール、既定ディスプレイマネージャーの変更やサービス再起動は行いません。
LightDMをその場で再起動すると作業中のセッションが終了するため、通常は次のログアウト・再起動で確認します。

## 8. 本セットの検証範囲

`tests/check_bundle.py` で、新規生成・別ホームへのパス置換・バックアップ・シンボリックリンク復元・
導入後の編集保護・Azote選択の維持・空白を含む画像パスからのコピー・dry-runを一時ディレクトリ上で確認します。

```bash
python3 tests/check_bundle.py
```

作成時には実機上のパッケージ候補でapt導入シミュレーションを行い、
一時ホームへ生成したsway等の構文も確認しています。
まっさらなOSへの実インストールやrootによるシステム設定適用は、このセットの検証では未実行です。
既存の実機で動作した設定を基にしていますが、初回の画面表示・認証・サスペンドは導入先で確認してください。

## 9. 参考と同梱フォント

- Sway: https://github.com/swaywm/sway
- gtklock: https://github.com/jovanlanik/gtklock
- Azote: https://github.com/nwg-piotr/azote
- LightDM GTK Greeter: https://github.com/Xubuntu/lightdm-gtk-greeter
- Nerd Fonts: https://github.com/ryanoasis/nerd-fonts

同梱のSymbols Nerd Font Monoは既存実機に導入した公式配布物です。
`fonts/LICENSE` と `fonts/README.md` に上流のライセンスと説明を同梱しています。

## 10. Gitでの管理と実機設定の取り込み

このフォルダをGitリポジトリとして管理します。実機の設定は通常どおり編集し、
変更を残したいタイミングで次を実行してください。

```bash
cd ~/Projects/x13s-sway-setup  # 配置先に合わせる
python3 sync-configs.py       # 取り込み予定だけ表示
python3 sync-configs.py --apply

git diff --stat
git diff                     # 内容を確認
python3 tests/check_bundle.py
python3 tests/check_sync.py
git add .
git commit -m "Update desktop configuration"
```

`sync-configs.py` がコピーする対象は、リポジトリの `config/` に既に存在する設定ファイルと、
`bin/` に存在する補助スクリプト、LightDMのgreeter設定・テーマCSSです。
現在のホームパスは `@HOME@` へ戻して保存するので、別ユーザーでも導入できます。
リンクされている設定ファイルもリンク先の内容を通常ファイルとしてコピーします。
実機の設定や元のリンク先は変更せず、Gitのadd・commit・pushも自動では行いません。

存在しない実機ファイルはスキップし、リポジトリの既存内容を維持します。
初回は現在の設定をコピー済みです。以後は `--apply` の実行で取り込みます。
`--skip-system` を付けるとLightDMのシステム設定を除外できます。

ブラウザープロファイル、トークン、履歴、個人辞書、壁紙画像、GSettings/dconfの全体は取り込みません。
Nerd Fontsも同梱済みのファイルを維持します。外観のGSettings値は導入スクリプト側で管理しています。
ポータル設定は導入時にスクリプトが生成します。変更する場合は `scripts/apply.py` を編集してください。
新しい設定ファイルも管理したい場合は、対応するパスを `config/` に追加すると次回から取り込み対象になります。
ただしバイナリーや認証情報を追加しないでください。

Gitの名前・メールが未設定の場合は、ご自身の情報を設定してから最初のコミットを作成してください。
このリポジトリだけに設定するなら、`--global` は付けません。

```bash
git config user.name "Your Name"
git config user.email "your-address@example.com"
git add .
git commit -m "Initial X13s Sway setup"
```

チェックサムは `sync-configs.py --apply` で更新されます。
手順書・スクリプトを手動編集した場合は、コミット前に次を実行します。

```bash
python3 scripts/update-checksums.py
sha256sum -c MANIFEST.sha256
```

以前作成した `../x13s-sway-setup.tar.gz` は自動では更新しません。
新しい配布アーカイブを作る場合は、Git情報を含めずに書き出します。

```bash
git archive --format=tar.gz --prefix=x13s-sway-setup/ \
  -o ../x13s-sway-setup.tar.gz HEAD
```

`git archive` に入るのはコミット済みの内容です。先に変更をコミットしてください。
リモートリポジトリは設定していません。必要に応じて追加し、内容を確認してからpushしてください。


## 11. ホスト名から電源メニュー

Waybarの `custom/host` を左クリックすると、クリック位置にGTKのリストメニューを表示します。
Waybar内蔵の `menu=on-click` を使用し、追加の電源メニューパッケージは不要です。

- ロック: 既存の `x13s-lock` を実行。
- スリープ: ロック完了後に `systemctl suspend`。ロック失敗時はスリープしません。
- ログアウト・再起動・電源オフ: Fuzzelで確認してから実行。初期選択はキャンセルです。
- メニュー外クリックやEscapeで閉じられます。

設定は `config/waybar/power-menu.xml`、`config/waybar/config.jsonc`、
`config/waybar/style.css` と `bin/x13s-power` に保存しています。
ホスト名が画面の左右どちらに配置されていても動作します。
実機側を編集した後は `python3 sync-configs.py --apply` で取り込めます。

```bash
python3 tests/check_power.py
```

このテストは電源操作・ロック操作をすべてスタブへ置き換え、確認のキャンセル・実行先・
スリープ前のロック順序を確認します。実際にログアウト・再起動等は行いません。
