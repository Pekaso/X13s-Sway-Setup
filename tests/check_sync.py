#!/usr/bin/env python3
"""Exercise live-to-template sync without reading the real user's config."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]

class SyncTests(unittest.TestCase):
    def test_preview_and_copy_of_symlink_with_home_normalization(self):
        with tempfile.TemporaryDirectory(prefix='x13s-sync-') as tmp:
            root=Path(tmp);repo=root/'repo';home=root/'desktop-user'
            (repo/'scripts').mkdir(parents=True)
            shutil.copy2(SOURCE/'sync-configs.py',repo/'sync-configs.py')
            shutil.copy2(SOURCE/'scripts/update-checksums.py',repo/'scripts/update-checksums.py')
            target=repo/'config/kitty/kitty.conf';target.parent.mkdir(parents=True)
            target.write_text('old\n')
            real=root/'actual-kitty.conf';real.write_text(f'include {home}/palette.conf\n')
            live=home/'.config/kitty/kitty.conf';live.parent.mkdir(parents=True);live.symlink_to(real)
            private=home/'.config/browser/token';private.parent.mkdir(parents=True);private.write_text('private')
            cmd=['python3',str(repo/'sync-configs.py'),'--home',str(home),'--skip-system']
            subprocess.run(cmd,check=True,capture_output=True)
            self.assertEqual(target.read_text(),'old\n')
            self.assertFalse((repo/'MANIFEST.sha256').exists())
            subprocess.run(cmd+['--apply'],check=True,capture_output=True)
            self.assertEqual(target.read_text(),'include @HOME@/palette.conf\n')
            self.assertFalse(target.is_symlink())
            self.assertTrue(live.is_symlink())
            self.assertFalse((repo/'config/browser').exists())
            subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=repo,check=True,capture_output=True)
            result=subprocess.run(cmd,check=True,capture_output=True,text=True)
            self.assertIn('0 file(s) would change',result.stdout)

if __name__=='__main__':unittest.main(verbosity=2)
