"""Local dense + BM25 retrieval with reciprocal-rank fusion. No generation."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import numpy as np
from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tokenizers import Tokenizer
from fastembed.rerank.cross_encoder import TextCrossEncoder

ROOT = Path(__file__).resolve().parent
MODEL = 'BAAI/bge-small-en-v1.5'

def terms(text):
    return re.findall(r'[a-z0-9]+', text.lower())

class Retriever:
    def __init__(self):
        self.model = TextEmbedding(MODEL, cache_dir=str(ROOT/'models'), threads=2)
        self.tokenizer = Tokenizer.from_str(self.model.model.tokenizer.to_str())
        # Inspect token length without tokenizer truncation; prevent silent loss.
        self.tokenizer.no_truncation()
        self.tokenizer.no_padding()
        self.indices = {}
        self.reranker = None

    def token_count(self, text):
        return len(self.tokenizer.encode(text).ids)

    def index(self, strategy):
        if strategy in self.indices:
            return self.indices[strategy]
        parents = json.loads((ROOT/f'data/chunks-{strategy}.json').read_text(encoding='utf-8'))
        splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=60,
                    length_function=self.token_count, separators=['\n\n','\n',' ', ''])
        chunks = []
        for parent in parents:
            # Only oversized section chunks need subdivision. Preserve source and
            # condition sentences; parent ID makes the subdivision inspectable.
            pieces = [parent['text']]
            if self.token_count(parent['text'])>450:
                # Keep complete alphabetic requirements together. Splitting a
                # clause mid-sentence can drop its OR alternative or condition.
                atoms=[a.strip() for a in re.split(r'(?=(?<!\S)[a-v]\.\s)',parent['text']) if a.strip()]
                pieces=[]; current=''
                for atom in atoms:
                    if self.token_count(atom)>450:
                        raise ValueError('A complete requirement exceeds model capacity; use a longer-context model')
                    candidate=(current+' '+atom).strip()
                    if self.token_count(candidate)>450:
                        pieces.append(current); current=atom
                    else:
                        current=candidate
                if current:
                    pieces.append(current)
            for n,text in enumerate(pieces,1):
                count = self.token_count(text)
                if count>450:
                    raise ValueError('Embedding input exceeds configured budget')
                chunks.append({**parent, 'id':f"{parent['id']}.{n}",
                               'parent_id':parent['id'], 'text':text, 'tokens':count})
        fingerprint = hashlib.sha256(json.dumps([MODEL,chunks],sort_keys=True).encode()).hexdigest()
        file = ROOT/f'data/vectors-{strategy}.npz'
        vectors = None
        if file.exists():
            with np.load(file,allow_pickle=False) as saved:
                if str(saved['fingerprint'])==fingerprint:
                    vectors=saved['vectors']
        if vectors is None:
            vectors=np.array(list(self.model.passage_embed([c['text'] for c in chunks])))
            np.savez(file,vectors=vectors,fingerprint=np.array(fingerprint))
        vectors=vectors/np.maximum(np.linalg.norm(vectors,axis=1,keepdims=True),1e-12)
        index=(chunks,vectors,BM25Okapi([terms(c['text']) for c in chunks]))
        self.indices[strategy]=index
        (ROOT/f'data/indexed-chunks-{strategy}.json').write_text(json.dumps(chunks,ensure_ascii=False,indent=2),encoding='utf-8')
        return index

    def search(self, question, strategy='recursive', mode='hybrid', k=5):
        if not question.strip():
            raise ValueError('Question must not be empty')
        if self.token_count(question)>450:
            raise ValueError('Please shorten the question (maximum 450 tokens)')
        chunks,vectors,bm25=self.index(strategy)
        query=np.array(next(self.model.query_embed(question)))
        query=query/max(np.linalg.norm(query),1e-12)
        dense=vectors@query
        lexical=bm25.get_scores(terms(question))
        dr=np.argsort(-dense,kind='stable')
        kr=np.argsort(-lexical,kind='stable')
        fusion=np.zeros(len(chunks))
        for ranking in (dr,kr):
            for rank,i in enumerate(ranking[:10],1):
                if ranking is kr and lexical[i]<=0:
                    continue
                fusion[i]+=1/(60+rank)
        scores={'dense':dense,'keyword':lexical,'hybrid':fusion,'reranked':fusion}[mode]
        order=np.argsort(-scores,kind='stable')[:(10 if mode=='reranked' else k)]
        if mode=='reranked':
            if self.reranker is None:
                self.reranker=TextCrossEncoder('Xenova/ms-marco-MiniLM-L-6-v2',
                                             cache_dir=str(ROOT/'models'),threads=2)
            checker=Tokenizer.from_str(self.reranker.model.tokenizer.to_str())
            checker.no_truncation()
            checker.no_padding()
            for i in order:
                if len(checker.encode(question,chunks[i]['text']).ids)>512:
                    raise ValueError('Question and passage exceed reranker context; shorten question')
            ranked=np.array(list(self.reranker.rerank(question,[chunks[i]['text'] for i in order])))
            scores=ranked
            selected=np.argsort(-ranked,kind='stable')[:k]
            return [{**chunks[order[j]],'score':float(ranked[j]),
                     'dense_score':float(dense[order[j]]),
                     'keyword_score':float(lexical[order[j]])} for j in selected]
        return [{**chunks[i], 'score':float(scores[i]),'dense_score':float(dense[i]),
                 'keyword_score':float(lexical[i])} for i in order]

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('question')
    parser.add_argument('--strategy',choices=['fixed','recursive','section','semantic'],default='recursive')
    parser.add_argument('--mode',choices=['dense','keyword','hybrid','reranked'],default='hybrid')
    args=parser.parse_args()
    results=Retriever().search(args.question,args.strategy,args.mode)
    print(json.dumps(results,ensure_ascii=False,indent=2))
