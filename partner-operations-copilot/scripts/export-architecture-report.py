"""Build portable documentation visuals and reports. No network or model calls."""
from __future__ import annotations

import base64
import re
from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/partner-copilot-explainer"
OUT = ROOT / "generated-artifacts/partner-explainer"
GREEN = "#285f4e"
INK = "#203b3b"
MUTED = "#5a6d66"
CREAM = "#f5f2e9"
GOLD = "#bd9446"


def text(x, y, value, size=20, color=INK, weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def lines(x, y, values, size=20, color=MUTED, step=29):
    return "".join(text(x, y+i*step, value, size, color) for i, value in enumerate(values))


def box(x, y, w, h, title, body, fill="#ffffff", stroke="#d9e2db", title_size=25):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        + text(x+24, y+43, title, title_size, INK, 700)
        + lines(x+24, y+77, body, 19, MUTED, 27)
    )


def arrow(path, color=GREEN, dashed=False):
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3" marker-end="url(#a)"' + (' stroke-dasharray="8 7"' if dashed else "") + '/>'


def svg_start(h, title, subtitle):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="{h}" viewBox="0 0 1680 {h}">'
        '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L0,6 L8,3 z" fill="{GREEN}"/></marker></defs>'
        f'<rect width="1680" height="{h}" fill="{CREAM}"/>'
        + text(56, 68, title, 42, INK, 700)
        + text(58, 108, subtitle, 21, MUTED)
    )


def architecture():
    s = svg_start(1080, "How Partner Desk is connected", "Read-only Salesforce demo records · synthetic quotes · cited public knowledge")
    for x, w, label, num in [(55,450,"BROWSER", "01"), (560,450,"API STACK","02"), (1065,560,"AGENT RUNTIME","03")]:
        s += f'<rect x="{x}" y="180" width="{w}" height="690" rx="24" fill="#ebece4"/>'
        s += text(x+25,220,f"{num}  {label}",19,GREEN,700)
    s += box(75,260,410,145,"React + Vite",["Partner / staff demo pages","Wouter navigation","Answer, citations, execution trace"])
    s += box(75,460,410,130,"Typed request hook",["Orval + React Query","OpenAPI-generated request/response"])
    s += box(75,665,410,165,"Browser localStorage",["View preference + thread ID","Support requests + staff responses","Queue is not shared across devices"])
    s += box(580,260,410,145,"Express · public /api",["Zod input + demo usage caps","Salesforce Connected App REST read","Fixed Developer Edition allowlist"])
    s += box(580,460,410,130,"FastAPI · loopback",["Python on 127.0.0.1:8000","Partner/thread checks → /agent/run","Uses scoped registration data"])
    s += box(580,665,410,165,"PostgreSQL checkpoints",["LangGraph AsyncPostgresSaver","Conversation + execution state","Not the support-request queue"])
    s += box(1085,260,520,145,"LangGraph control flow",["Safety + partner-scope gates","Exact-ID route → bounded tool loop","Requested-source coverage check"])
    s += box(1085,460,520,130,"LangChain read-only tools",["Salesforce registration lookup","Synthetic quote · local guide · public RAG","Sources return to the model"])
    s += box(1085,665,520,165,"Nebius Token Factory",["Chat: Qwen3-30B-A3B-Instruct-2507","Embeddings: Qwen3-Embedding-8B","Credentials stay server-side"])
    s += arrow("M485 330 L580 330")
    s += arrow("M785 405 L785 460")
    s += arrow("M990 510 L1040 510 L1040 330 L1085 330")
    s += arrow("M1345 405 L1345 460")
    s += arrow("M1405 460 L1405 405")
    s += arrow("M785 590 L785 665")
    s += arrow("M1605 370 L1640 370 L1640 625 L1345 625 L1345 665")
    s += arrow("M280 460 L280 405")
    s += arrow("M280 590 L280 665", dashed=True)
    s += text(72,928,"READS ARE SOURCE-BOUNDED. WRITES ARE HUMAN-CONTROLLED.",23,GREEN,700)
    s += lines(72,971,[
        "Salesforce reads are fixed to one Developer Edition org and approved demo registrations; quotes remain synthetic.",
        "The model cannot update Salesforce, send email, or approve pricing, credit, or eligibility.",
        "The role switch is not authentication; do not use real partner data in this public demo."
    ],21,MUTED,31)
    return s+"</svg>"


