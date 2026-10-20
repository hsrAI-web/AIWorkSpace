"""Deterministic excerpt IDs. Models select IDs; Python supplies source text."""
import re
from pydantic import BaseModel, Field, ConfigDict

class DraftStatement(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text: str = Field(min_length=1,max_length=600)
    excerpt_ids: list[str] = Field(min_length=1,max_length=3)

class DraftAnswer(BaseModel):
    model_config=ConfigDict(extra='forbid')
    statements: list[DraftStatement] = Field(max_length=3)
    clarification_questions: list[str] = Field(max_length=2)
    insufficient_evidence: bool

def catalog_for(evidence):
    catalog=[]
    for passage in evidence:
        text=passage['text']
        # Split only at whole alphabetic requirements. Keep other passages intact
        # so deadline rows, role headings and exceptions retain their context.
        starts=list(re.finditer(r'(?<!\S)[a-r]\.\s',text))
        spans=([text[m.start():starts[i+1].start() if i+1<len(starts) else len(text)].strip()
                for i,m in enumerate(starts)] if len(starts)>=3 else [text])
        for span in spans:
            catalog.append(dict(id=f'X{len(catalog)+1}',citation=passage['id'],
                text=span,section=passage.get('section',''),pages=passage.get('pages',[]),
                source_id=passage.get('source_id',''),url=passage.get('url','')))
    return catalog

def resolve_draft(raw,catalog):
    """Reject unknown IDs. Never trust model-supplied quotations or source IDs."""
    draft=DraftAnswer.model_validate_json(raw)
    by_id={e['id']:e for e in catalog}
    statements=[]
    for s in draft.statements:
        ids=list(dict.fromkeys(s.excerpt_ids))
        unknown=[i for i in ids if i not in by_id]
        if unknown:
            raise ValueError('Unknown excerpt IDs: '+', '.join(unknown))
        selected=[by_id[i] for i in ids]
        statements.append(dict(text=s.text,
            citations=list(dict.fromkeys(e['citation'] for e in selected)),
            evidence_quotes=[dict(citation=e['citation'],quote=e['text'],excerpt_id=e['id']) for e in selected]))
    return dict(statements=statements,clarification_questions=draft.clarification_questions,
                insufficient_evidence=draft.insufficient_evidence)

def checklist_first(question,scope='hospitalisation'):
    """Conservative routing: focused conditions, deadlines and alternatives stay RAG."""
    if scope!='hospitalisation': return False
    q=question.lower()
    narrow=r'implant|lens|non[ -]network|accident|\bfir\b|\bmlc\b|bank|neft|cheque|pharmac|prescription|\bkyc\b|lakh|\breceipt|payment|deadline|\bwhen\b|another insurer|other insurer|post[ -]hospital|pre[ -]hospital|death|ambulance|vaccin|approv|status'
    if re.search(narrow,q): return False
    return bool(re.search(r'what.*(?:document|paperwork)|(?:document|paperwork).*(?:need|require)|what else.*need|which paperwork.*(?:still|missing)|(?:show|give|prepare).*(?:checklist)',q))

def checklist_evidence(checklist):
    return [dict(id='checklist-'+i['id'],source_id=i['source_id'],pages=i['pages'],
                 section=i['section'],text=i['source_text'],url=i['url']) for i in checklist['items']]
