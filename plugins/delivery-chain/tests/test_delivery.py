import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

CLI=Path(__file__).resolve().parents[1]/'scripts/delivery.py'
SPEC=importlib.util.spec_from_file_location('delivery',CLI)
delivery=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(delivery)
A='snapshot:sha256:'+'a'*64
B='snapshot:sha256:'+'b'*64

class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name)
        self.run=self.project/'docs/quality/delivery-runs/demo'
        self.call('init','--project',str(self.project),'--run-id','demo','--title','Demo')
    def call(self,*args,ok=True):
        r=subprocess.run([sys.executable,str(CLI),*args],capture_output=True,text=True)
        if ok:self.assertEqual(r.returncode,0,r.stderr)
        else:self.assertNotEqual(r.returncode,0)
        return r
    def event(self,stage,outcome='PASS',**kw):
        return self.call('event','--run',str(self.run),'--stage',stage,'--outcome',outcome,'--evidence','test evidence',**kw)
    def freeze(self,c=A):self.call('freeze','--run',str(self.run),'--candidate',c)
    def data(self):return json.loads((self.run/'run.json').read_text())
    def test_initial_and_existing_run(self):
        self.assertEqual(self.data()['events'],[])
        self.call('init','--project',str(self.project),'--run-id','demo','--title','Other',ok=False)
        self.assertEqual(self.data()['title'],'Demo')
    def test_no_pass_before_candidate(self):self.event('verify',ok=False)
    def test_no_pass_without_evidence(self):
        self.freeze();self.call('event','--run',str(self.run),'--stage','verify','--outcome','PASS',ok=False)
    def test_gate_and_candidate_invalidation(self):
        self.freeze()
        for stage in ['build','verify','security','review']:self.event(stage)
        self.event('machine')
        self.event('final',ok=False)
        self.call('decision','--run',str(self.run),'--decision','APPROVED','--actor','User','--statement','Approved exact candidate','--candidate',A)
        self.event('final')
        self.freeze(B)
        state=delivery.frames(self.data())[-1]['stages']
        self.assertTrue(state['human']['stale']);self.assertTrue(state['review']['stale'])
        self.event('final',ok=False)
    def test_no_forged_human_stage(self):
        self.freeze();self.event('human',ok=False)
        self.call('decision','--run',str(self.run),'--decision','APPROVED','--actor','User','--statement','ok','--candidate',B,ok=False)
    def test_history_failure_retry(self):
        self.freeze();self.event('review','FAIL');self.event('build','NONE');self.event('review')
        fs=delivery.frames(self.data())
        self.assertEqual(fs[1]['stages']['review']['outcome'],'FAIL')
        self.assertEqual(fs[-1]['stages']['review']['outcome'],'PASS')
    def test_deployment_does_not_imply_approval(self):
        self.freeze();self.event('deploy')
        d=self.data();self.assertTrue(d['events'][-1]['before_approval'])
        self.assertEqual(delivery.frames(d)[-1]['stages']['human']['execution'],'pending')
    def approve_all(self):
        self.freeze()
        for stage in ['build','verify','security','review','machine']:self.event(stage)
        self.call('decision','--run',str(self.run),'--decision','APPROVED','--actor','User','--statement','Accepted current candidate')
        self.event('final')
    def test_failure_invalidates_downstream_same_candidate(self):
        self.approve_all();self.event('review','FAIL')
        state=delivery.frames(self.data())[-1]['stages']
        self.assertTrue(state['machine']['stale']);self.assertTrue(state['final']['stale'])
        self.freeze()  # Repeating the same hash cannot revive approvals.
        self.event('final',ok=False);self.event('deploy')
        self.assertTrue(self.data()['events'][-1]['before_final'])
    def test_deploy_other_candidate_has_no_approval(self):
        self.approve_all()
        self.call('event','--run',str(self.run),'--stage','deploy','--outcome','PASS','--candidate',B,'--evidence','test deployment')
        e=self.data()['events'][-1]
        self.assertTrue(e['before_approval']);self.assertTrue(e['before_final'])
    def test_running_decision_rejected(self):
        self.freeze()
        self.call('decision','--run',str(self.run),'--decision','APPROVED','--actor','User','--statement','Accepted','--execution','running',ok=False)
    def test_concurrent_writers(self):
        def write(i):self.event('plan','NONE')
        with ThreadPoolExecutor(max_workers=6) as p:list(p.map(write,range(12)))
        self.assertEqual([e['seq'] for e in self.data()['events']],list(range(1,13)))
    def test_script_injection_and_regeneration(self):
        note='</script><script>window.PWNED=1</script>'
        self.call('event','--run',str(self.run),'--stage','plan','--note',note)
        page=(self.run/'index.html').read_text()
        self.assertNotIn(note,page);self.assertIn('\\u003c/script',page)
        (self.run/'index.html').unlink();self.call('render','--run',str(self.run))
        self.assertTrue((self.run/'index.html').exists())
    def test_fingerprint_excludes_journal_and_test_output(self):
        (self.project/'app.txt').write_text('one')
        self.call('freeze','--run',str(self.run));first=self.data()['events'][-1]['candidate']
        (self.project/'test-results').mkdir();(self.project/'test-results/x').write_text('result')
        self.event('plan');self.call('freeze','--run',str(self.run))
        self.assertEqual(first,self.data()['events'][-1]['candidate'])
        (self.project/'app.txt').write_text('two');self.call('freeze','--run',str(self.run))
        self.assertNotEqual(first,self.data()['events'][-1]['candidate'])

if __name__=='__main__':unittest.main()