def workflow():
    s = svg_start(1020,"What happens after “Get an answer”","Record lookup, semantic public-source retrieval, or a deliberate human handoff")
    s += box(40,205,240,145,"Question",["Selected demo partner","Partner-prefixed thread","Validate before execution"],title_size=23)
    s += box(330,205,260,145,"Safety + scope",["Sensitive or unsupported?","Human route when required","No model call on sensitive path"],title_size=23)
    s += box(640,205,260,145,"ID planner",["Exact IDs → scoped lookups","Up to 3 IDs per plan","No model tool-selection step"],title_size=23)
    s += box(950,205,260,145,"Routine agent",["Nebius selects read-only tools","Retrieves before summarizing","Thread context resolves follow-ups"],title_size=23)
    s += box(1260,205,365,145,"Evidence check",["Requested records / sources present?","Missing source → withhold answer","Citations + trace in response"])
    s += arrow("M280 275 L330 275")
    s += arrow("M590 275 L640 275")
    s += text(596,254,"routine",18,GREEN)
    s += arrow("M900 275 L950 275")
    s += arrow("M1210 275 L1260 275")
    s += box(950,425,260,140,"Four read-only tools",["Salesforce registration / demo quote","Local guide / public knowledge RAG","Partner scope + evidence"],title_size=23)
    s += arrow("M1080 350 L1080 425")
    s += arrow("M1080 425 L1080 350")
    s += box(1260,425,365,140,"Visible result",["Answer + source timestamps","Expandable execution trace","Or labeled non-AI fallback"])
    s += arrow("M1440 350 L1440 425")
    s += box(330,685,260,135,"Human handoff",["Prepare a support form","No decision was made","No automatic submission"],"#fbf2dc","#d7bc7c",title_size=23)
    s += arrow("M460 350 L460 685",GOLD)
    s += text(478,550,"sensitive / unsupported",18,GREEN)
    s += box(640,685,260,135,"Partner confirms",["Review category + context","Click Save support request","Browser-local write"],"#fbf2dc","#d7bc7c",title_size=23)
    s += box(950,685,260,135,"Staff demo review",["Assign owner / update status","Record a human response","Same-browser queue"],"#fbf2dc","#d7bc7c",title_size=23)
    s += arrow("M590 750 L640 750")
    s += arrow("M900 750 L950 750")
    s += arrow("M1260 325 L1230 325 L1230 620 L460 620 L460 685",dashed=True)
    s += text(700,608,"Missing evidence / uncited ID",18,MUTED)
    s += text(60,905,"RECOVERY CONTROLS",22,GREEN,700)
    s += lines(60,944,[
        "At most 3 executed tool rounds · bounded recent model context · timeout / retry limits",
        "Evidence checks verify expected records and sources; they are not a fact-check of every generated sentence."
    ],21,MUTED,31)
    return s+"</svg>"


def annotated(filename, title, description, callouts):
    image = DOCS / "images" / filename
    data = base64.b64encode(image.read_bytes()).decode()
    s = svg_start(1140,title,description)
    s += '<rect x="35" y="145" width="1270" height="890" rx="18" fill="#dce3dc"/>'
    # Captures are approximately 1440 by 1000; preserve their ratio without cropping.
    s += f'<image x="45" y="155" width="1250" height="868" preserveAspectRatio="xMidYMin meet" href="data:image/jpeg;base64,{data}"/>'
    for i, (px, py, heading, explanation) in enumerate(callouts,1):
        cx, cy = 45+px*1250/1440, 155+py*868/1000
        s += f'<circle cx="{cx}" cy="{cy}" r="19" fill="{GREEN}" stroke="#fff" stroke-width="3"/>'
        s += text(cx-6,cy+7,str(i),20,"#fff",700)
        y=190+(i-1)*190
        s += f'<circle cx="1353" cy="{y-6}" r="17" fill="{GREEN}"/>'
        s += text(1348,y,str(i),18,"#fff",700)
        s += text(1380,y,heading,20,INK,700)
        s += lines(1335,y+35,wrap(explanation,29),18,MUTED,26)
    s += text(48,1080,"Current preview screenshot · demo-only records · annotations explain behavior; no live interaction is simulated.",20,MUTED)
    return s+"</svg>"


def markdown_html(source: str) -> str:
    output=[]
    buffer=[]
    in_code=False
    code=[]
    table=[]
    def inline(t):
        t=escape(t)
        t=re.sub(r"`([^`]+)`",r"<code>\1</code>",t)
        return re.sub(r"\*\*([^*]+)\*\*",r"<strong>\1</strong>",t)
    def flush():
        if buffer:
            output.append("<p>"+inline(" ".join(buffer))+"</p>")
            buffer.clear()
    def flush_table():
        if table:
            output.append("<table>")
            for i,row in enumerate(table):
                if re.fullmatch(r"[\s|:\-]+",row): continue
                tag="th" if i==0 else "td"
                cells=row.strip().strip("|").split("|")
                output.append("<tr>"+"".join(f"<{tag}>{inline(c.strip())}</{tag}>" for c in cells)+"</tr>")
            output.append("</table>")
            table.clear()
    for line in source.splitlines():
        if line.startswith("```"):
            flush();flush_table()
            if in_code:
                if not code or not code[0].startswith("flowchart"):
                    output.append("<pre>"+escape("\n".join(code))+"</pre>")
                code=[];in_code=False
            else: in_code=True
        elif in_code: code.append(line)
        elif line.startswith("|"):
            flush();table.append(line)
        else:
            flush_table()
            if not line.strip(): flush()
            elif line.startswith("#"):
                flush()
                level=min(len(line)-len(line.lstrip("#")),4)
                output.append(f"<h{level}>"+inline(line.lstrip("# "))+f"</h{level}>")
            elif line.startswith("!["):
                flush()
                match=re.match(r"!\[(.*?)\]\((.*?)\)",line)
                if match:
                    asset=DOCS/match[2]
                    output.append('<figure>'+asset.read_text()+f'<figcaption>{escape(match[1])}</figcaption></figure>')
            elif line.startswith("- ") or re.match(r"^\d+\.\s",line):
                flush();output.append('<p class="item">'+inline(line)+"</p>")
            else:buffer.append(line)
    flush();flush_table()
    return "\n".join(output)


