"""Evidence-marker coverage smoke benchmark, not answer accuracy evaluation."""
import json
import hashlib
from time import perf_counter
from retrieval import ROOT, Retriever

# Reference markers from the manual. Form-only cases and generation/abstention
# are excluded until their corresponding stages exist.
CASES = [
 ('01','What documents do I need for hospitalisation reimbursement?', ['Duly Completed claim form','Discharge Card','Final Hospital bill']),
 ('02','I have a discharge summary and bill. What else is needed?', ['payment receipt','claim form']),
 ('03','Do I need a receipt to show I paid the hospital bill?', ['payment receipt']),
 ('04','What paperwork is needed for an implanted lens?', ['implant stickers','Invoice']),
 ('05','Does everyone need to provide an FIR?', ['Accident cases only']),
 ('06','What evidence do I need from a non-network hospital?', ['Registration Certificate']),
 ('07','Do pharmacy bills need prescriptions?', ['prescription by Medical Practitioner']),
 ('08','Who fills claim form Part A and Part B?', ['TO BE FILLED IN BY THE INSURED','TO BE FILLED IN BY THE HOSPITAL']),
 ('09','What bank payment documents should I prepare?', ['NEFT form','cancelled blank cheque']),
 ('10','When should I notify an emergency admission?', ['Within 24 hours','whichever is earlier']),
 ('11','When must I submit expenses after post hospitalisation treatment?', ['Within 15 days','completion of post']),
 ('12','Does missing the claim deadline always cause rejection?', ['delay','beyond the control']),
 ('13','My original documents are with another insurer. What can I submit?', ['claim settlement advice','certified by the other insurer']),
 ('14','My claim is exactly one lakh. Is KYC definitely unnecessary?', ['above Rs 1 lakh']),
]

def normalize(text):
    return ' '.join(text.lower().split())

def main():
    engine=Retriever()
    # Warm all indices. Timings below exclude downloads, index construction and
    # model startup, and therefore do not measure end-to-end application latency.
    for strategy in ('fixed','recursive','section','semantic'):
        engine.index(strategy)
    engine.search('What claim documents are needed?',mode='reranked')
    rows=[]
    for strategy in ('fixed','recursive','section','semantic'):
        for mode in ('dense','keyword','hybrid','reranked'):
            for case,question,markers in CASES:
                start=perf_counter()
                results=engine.search(question,strategy,mode,k=3)
                duration=perf_counter()-start
                found=normalize(' '.join(r['text'] for r in results))
                missing=[m for m in markers if normalize(m) not in found]
                rows.append(dict(case=case,strategy=strategy,mode=mode,
                                 reference_markers=markers,missing_markers=missing,
                                 marker_coverage_at_3=not missing,
                                 seconds=duration,ids=[r['id'] for r in results]))
    summary=[]
    for strategy in ('fixed','recursive','section','semantic'):
        for mode in ('dense','keyword','hybrid','reranked'):
            subset=[r for r in rows if r['strategy']==strategy and r['mode']==mode]
            passed=sum(r['marker_coverage_at_3'] for r in subset)
            summary.append(dict(strategy=strategy,mode=mode,passed=passed,total=len(subset)))
    report=dict(metric='All reference text markers found across top 3 passages',
                corpus_chunk_hashes={s:hashlib.sha256((ROOT/f'data/chunks-{s}.json').read_bytes()).hexdigest()
                                     for s in ('fixed','recursive','section','semantic')},
                limitations=['Small manual plus reviewed form-page-4 corpus; long sections can inflate coverage.',
                             'Measures text-marker presence, not semantic sufficiency or answer faithfulness.',
                             'Case 15 (approval/live status) is an answer-level abstention test; case 14 checks threshold retrieval only.',
                             'This benchmark does not score the generated answers or the separate deterministic checklist.'],
                summary=summary,results=rows)
    (ROOT/'data/retrieval-evaluation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
