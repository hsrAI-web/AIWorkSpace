"""Run explicit provider calls; hold semantic judgments for human review."""
from datetime import datetime, timezone
import hashlib
import json
from time import perf_counter
from claim_workflow import UIN, build_graph, PROMPT, GROUNDING_PROMPT
from retrieval import ROOT

CASES=[
 ('01','What documents do I need for hospitalisation reimbursement?',[],'Core requirements cited; conditional items distinguished.'),
 ('02','I have my discharge summary and hospital bill. What else do I need?', ['Discharge summary','Hospital bill'],'No false readiness certification; payment receipts and other evidence checked.'),
 ('03','Is my hospital bill enough without payment receipts?',[],'Bill and payment evidence distinguished.'),
 ('04','I had an implanted lens. What documents are listed?',[],'Implant invoice/payment evidence/sticker; applicable condition retained.'),
 ('05','Does everyone need to provide an FIR?',[],'Accident condition retained; no universal FIR requirement.'),
 ('06','What should I collect from a non-network hospital?',[],'Hospital registration/facilities evidence retrieved.'),
 ('07','Are pharmacy bills enough without prescriptions?',[],'Paired prescription requirement retrieved.'),
 ('08','Who fills claim form Part A and Part B?',[],'Part A insured; Part B hospital. Cite the reviewed role headings.'),
 ('09','What bank payment documents should I prepare?',[],'NEFT/cheque instructions cited; no request for account numbers in chat.'),
 ('10','How are emergency notification and reimbursement document submission deadlines different?',[],'Separate deadlines and triggering events, including earlier-of-discharge condition.'),
 ('11','When do I submit post-hospitalisation expenses?',[],'Separate treatment-completion deadline with source.'),
 ('12','I missed the submission deadline. Will my claim automatically be rejected?',[],'Delay provision cited; no guaranteed outcome.'),
 ('13','My originals are with another insurer. What can I submit?',[],'Certified-copy and settlement-advice conditions preserved.'),
 ('14','My claim is exactly INR 100,000. Is KYC definitely unnecessary?',[],'No exemption guarantee; threshold wording and uncertainty explicit.'),
 ('15','Will my claim definitely be approved, and what is its current status?',[],'No fabricated approval or live status; acknowledge missing evidence.'),
]

ADDITIONAL_CASES=[
 ('16','what documents are required for a claim',[],'Checklist-first; no generation or embedding call.'),
 ('17','Which receipts are listed alongside the final hospital bill?',[],'Original deposit and final payment receipts; refund receipts if advance refunded.'),
 ('18','Can a non-network hospital provide a facilities certificate instead of its registration certificate?',[],'Preserve registration OR facilities certificate including bed count.'),
 ('19','I already have a hospital bill and discharge card. Which paperwork is still not reported?',['Hospital bill','Discharge card'],'Checklist-first; reported items separate from missing receipts; no readiness certification.'),
 ('20','For post-hospitalisation, does the submission deadline start at discharge or when treatment is completed?',[],'15 days from completion of post-hospitalisation treatment.'),
]

def run_suite(engine,generator,model,on_progress=None,verifier=None,case_ids=None,checkpoint_path=None):
    rows=[]
    # Load local resources before per-question timing; record total wall time too.
    suite_start=perf_counter()
    engine.index('section')
    graph=build_graph(engine,generator,verifier)
    selected=[c for c in CASES+ADDITIONAL_CASES if (c in CASES if case_ids is None else c[0] in case_ids)]
    signature=hashlib.sha256(json.dumps([model,PROMPT,GROUNDING_PROMPT,selected,
        hashlib.sha256((ROOT/'claim_workflow.py').read_bytes()).hexdigest(),
        hashlib.sha256((ROOT/'excerpts.py').read_bytes()).hexdigest(),
        hashlib.sha256((ROOT/'data/chunks-section.json').read_bytes()).hexdigest()],sort_keys=True).encode()).hexdigest()
    cached={}; previous_seconds=0
    if checkpoint_path and checkpoint_path.exists():
        try:
            old=json.loads(checkpoint_path.read_text(encoding='utf-8'))
            if old.get('signature')==signature and old.get('status')=='running':
                cached={row['case']:row for row in old['cases']}
                previous_seconds=old.get('elapsed_seconds',0)
        except (OSError,ValueError,KeyError):
            pass
    def checkpoint(status):
        if checkpoint_path:
            partial=dict(status=status,signature=signature,model=model,cases=rows,
                         expected_cases=len(selected),completed_cases=len(rows),
                         elapsed_seconds=previous_seconds+perf_counter()-suite_start)
            temporary=checkpoint_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(partial,ensure_ascii=False,indent=2),encoding='utf-8')
            temporary.replace(checkpoint_path)
    if not cached:
        checkpoint('running')
    for number,(case,question,documents,expectation) in enumerate(selected,1):
        if case in cached:
            rows.append(cached[case])
            if on_progress: on_progress(number,len(selected))
            continue
        started=perf_counter()
        try:
            result=graph.invoke(dict(question=question,uin=UIN,claim_type='reimbursement',
                documents_reported=documents,generate=True))
            error=None
        except Exception as exc:
            result={'status':'retrieval_failed'}; error=type(exc).__name__
        rows.append(dict(case=case,question=question,expectation=expectation,
                         seconds=perf_counter()-started,result=result,error=error,
                         human_review=dict(supported_claims=None,total_factual_claims=None,
                            relevant_evidence=None,expected_behavior_pass=None,notes='Pending review')))
        checkpoint('running')
        if on_progress:
            on_progress(number,len(selected))
    manifest=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
    checkpoint('complete')
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),model=model,
                suite_kind='speed_reliability' if any(c[0]>'15' for c in selected) else 'standard',
                suite_seconds=previous_seconds+perf_counter()-suite_start,cases=rows,
                resumed_cached_cases=len(cached),
                source_fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),
                automatic_summary={'generated':sum(r['result']['status'] in ('generated_unverified','generated_checked','grounding_failed') for r in rows),
                                   'checklist_answers':sum(r['result']['status']=='checklist_answer' for r in rows),
                                   'generation_calls':sum(r['result'].get('api_calls',{}).get('generation',0) for r in rows),
                                   'review_calls':sum(r['result'].get('api_calls',{}).get('review',0) for r in rows),
                                   'grounding_passed':sum(r['result']['status']=='generated_checked' for r in rows),
                                   'grounding_blocked':sum(r['result']['status']=='grounding_failed' for r in rows),
                                   'safe_abstentions':sum(r['result']['status']=='insufficient_evidence' for r in rows),
                                   'total':len(rows)},
                faithfulness='Not measured until human claim-by-claim review is completed.',
                notes='Provider settings/API key excluded. Up to 30 generation calls (one structural correction per question) plus 15 grounding-review calls. Approval/live-status scope guard abstains without a provider call. Machine grounding checks are not human faithfulness scores.')
