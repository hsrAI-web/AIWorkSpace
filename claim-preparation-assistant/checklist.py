"""Auditable checklist from manual 1.6; no LLM infers document possession."""
from functools import lru_cache
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parent

# Narrow aliases deliberately avoid fuzzy matching: a prescription is not a bill,
# a bill is not a payment receipt, and negated/partial descriptions stay unmatched.
RULES=[
 ('form','Completed claim form','a',None,['claim form','signed claim form','completed claim form']),
 ('identity','Photo ID and age proof','b',None,['photo id and age proof','id and age proof']),
 ('hospital_registration','Non-network hospital registration/facility evidence','c','non_network',['hospital registration certificate','hospital registration evidence']),
 ('discharge','Discharge/day-care/transfer summary','d',None,['discharge summary','discharge card','day care summary','transfer summary']),
 ('bill','Final hospital bill','e',None,['hospital bill','final hospital bill']),
 ('receipt','Hospital deposit/final payment receipts','e',None,['hospital payment receipts','hospital payment receipt','hospital bill payment receipt']),
 ('implant','Implant invoice, payment receipt and sticker','f','implant',['implant invoice receipt and sticker','implant invoice, receipt and sticker']),
 ('consultation','Consultation and treatment history papers','g',None,['consultation history','consultation papers']),
 ('diagnostics','Diagnostic reports, prescription, bill and receipt','h',None,['diagnostic reports prescription bill and receipt']),
 ('pharmacy','Pharmacy bills and prescriptions','i',None,['pharmacy bills and prescriptions']),
 ('accident','Accident MLC/FIR evidence','j','accident',['fir','mlc','mlc or fir']),
 ('accident_history','Treating-doctor intoxication history certification','k','accident',['doctor intoxication history certificate']),
 ('death','Death summary and certificate','l','death',['death summary and certificate']),
 ('indoor','Indoor case papers and nursing sheet, if requested','m','requested_indoor',['indoor case papers and nursing sheet']),
 ('vaccination','Vaccination invoice and receipt','n','vaccination',['vaccination invoice and receipt']),
 ('ambulance','Ambulance invoice and prescribed loss details','o','ambulance',['ambulance invoice and loss details']),
 ('kyc','KYC documentation','p','kyc',['kyc documents','kyc documentation']),
 ('bank','NEFT form and cancelled cheque','q',None,['neft form and cancelled cheque']),
 ('legal_heir','Legal heir/succession certificate where applicable','r','legal_heir',['legal heir certificate','succession certificate']),
]

def normalize(value):
    return ' '.join(re.findall(r'[a-z0-9]+',value.lower()))

@lru_cache(maxsize=1)
def source_requirements():
    pages=json.loads((ROOT/'data/cleaned-pages.json').read_text(encoding='utf-8'))
    manual=[p for p in pages if p['source_id']=='M1']
    text='\n'.join(p['clean_text'] for p in manual)
    text=text[text.index('1.6. List of documents required for a Claim'):]
    starts=list(re.finditer(r'(?m)^([a-v])\.\s',text))
    result={}
    for index,match in enumerate(starts):
        end=starts[index+1].start() if index+1<len(starts) else len(text)
        result[match.group(1)]=' '.join(text[match.start():end].split())
    assert set('abcdefghijklmnopqr').issubset(result)
    manifest=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
    url=next(m['url'] for m in manifest if m['source_id']=='M1')
    return result,url

def prepare_checklist(documents,context=None,scope='hospitalisation'):
    if scope!='hospitalisation':
        return {'items':[], 'questions':['This checklist currently supports hospitalisation/day-care only. Confirm the claim subtype.'],
                'unmatched_reported':documents,'readiness':'not_assessed'}
    context=context or {}
    requirements,url=source_requirements()
    reported={normalize(d):d for d in documents}
    matched=set(); items=[]; questions=[]
    for key,label,clause,condition,aliases in RULES:
        applicability='required'
        if condition=='kyc':
            # Broader form checklist references KYC. Do not infer an exemption
            # below the manual's threshold or at exactly one lakh.
            applicability='required' if context.get('amount_band')=='above_100000' else 'confirm_with_insurer'
        elif condition:
            value=context.get(condition,'unknown')
            applicability={'yes':'required','no':'not_applicable'}.get(value,'context_needed')
        alias_set={normalize(a) for a in aliases}
        hits=set(reported)&alias_set
        matched.update(hits)
        possession='reported_present' if hits else 'not_reported'
        # A matching name does not prove completeness of the documents listed
        # in the clause; retain the exact requirement for inspection.
        item=dict(id=key,requirement=label,applicability=applicability,
                  possession=possession,reported_names=[reported[h] for h in sorted(hits)],
                  source_id='M1',pages=[1] if clause=='a' else [2],
                  section=f'1.6({clause})',source_text=requirements[clause],url=url)
        items.append(item)
        if applicability=='context_needed':
            questions.append(f'Confirm whether this applies: {label}.')
    questions.append('Confirm KYC requirements with the insurer if the amount is not above INR 100,000; no exemption is inferred.') if context.get('amount_band')!='above_100000' else None
    return dict(items=items,questions=questions,unmatched_reported=[d for n,d in reported.items() if n not in matched],
                readiness='not_assessed',
                note='Not reported does not mean absent. Reported present does not verify completeness, authenticity, or readiness. Additional insurer requests may apply.')
