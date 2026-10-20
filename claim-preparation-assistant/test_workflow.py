import json
import unittest
from claim_workflow import UIN,build_graph,source_specific_errors,Answer,Statement,quote_errors,provider_draft_errors
from excerpts import catalog_for,checklist_first

class FakeRetriever:
    def search(self,*a,**k):return [dict(id='e1',text='Source passage',pages=[4],source_id='F1')]
def draft(text='A supported statement',ids=None):
    return json.dumps(dict(statements=[dict(text=text,excerpt_ids=ids or ['X1'])],clarification_questions=[],insufficient_evidence=False))
class WorkflowTests(unittest.TestCase):
    def state(self,**updates):
        return dict(question='Are payment receipts needed?',uin=UIN,claim_type='reimbursement',generate=True,**updates)
    def test_unknown_scope_stops_before_retrieval(self):
        result=build_graph().invoke({'question':'What do I need?'})
        self.assertEqual(result['status'],'needs_clarification');self.assertNotIn('evidence',result)
    def test_broad_checklist_never_calls_retriever_or_provider(self):
        class NoRetriever:
            def search(self,*a,**k):raise AssertionError('No embeddings or reranking needed')
        def no_call(_):raise AssertionError('No provider call needed')
        for q in ['what documents are required for a claim','What documents do I need for hospitalisation reimbursement?',
                  'I have my discharge summary and hospital bill. What else do I need?']:
            result=build_graph(NoRetriever(),no_call,no_call).invoke({**self.state(),
                'question':q,'documents_reported':['Hospital bill']})
            self.assertEqual(result['status'],'checklist_answer');self.assertEqual(len(result['checklist']['items']),19)
            self.assertFalse(result['api_calls'])
            receipt=next(i for i in result['checklist']['items'] if i['id']=='receipt')
            self.assertEqual(receipt['possession'],'not_reported')
    def test_focused_questions_and_other_scope_do_not_use_broad_checklist(self):
        for q in ['Are pharmacy bills enough without prescriptions?','What documents do I need for an implant?',
                  'What do I need from a non-network hospital?','Is KYC necessary at INR 100,000?',
                  'What documents do I submit to another insurer?']:
            self.assertFalse(checklist_first(q))
        self.assertFalse(checklist_first('What documents are required?',scope='other'))
    def test_evidence_only_without_generation(self):
        result=build_graph(FakeRetriever()).invoke({**self.state(),'generate':False})
        self.assertEqual(result['status'],'evidence_only')
    def test_id_resolves_to_original_source_and_exact_text(self):
        r=build_graph(FakeRetriever(),lambda _:draft()).invoke(self.state())
        self.assertEqual(r['status'],'generated_unverified')
        s=r['answer']['statements'][0];self.assertEqual(s['citations'],['e1'])
        self.assertEqual(s['evidence_quotes'],[dict(citation='e1',quote='Source passage',excerpt_id='X1')])
        self.assertEqual(quote_errors(Answer.model_validate(r['answer']),r['evidence']),[])
    def test_unknown_excerpt_is_blocked_not_guessed(self):
        r=build_graph(FakeRetriever(),lambda _:draft(ids=['X99'])).invoke(self.state())
        self.assertEqual(r['status'],'invalid_answer');self.assertNotIn('answer',r)
    def test_model_cannot_override_quotation(self):
        raw=json.loads(draft());raw['statements'][0]['evidence_quotes']=[{'quote':'Fabricated quotation'}]
        r=build_graph(FakeRetriever(),lambda _:json.dumps(raw)).invoke(self.state())
        self.assertEqual(r['status'],'invalid_answer')
    def test_provider_preflight_rejects_unknown_id(self):
        payload=dict(excerpts=catalog_for(FakeRetriever().search()),question='Question',allowed_excerpt_ids=['X1'])
        self.assertTrue(provider_draft_errors(draft(ids=['X99']),payload))
        self.assertEqual(provider_draft_errors(draft(),payload),[])
    def test_clause_excerpt_preserves_conditions_and_alternatives(self):
        text='Documents a. Form b. Registration OR facilities certificate in non-network cases c. MLC / FIR in accident cases only'
        catalog=catalog_for([dict(id='p',text=text)])
        self.assertEqual(len(catalog),3)
        self.assertIn('OR facilities certificate in non-network cases',catalog[1]['text'])
        self.assertIn('accident cases only',catalog[2]['text'])
        for e in catalog:self.assertIn(e['text'],text)
    def test_valid_id_does_not_bypass_grounding(self):
        check=lambda _:json.dumps(dict(supported=False,unsupported_statement_indexes=[0],notes='Unsupported'))
        r=build_graph(FakeRetriever(),lambda _:draft(),check).invoke(self.state())
        self.assertEqual(r['status'],'grounding_failed');self.assertFalse(r['answer'])
    def test_pass_records_per_stage_timings_and_calls(self):
        check=lambda _:json.dumps(dict(supported=True,unsupported_statement_indexes=[],notes='Supported'))
        r=build_graph(FakeRetriever(),lambda _:draft(),check).invoke(self.state())
        self.assertEqual(r['status'],'generated_checked')
        self.assertEqual(r['api_calls'],{'generation':1,'review':1})
        self.assertEqual(set(r['timings']),{'checklist','retrieval','generation','review'})
    def test_empty_answer_requires_insufficient_evidence_flag(self):
        raw=json.dumps(dict(statements=[],clarification_questions=[],insufficient_evidence=False))
        self.assertEqual(build_graph(FakeRetriever(),lambda _:raw).invoke(self.state())['status'],'invalid_answer')
    def test_scope_abstention_makes_no_provider_call(self):
        def no_call(_):raise AssertionError('No live claim integration')
        r=build_graph(FakeRetriever(),no_call,no_call).invoke({**self.state(),
            'question':'Will my claim definitely be approved, and what is its current status?'})
        self.assertEqual(r['status'],'insufficient_evidence');self.assertEqual(r['api_calls']['generation'],0)
    def test_provider_failure_is_separate(self):
        def fail(_):raise RuntimeError('Synthetic failure')
        self.assertEqual(build_graph(FakeRetriever(),fail).invoke(self.state())['status'],'generation_failed')
    def test_first_consultation_does_not_match_fir(self):
        answer=Answer.model_construct(statements=[Statement.model_construct(text='You need first consultation letters.')])
        self.assertEqual(source_specific_errors(answer,[{'text':'MLC/FIR'}]),[])
    def test_registration_alternative_guard_remains(self):
        answer=Answer.model_construct(statements=[Statement.model_construct(text='A registration certificate is required.')])
        self.assertTrue(source_specific_errors(answer,[{'text':'registration certificate or certificate from Hospital authorities providing facilities'}]))
    def test_kyc_exemption_guard_remains(self):
        r=build_graph(FakeRetriever(),lambda _:draft(text='KYC is not required at exactly INR 100,000.')).invoke(
            {**self.state(),'question':'Is KYC unnecessary at INR 100,000?'})
        self.assertEqual(r['status'],'grounding_failed')
if __name__=='__main__':unittest.main()
