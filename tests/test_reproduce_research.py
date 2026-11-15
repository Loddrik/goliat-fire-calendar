import sys
import tempfile
import unittest
import subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from reproduce_research import validate_checkout,deadline_timestamp

class ReproductionGuardTests(unittest.TestCase):
 def test_rejects_same_and_nested_directories_before_any_write(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'source';root.mkdir()
   for dest in [root,root/'child',root.parent]:
    with self.assertRaisesRegex(ValueError,'outside'):validate_checkout(root,dest)
   self.assertEqual(list(root.iterdir()),[])

 def test_rejects_dirty_or_different_commit_checkouts(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'source';root.mkdir();dest=Path(d)/'destination'
   def git(path,*args):return subprocess.run(['git',*args],cwd=path,check=True,capture_output=True,text=True)
   git(root,'init');git(root,'config','user.name','Test');git(root,'config','user.email','test@example.invalid');git(root,'config','commit.gpgsign','false')
   (root/'input').write_text('pinned');git(root,'add','input');git(root,'commit','-m','fixture')
   subprocess.run(['git','clone','--local',str(root),str(dest)],check=True,capture_output=True)
   self.assertEqual(validate_checkout(root,dest),dest.resolve())
   (dest/'input').write_text('changed')
   with self.assertRaisesRegex(ValueError,'clean'):validate_checkout(root,dest)
   git(dest,'checkout','--','input');(root/'input').write_text('new');git(root,'add','input');git(root,'commit','-m','new')
   with self.assertRaisesRegex(ValueError,'commits differ'):validate_checkout(root,dest)

 def test_deadline_requires_timezone_and_reserve(self):
  with self.assertRaisesRegex(ValueError,'UTC offset'):deadline_timestamp('2030-01-01T00:00:00')
  with self.assertRaisesRegex(ValueError,'reserve'):deadline_timestamp('2000-01-01T00:00:00Z')
  future=datetime.now(timezone.utc)+timedelta(hours=1)
  self.assertAlmostEqual(deadline_timestamp(future.isoformat()),future.timestamp())

if __name__=='__main__':unittest.main()
