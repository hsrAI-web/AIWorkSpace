"""Embedding-based semantic boundaries with whole requirement items as atoms."""
import json
import re
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from retrieval import ROOT, Retriever, MODEL

def main():
    engine=Retriever()
    parents=json.loads((ROOT/'data/chunks-section.json').read_text(encoding='utf-8'))
    atoms=[]
    for parent in parents:
        # Manual alphabetic items keep conditions and exceptions in the same atom.
        # Other prose splits at full-stop sentence boundaries; form subsections
        # are already visually reviewed contiguous blocks.
        pattern=r'(?=(?<!\S)[a-v]\.\s)' if parent['source_id']=='M1' else r'(?<=\.)\s+(?=[A-Z])'
        parts=[p.strip() for p in re.split(pattern,parent['text']) if p.strip()]
        limiter=RecursiveCharacterTextSplitter(chunk_size=440,chunk_overlap=0,
                  length_function=engine.token_count,separators=['\n\n','\n','. ',' ',''])
        for part in parts:
            for piece in ([part] if engine.token_count(part)<=440 else limiter.split_text(part)):
                atoms.append({**parent,'text':piece})
    embeddings=np.array(list(engine.model.passage_embed([a['text'] for a in atoms])))
    embeddings/=np.maximum(np.linalg.norm(embeddings,axis=1,keepdims=True),1e-12)
    distances=1-np.sum(embeddings[:-1]*embeddings[1:],axis=1)
    # Threshold fixed before evaluation, not tuned against expected answers.
    threshold=float(np.percentile(distances,75))
    chunks=[]; group=[]
    def flush():
        if not group:
            return
        source=group[0]
        chunks.append(dict(source_id=source['source_id'],pages=sorted({p for a in group for p in a['pages']}),
            section=' / '.join(dict.fromkeys(a['section'] for a in group)),
            text=' '.join(a['text'] for a in group),url=source['url'],uin=source['uin']))
    for i,atom in enumerate(atoms):
        joined=' '.join([a['text'] for a in group]+[atom['text']])
        if group and (atom['source_id']!=group[-1]['source_id'] or
                      distances[i-1]>threshold or engine.token_count(joined)>450):
            flush(); group=[]
        group.append(atom)
    flush()
    for i,chunk in enumerate(chunks,1):
        chunk.update(id=f'semantic-{i:03}',strategy='semantic',word_count=len(chunk['text'].split()))
        assert engine.token_count(chunk['text'])<=450
    (ROOT/'data/chunks-semantic.json').write_text(json.dumps(chunks,ensure_ascii=False,indent=2),encoding='utf-8')
    report=dict(model=MODEL,method='Adjacent atomic-block embedding cosine distance; 75th percentile break threshold',
                threshold=threshold,atoms=len(atoms),chunks=len(chunks),max_tokens=max(engine.token_count(c['text']) for c in chunks),
                note='Requirement-item atoms preserve local conditions; page references conservatively include parent section pages.')
    (ROOT/'data/semantic-chunk-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
