"""Replay observed live failures; no provider calls or new model costs."""
import json
import unittest
from pathlib import Path
from claim_workflow import Answer, Statement, source_specific_errors

ROOT=Path(__file__).resolve().parent

class RecordedFailureTests(unittest.TestCase):
    def test_observed_fir_and_provider_errors_are_now_withheld(self):
        report=json.loads((ROOT/'data/live-evaluation-before-retest.json').read_text(encoding='utf-8'))
        for case_id in ('05','06'):
            with self.subTest(case=case_id):
                case=next(c for c in report['cases'] if c['case']==case_id)
                # Historical drafts predate the quote schema. Construct only the
                # fields read by these local guards, keeping fixtures unchanged.
                draft=Answer.model_construct(statements=[Statement.model_construct(**s)
                    for s in case['result']['answer']['statements']],
                    clarification_questions=[],insufficient_evidence=False)
                errors=source_specific_errors(draft,case['result']['evidence'],case['question'])
                self.assertTrue(errors)

if __name__=='__main__': unittest.main()
