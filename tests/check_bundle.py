#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parents[1]

def run(*args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs)

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='x13s-bundle-test-')
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)/'new-user'

    def apply(self):
        run('python3',str(BASE/'scripts/apply.py'),'--home',str(self.home))
        return sorted((self.home/'.local/state/x13s-sway/backups').glob('*/manifest.json'))[-1]

    def test_stage_portability(self):
        run('bash',str(BASE/'install.sh'),'--stage',str(self.home))
        for rel in ['.config/sway/config','.config/gtklock/config.ini']:
            s=(self.home/rel).read_text()
            self.assertNotIn('@HOME@',s)
            self.assertNotIn('/home/ktada',s)
            self.assertIn(str(self.home),s)
        self.assertTrue((self.home/'.azotebg').stat().st_mode & 0o100)
        run('sh','-n',str(self.home/'.azotebg'))
        json.loads((self.home/'.config/waybar/config.jsonc').read_text())

    def test_existing_symlink_restored_without_touching_its_target(self):
        original=Path(self.tmp.name)/'old-kitty.conf';original.write_text('old settings\n')
        dest=self.home/'.config/kitty/kitty.conf';dest.parent.mkdir(parents=True)
        dest.symlink_to(original)
        manifest=self.apply()
        self.assertFalse(dest.is_symlink())
        self.assertEqual(original.read_text(),'old settings\n')
        run('python3',str(BASE/'restore.py'),str(manifest))
        self.assertTrue(dest.is_symlink())
        self.assertEqual(dest.read_text(),'old settings\n')
        self.assertFalse((self.home/'.config/sway/config').exists())

    def test_later_edits_are_preserved(self):
        manifest=self.apply();dest=self.home/'.config/sway/config'
        dest.write_text('# later edit\n')
        result=subprocess.run(['python3',str(BASE/'restore.py'),str(manifest)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertEqual(dest.read_text(),'# later edit\n')
        run('python3',str(BASE/'restore.py'),str(manifest),'--force')
        self.assertFalse(dest.exists())

    def test_azote_choice_is_preserved(self):
        self.home.mkdir();p=self.home/'.azotebg';p.write_text('# custom wallpaper\n')
        manifest=self.apply()
        self.assertEqual(p.read_text(),'# custom wallpaper\n')
        self.assertNotIn('.azotebg',[f['path'] for f in json.loads(manifest.read_text())['files']])

    def test_wallpaper_is_copied_from_path_with_spaces(self):
        image=Path(self.tmp.name)/'wallpaper with spaces.png'
        image.write_bytes(b'\x89PNG\r\n\x1a\n')
        run('python3',str(BASE/'scripts/apply.py'),'--home',str(self.home),'--wallpaper',str(image))
        saved=self.home/'.local/share/backgrounds/x13s-wallpaper.png'
        self.assertEqual(saved.read_bytes(),image.read_bytes())
        script=(self.home/'.azotebg').read_text()
        self.assertIn(str(saved),script)
        self.assertNotIn(str(image),script)
        run('sh','-n',str(self.home/'.azotebg'))

    def test_dry_run_does_not_write(self):
        run('bash',str(BASE/'install.sh'),'--dry-run','--stage',str(self.home),'--lightdm')
        self.assertFalse(self.home.exists())

if __name__=='__main__':unittest.main(verbosity=2)