def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    diagrams={
        "architecture.svg":architecture(),
        "workflow.svg":workflow(),
        "annotated-home.svg":annotated("partner-home.jpg","01 / Partner home","Read-only Salesforce registrations; local synthetic quotes",[
            (970,35,"Demo source","Red Valley and Bluewater map to a fixed Salesforce Developer Edition record set; the role selector is not sign-in."),
            (820,330,"Live status","Refresh reads the approved Salesforce demo registrations; only the selected partner's records are passed to the agent."),
            (600,570,"Registration status","Salesforce registration status and Opportunity stage are distinct fields; the app makes no CRM updates."),
            (1190,520,"Quote boundary","Quote examples are local synthetic data. Native Salesforce Quotes are not enabled.")
        ]),
        "annotated-help.svg":annotated("partner-help.jpg","02 / Ask, retrieve, or hand off","The agent selects read-only sources; the support form remains human-controlled",[
            (650,300,"Scoped question","The generated client sends question, partner ID, and thread ID through the public API."),
            (640,500,"Source routing","Record IDs use scoped lookups; broad partner questions use semantic search over curated public snapshots."),
            (640,650,"Cited guidance","General co-sell/security guidance can cite public sources; this is not company policy or an internal asset catalog."),
            (1215,455,"Human handoff","The partner reviews and saves a support request; it is stored only in this browser.")
        ]),
        "annotated-quotes.svg":annotated("quotes.jpg","03 / Quote status","Local synthetic quote examples; no native Salesforce Quote connection",[
            (755,170,"Data boundary","All quote examples are synthetic; the connected org's native Salesforce Quotes are not enabled."),
            (825,390,"No matching quote","This Salesforce-backed demo partner has no local quote examples. Switch to a synthetic partner for a quote lookup."),
            (825,570,"Human-owned decisions","Pricing, credit, and eligibility questions route to a human rather than an autonomous decision.")
        ])
    }
    for name,content in diagrams.items():
        (DOCS/name).write_text(content)
    content=markdown_html((DOCS/"README.md").read_text())
    css="""
    :root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#efeee6;color:#203b3b;font:17px/1.65 Arial,sans-serif}
    main{max-width:1160px;margin:40px auto;background:#fffdf7;padding:64px;border-top:10px solid #285f4e}
    h1{font-size:43px;line-height:1.15;letter-spacing:-1.5px}h2{font-size:28px;border-top:1px solid #dbe3db;padding-top:30px;margin-top:45px}
    h3{font-size:22px}p{margin:12px 0}figure{margin:26px -20px}svg{width:100%;height:auto;display:block}figcaption{font-size:13px;color:#5a6d66;margin-top:8px}
    table{border-collapse:collapse;width:100%;font-size:14px;margin:24px 0}td,th{border:1px solid #dbe3db;padding:12px;text-align:left;vertical-align:top}th{background:#eaf0e8}
    code{font:13px/1.5 monospace;overflow-wrap:anywhere;background:#edf1eb;padding:2px 4px}pre{font:13px/1.6 monospace;white-space:pre-wrap;background:#edf1eb;padding:20px}
    .item{padding-left:16px}a{color:#285f4e}@page{size:A4;margin:15mm}
    @media print{body{background:white;font-size:10pt}main{max-width:none;margin:0;padding:0;border:none}h1{font-size:27pt}h2{font-size:17pt;break-after:avoid}h3{break-after:avoid}figure{margin:12px 0;break-inside:avoid}table{font-size:8pt}tr{break-inside:avoid}code,pre{font-size:8pt}p{orphans:3;widows:3}}
    """
    (OUT/"partner-copilot-architecture-report.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Partner Operations Copilot — architecture report</title><style>'+css+'</style><main>'+content+'</main></html>'
    )
    print("Created 5 SVG visuals and self-contained HTML report.")


if __name__=="__main__":
    main()
