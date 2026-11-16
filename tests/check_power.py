#!/usr/bin/env python3
"""Test menu dispatch with stubs: never run a real power/lock command."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

BASE=Path(__file__).resolve().parents[1]

class PowerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='x13s-power-test-')
        self.addCleanup(self.tmp.cleanup)
        self.h=Path(self.tmp.name);self.bin=self.h/'.local/bin';self.bin.mkdir(parents=True)
        self.log=self.h/'calls'
        for name,text in {
            'x13s-lock':'echo lock >> "$CALL_LOG"; exit "${LOCK_STATUS:-0}"',
            'systemctl':'echo "systemctl $*" >> "$CALL_LOG"',
            'swaymsg':'echo "swaymsg $*" >> "$CALL_LOG"',
            'fuzzel':'cat >/dev/null; printf "%s\\n" "${CHOICE:-キャンセル}"; exit "${CHOOSER_STATUS:-0}"',
        }.items():
            p=self.bin/name;p.write_text('#!/bin/sh\n'+text+'\n');p.chmod(0o755)
        self.env=dict(os.environ,HOME=str(self.h),PATH=str(self.bin)+':'+os.environ['PATH'],CALL_LOG=str(self.log))

    def invoke(self,action,**env):
        return subprocess.run(['sh',str(BASE/'bin/x13s-power'),action],env=dict(self.env,**env),capture_output=True,text=True)

    def calls(self):return self.log.read_text().splitlines() if self.log.exists() else []

    def test_cancel_and_escape_do_nothing(self):
        for action in ('logout','reboot','poweroff'):
            self.assertEqual(self.invoke(action).returncode,0)
            self.assertEqual(self.invoke(action,CHOOSER_STATUS='1').returncode,0)
        self.assertEqual(self.calls(),[])

    def test_explicit_confirmation_dispatches_expected_action(self):
        for action,label,expected in [('logout','ログアウト','swaymsg exit'),('reboot','再起動','systemctl reboot'),('poweroff','電源オフ','systemctl poweroff')]:
            self.assertEqual(self.invoke(action,CHOICE=label+'する').returncode,0)
            self.assertEqual(self.calls()[-1],expected)

    def test_suspend_locks_first_and_stops_if_lock_fails(self):
        self.assertNotEqual(self.invoke('suspend',LOCK_STATUS='1').returncode,0)
        self.assertEqual(self.calls(),['lock'])
        self.log.unlink()
        self.assertEqual(self.invoke('suspend').returncode,0)
        self.assertEqual(self.calls(),['lock','systemctl suspend'])

    def test_unknown_action_is_rejected(self):
        self.assertEqual(self.invoke('unsupported').returncode,2)
        self.assertEqual(self.calls(),[])

    def test_menu_ids_match_dispatch_commands(self):
        tree=ET.parse(BASE/'config/waybar/power-menu.xml')
        ids={o.attrib['id'] for o in tree.findall('.//object')}
        d=json.loads((BASE/'config/waybar/config.jsonc').read_text())['custom/host']
        self.assertEqual(d['menu'],'on-click')
        for action,command in d['menu-actions'].items():
            self.assertIn(action,ids)
            self.assertEqual(command,'~/.local/bin/x13s-power '+action)

if __name__=='__main__':unittest.main(verbosity=2)
