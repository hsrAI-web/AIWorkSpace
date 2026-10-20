"""Build equal-size baseline and section-aware comparison corpora.

Form tables remain quarantined until their reading order is reviewed.
Word counts here are not embedding-model token counts.
"""
from pathlib import Path
import json
import re
import unicodedata
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parent

def clean(text):
    lines = unicodedata.normalize('NFKC', text).splitlines()
    output, footer = [], False
    for line in lines:
        line = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', line).strip()
        if line.startswith('HDFC ERGO General Insurance Company Limited. IRDAI'):
            footer = True
            continue
        if footer:
            if 'UIN:' in line:
                footer = False
            continue
        if not line or re.fullmatch(r'\d+', line):
            continue
        if line in ('HDFC ERGO General Insurance Company Limited',
                    'my: Optima Secure Claims Procedure', 'Claim Manual'):
            continue
        if line.startswith(('ClaimManual/Ver', 'CF/Ver')):
            continue
        output.append(line)
    return '\n'.join(output)

def recursive_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, length_function=len,
        separators=['\n\n', '\n', ' ', ''], add_start_index=True,
    )
    result = []
    for page in pages:
        documents = splitter.create_documents([page['clean_text']])
        for document in documents:
            start = document.metadata['start_index']
            text = document.page_content
            assert start >= 0 and page['clean_text'][start:start+len(text)] == text
            assert len(text) <= 1000
            result.append(dict(source_id=page['source_id'], pages=[page['page']],
                               section='Recursive character window', text=text,
                               start_char=start, end_char=start+len(text)))
    return result

def fixed_character_chunks(pages,size=1000,overlap=150):
    """Literal fixed-size control for the handout's chunking comparison."""
    result=[]
    for page in pages:
        text=page['clean_text']
        for start in range(0,len(text),size-overlap):
            piece=text[start:start+size]
            result.append(dict(source_id=page['source_id'],pages=[page['page']],
                               section='Fixed character window',text=piece,
                               start_char=start,end_char=start+len(piece)))
            if start+size>=len(text):
                break
    return result

def manual_sections(pages):
    result, heading, lines, refs = [], None, [], set()
    def flush():
        if lines:
            result.append(dict(source_id='M1', pages=sorted(refs), section=heading,
                               text=' '.join(lines)))
    for page in pages:
        for line in page['clean_text'].splitlines():
            if re.match(r'^1\.\d+\.', line):
                flush()
                heading, lines, refs = line, [], set()
            if heading:
                lines.append(line)
                refs.add(page['page'])
    flush()
    return result

def reviewed_form_sections(pages):
    """Only page-4 prose/checklists visually checked against rendered original.

    Stop before Ambulance Benefit, which continues on the following page.
    Other form tables remain excluded.
    """
    page = next(p for p in pages if p['source_id']=='F1' and p['page']==4)
    text = page['clean_text']
    headings = ['LIST OF ENCLOSURES FOR SUBMISSION OF CLAIM',
                'In-patient Treatment /Day Care Procedures', 'Road Traffic Accident',
                'For Death Cases', 'Pre and Post-hospitalization/Vaccination',
                'Organ Donation/Transplantation', 'Ambulance Benefit']
    offsets = [text.index(h) for h in headings]
    assert offsets==sorted(offsets)
    sections=[dict(source_id='F1', pages=[4], section=headings[i],
                 text=text[start:offsets[i+1]].strip())
            for i,start in enumerate(offsets[:-1])]
    for number,role in [(1,'Part A: insured'),(3,'Part B: hospital')]:
        page=next(p for p in pages if p['source_id']=='F1' and p['page']==number)
        text=page['clean_text']
        start=text.index('CLAIM FORM')
        end=text.index('The issue of this Form',start)
        sections.append(dict(source_id='F1',pages=[number],section=role,text=text[start:end].strip()))
    return sections

def main():
    pages = json.loads((ROOT/'data/pages.json').read_text(encoding='utf-8'))
    manifest = json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
    metadata = {item['source_id']:item for item in manifest}
    cleaned = [{**page, 'clean_text':clean(page['text'])} for page in pages]
    # Manual prose has verified section boundaries. Form layouts need separate
    # table-aware treatment; do not silently index scrambled field/checklist rows.
    eligible = [page for page in cleaned if page['source_id']=='M1']
    form_sections = reviewed_form_sections(cleaned)
    form_pages = [dict(source_id='F1',page=number,
                  clean_text='\n\n'.join(c['text'] for c in form_sections if c['pages']==[number]))
                  for number in (1,3,4)]
    corpora = {'fixed':fixed_character_chunks(eligible+form_pages),
               'recursive':recursive_chunks(eligible+form_pages),
               'section':manual_sections(eligible)+form_sections}
    for strategy, chunks in corpora.items():
        for n, chunk in enumerate(chunks, 1):
            chunk.update(id=f'{strategy}-{n:03}', strategy=strategy,
                         word_count=len(chunk['text'].split()),
                         url=metadata[chunk['source_id']]['url'],
                         uin=metadata[chunk['source_id']]['uin'])
        (ROOT/f'data/chunks-{strategy}.json').write_text(
            json.dumps(chunks, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT/'data/cleaned-pages.json').write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2), encoding='utf-8')
    sections = [c for c in corpora['section'] if c['source_id']=='M1']
    assert len(sections)==6, 'Expected all six manual sections'
    documents = next(c for c in sections if c['section'].startswith('1.6.'))
    assert documents['pages']==[1,2], 'Cross-page section continuation lost'
    for phrase in ('Accident cases only', 'above Rs 1 lakh',
                   'beyond the control', 'cancelled blank cheque'):
        assert phrase in documents['text'], f'Lost condition: {phrase}'
    deadlines = next(c for c in sections if c['section'].startswith('1.5.'))
    assert 'Within 30 days' in deadlines['text'] and 'Within 15 days' in deadlines['text']
    report = dict(indexed_sources=['M1','F1 page 4 reviewed enclosures','F1 pages 1 and 3 reviewed role headings'],
                  deferred_sources=['Other F1 content, tables, and cross-page ambulance checklist'],
                  reason='Only visually reviewed form passages enter retrieval.',
                  checks='Six manual sections; cross-page checklist; key conditions; both deadline rows preserved.',
                  baseline=dict(implementation='langchain_text_splitters.RecursiveCharacterTextSplitter',
                                chunk_size_characters=1000, chunk_overlap_characters=150,
                                page_bounded=True),
                  strategies={k:dict(chunks=len(v), min_words=min(c['word_count'] for c in v),
                                     max_words=max(c['word_count'] for c in v)) for k,v in corpora.items()})
    (ROOT/'data/chunk-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
