"""Summarize measured results without inventing human evaluation scores."""
import json
import math
import statistics
from retrieval import ROOT

def latency(values):
    values=sorted(values)
    return f'median {statistics.median(values):.2f}s; p95 {values[math.ceil(.95*len(values))-1]:.2f}s'

def main():
    retrieval=json.loads((ROOT/'data/retrieval-evaluation.json').read_text(encoding='utf-8'))
    lines=['RETRIEVAL COMPARISON','Metric: expected source text markers across top 3 retrieved passages.',
           'Not generated-answer accuracy or semantic sufficiency. All strategies use the same admitted corpus.','']
    for summary in retrieval['summary']:
        sample=[r['seconds'] for r in retrieval['results'] if r['strategy']==summary['strategy'] and r['mode']==summary['mode']]
        lines.append(f"{summary['strategy']} / {summary['mode']}: {summary['passed']}/{summary['total']}; {latency(sample)}")
    lines+=['','Limitations:']+retrieval['limitations']
    lines+=['','Do not infer that semantic chunking or reranking always improves retrieval.',
            'Fixed/recursive windows, whole sections and semantic units differ in size, which affects marker coverage.',
            'Reported retrieval timings exclude model loading, downloads and initial indexing.']
    (ROOT/'RETRIEVAL-RESULTS.txt').write_text('\n'.join(lines),encoding='utf-8')
    path=ROOT/'data/live-evaluation.json'
    if path.exists():
        report=json.loads(path.read_text(encoding='utf-8'))
        lines=['LIVE ANSWER EVALUATION',f"Model: {report['model']}",
               f"Automatic counts: {report['automatic_summary']}",
               f"Per-question retrieval/generation/review timing: {latency([r['seconds'] for r in report['cases']])}",
               f"Total suite: {report['suite_seconds']:.2f}s",'',
               'A model grounding pass is not a human faithfulness score.',
               report['faithfulness'],'']
        for case in report['cases']:
            result=case['result']
            lines.append(f"Case {case['case']}: {result['status']} ({case['seconds']:.2f}s)")
            if result.get('grounding_review'):
                lines.append('  Model review: '+result['grounding_review']['notes'])
            if result.get('error'):
                lines.append('  '+result['error'])
        (ROOT/'LIVE-EVALUATION-RESULTS.txt').write_text('\n'.join(lines),encoding='utf-8')
    print('Current reports written; human review scores remain unfilled.')

if __name__=='__main__': main()
