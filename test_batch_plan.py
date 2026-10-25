import unittest,tempfile,csv
from pathlib import Path
from batch_plan import build_plan,FIELDS,STYLES
class PlanTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name);self.a=self.p/'assets';self.a.mkdir();(self.a/'a.png').write_bytes(b'image');self.row=['one','a.png','a.png','a.png','a.png','front']
 def plan(self,rows,fields=FIELDS):
  p=self.p/'jobs.csv'
  with p.open('w',newline='') as f:w=csv.writer(f);w.writerow(fields);w.writerows(rows)
  return build_plan(p,self.a,self.p/'out')
 def test_six_presets(self):self.assertEqual(len(self.plan([[s,*self.row[1:5],s] for s in STYLES])),6)
 def test_duplicate_casefold(self):
  with self.assertRaisesRegex(ValueError,'Duplicate'):self.plan([self.row,['ONE',*self.row[1:]]])
 def test_output_escape(self):
  with self.assertRaises(ValueError):self.plan([['../bad',*self.row[1:]]])
 def test_asset_escape(self):
  with self.assertRaises(ValueError):self.plan([['one','../a.png',*self.row[2:]]])
 def test_missing_asset(self):
  with self.assertRaises(ValueError):self.plan([['one','missing.png',*self.row[2:]]])
 def test_unknown_style(self):
  with self.assertRaisesRegex(ValueError,'Unknown'):self.plan([[*self.row[:-1],'wrong']])
 def test_existing_output(self):
  (self.p/'out').mkdir();(self.p/'out/one.png').write_bytes(b'old')
  with self.assertRaisesRegex(ValueError,'already exists'):self.plan([self.row])
 def test_header(self):
  with self.assertRaisesRegex(ValueError,'header'):self.plan([self.row],FIELDS[::-1])
 def test_hash_changes(self):
  a=self.plan([self.row])[0]['images']['cardfront_name']['sha256'];(self.a/'a.png').write_bytes(b'changed');b=self.plan([self.row])[0]['images']['cardfront_name']['sha256'];self.assertNotEqual(a,b)
 def test_empty(self):
  with self.assertRaisesRegex(ValueError,'no jobs'):self.plan([])
 def test_all_four_slots(self):self.assertEqual(len(self.plan([self.row])[0]['images']),4)
 def test_absolute_asset(self):
  with self.assertRaises(ValueError):self.plan([['one',str(self.a/'a.png'),*self.row[2:]]])
if __name__=='__main__':unittest.main()
