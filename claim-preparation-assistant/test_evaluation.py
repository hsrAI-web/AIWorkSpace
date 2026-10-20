import json
import unittest
import tempfile
from pathlib import Path
from live_evaluation import run_suite

class Engine:
    def index(self,strategy): pass
    def search(self,*args,**kwargs):
        return [{'id':'e1','text':'Test evidence','pages':[1],'source_id':'M1'}]

class EvaluationTests(unittest.TestCase):
    def test_suite_records_all_cases_and_leaves_human_scores_pending(self):
        progress=[]
        generator=lambda _:json.dumps(dict(statements=[],clarification_questions=[],insufficient_evidence=True))
        verifier=lambda _:json.dumps(dict(supported=True,unsupported_statement_indexes=[],notes='No factual statements'))
        report=run_suite(Engine(),generator,'mock-model',lambda n,total:progress.append(n),verifier)
        self.assertEqual(report['automatic_summary']['safe_abstentions'],13)
        self.assertEqual(report['automatic_summary']['checklist_answers'],2)
        self.assertEqual(progress,list(range(1,16)))
        self.assertTrue(all(c['human_review']['expected_behavior_pass'] is None for c in report['cases']))
        self.assertNotIn('api_key',json.dumps(report))
    def test_provider_failure_does_not_erase_other_cases(self):
        def generator(_): raise RuntimeError('synthetic failure')
        report=run_suite(Engine(),generator,'mock-model')
        self.assertEqual(len(report['cases']),15)
        self.assertEqual(report['automatic_summary']['generated'],0)
        self.assertEqual(sum(c['result']['status']=='generation_failed' for c in report['cases']),12)
        self.assertEqual(report['cases'][-1]['result']['status'],'insufficient_evidence')
    def test_interrupted_suite_resumes_saved_cases_without_recalling_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint=Path(directory)/'progress.json'
            calls=[]
            def generator(payload):
                calls.append(payload['question'])
                return json.dumps(dict(statements=[],clarification_questions=[],insufficient_evidence=True))
            def interrupt(n,total):
                if n==1: raise RuntimeError('Simulated browser interruption')
            with self.assertRaises(RuntimeError):
                run_suite(Engine(),generator,'mock-model',interrupt,case_ids=['13','14'],checkpoint_path=checkpoint)
            self.assertEqual(json.loads(checkpoint.read_text())['completed_cases'],1)
            report=run_suite(Engine(),generator,'mock-model',case_ids=['13','14'],checkpoint_path=checkpoint)
            self.assertEqual(report['resumed_cached_cases'],1)
            self.assertEqual(len(calls),2)
            self.assertEqual(json.loads(checkpoint.read_text())['status'],'complete')

if __name__=='__main__': unittest.main()
