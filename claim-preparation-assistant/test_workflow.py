import json
import unittest
from claim_workflow import UIN, build_graph, source_specific_errors, Answer, provider_draft_errors

class FakeRetriever:
    def search(self,*args,**kwargs):
        return [{'id':'e1','text':'Source passage','pages':[4],'source_id':'F1'}]

class WorkflowTests(unittest.TestCase):
    def test_live_status_is_out_of_scope_before_provider_call(self):
        def must_not_call(_): raise AssertionError('No status provider is connected')
        state=self.state(); state['question']='Will my claim definitely be approved, and what is its current status?'
        result=build_graph(FakeRetriever(),must_not_call).invoke(state)
        self.assertEqual(result['status'],'insufficient_evidence')
    def test_non_network_alternative_cannot_be_omitted(self):
        answer=Answer.model_construct(statements=[type('S',(),{'text':'A hospital registration certificate is required.'})()])
        self.assertTrue(source_specific_errors(answer,[{'text':'registration certificate or certificate from Hospital authorities providing facilities'}]))
    def test_first_consultation_does_not_match_fir(self):
        answer=Answer.model_validate(dict(statements=[dict(text='You need first consultation letters.',
            citations=['E1'],evidence_quotes=[dict(citation='E1',quote='First consultation letters')])],
            clarification_questions=[],insufficient_evidence=False))
        self.assertEqual(source_specific_errors(answer,[{'text':'MLC/FIR'}]),[])
    def test_provider_repair_rejects_unknown_alias(self):
        raw=json.dumps(dict(statements=[dict(text='A statement',citations=['document-M1'],
            evidence_quotes=[dict(citation='document-M1',quote='Source passage')])],
            clarification_questions=[],insufficient_evidence=False))
        self.assertIn('allowed_citations',provider_draft_errors(raw,{'allowed_citations':['E1']})[0])
    def test_alias_resolves_back_to_original_source(self):
        raw=json.dumps(dict(statements=[dict(text='A statement',citations=['E1'],
            evidence_quotes=[dict(citation='E1',quote='Source passage')])],
            clarification_questions=[],insufficient_evidence=False))
        result=build_graph(FakeRetriever(),lambda _:raw).invoke(self.state())
        self.assertEqual(result['status'],'generated_unverified')
        self.assertEqual(result['answer']['statements'][0]['citations'],['e1'])
    def state(self,**updates):
        return dict(question='What paperwork is needed?',uin=UIN,
                    claim_type='reimbursement',generate=True,**updates)
    def test_unknown_product_stops_before_retrieval(self):
        result=build_graph().invoke({'question':'What do I need?'})
        self.assertEqual(result['status'],'needs_clarification')
        self.assertNotIn('evidence',result)
    def test_evidence_only_without_generation(self):
        state=self.state(); state['generate']=False
        result=build_graph(FakeRetriever()).invoke(state)
        self.assertEqual(result['status'],'evidence_only')
    def test_valid_citation_ids_are_accepted_as_unverified(self):
        raw=json.dumps(dict(statements=[dict(text='A statement',citations=['e1'],evidence_quotes=[dict(citation='e1',quote='Source passage')])],
                            clarification_questions=[],insufficient_evidence=False))
        result=build_graph(FakeRetriever(),lambda _:raw).invoke(self.state())
        self.assertEqual(result['status'],'generated_unverified')
    def test_unknown_citation_blocks_answer(self):
        raw=json.dumps(dict(statements=[dict(text='A statement',citations=['invented'],evidence_quotes=[dict(citation='invented',quote='Source passage')])],
                            clarification_questions=[],insufficient_evidence=False))
        result=build_graph(FakeRetriever(),lambda _:raw).invoke(self.state())
        self.assertEqual(result['status'],'invalid_answer')
        self.assertNotIn('answer',result)
    def test_malformed_output_is_not_displayed(self):
        result=build_graph(FakeRetriever(),lambda _:'not json').invoke(self.state())
        self.assertEqual(result['status'],'generation_failed')
        self.assertNotIn('answer',result)
    def test_grounding_failure_withholds_draft(self):
        raw=json.dumps(dict(statements=[dict(text='Unsupported role',citations=['e1'],evidence_quotes=[dict(citation='e1',quote='Source passage')])],
                            clarification_questions=[],insufficient_evidence=False))
        checker=lambda _:json.dumps(dict(supported=False,unsupported_statement_indexes=[0],notes='Not in source'))
        result=build_graph(FakeRetriever(),lambda _:raw,checker).invoke(self.state())
        self.assertEqual(result['status'],'grounding_failed')
        self.assertFalse(result['answer'])
    def test_grounding_success_remains_distinct_from_human_review(self):
        raw=json.dumps(dict(statements=[dict(text='Supported',citations=['e1'],evidence_quotes=[dict(citation='e1',quote='Source passage')])],
                            clarification_questions=[],insufficient_evidence=False))
        checker=lambda _:json.dumps(dict(supported=True,unsupported_statement_indexes=[],notes='Supported'))
        result=build_graph(FakeRetriever(),lambda _:raw,checker).invoke(self.state())
        self.assertEqual(result['status'],'generated_checked')
    def test_safe_abstention_does_not_require_factual_grounding(self):
        raw=json.dumps(dict(statements=[],clarification_questions=['Ask the insurer for live status.'],insufficient_evidence=True))
        def must_not_call(_): raise AssertionError('No factual claims to audit')
        result=build_graph(FakeRetriever(),lambda _:raw,must_not_call).invoke(self.state())
        self.assertEqual(result['status'],'insufficient_evidence')
        self.assertTrue(result['answer']['insufficient_evidence'])
    def test_fabricated_source_quote_is_blocked(self):
        raw=json.dumps(dict(statements=[dict(text='A statement',citations=['e1'],
            evidence_quotes=[dict(citation='e1',quote='Words invented by the model')])],
            clarification_questions=[],insufficient_evidence=False))
        result=build_graph(FakeRetriever(),lambda _:raw).invoke(self.state())
        self.assertEqual(result['status'],'invalid_answer')
        self.assertFalse(result['answer'])
    def test_whitespace_only_quote_difference_is_allowed(self):
        raw=json.dumps(dict(statements=[dict(text='A statement',citations=['e1'],
            evidence_quotes=[dict(citation='e1',quote='Source   passage')])],
            clarification_questions=[],insufficient_evidence=False))
        result=build_graph(FakeRetriever(),lambda _:raw).invoke(self.state())
        self.assertEqual(result['status'],'generated_unverified')
    def test_boundary_kyc_exemption_blocked_even_with_real_quote(self):
        raw=json.dumps(dict(statements=[dict(text='KYC is not required at exactly INR 100,000.',citations=['e1'],
            evidence_quotes=[dict(citation='e1',quote='Source passage')])],
            clarification_questions=[],insufficient_evidence=False))
        state=self.state(); state['question']='Is KYC unnecessary at INR 100,000?'
        result=build_graph(FakeRetriever(),lambda _:raw).invoke(state)
        self.assertEqual(result['status'],'grounding_failed')
        self.assertIn('KYC exemption',result['error'])

if __name__=='__main__':
    unittest.main()
