import { useEffect, useMemo, useRef, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Link, Route, Switch, useLocation } from 'wouter';
import { useAnswerPartnerQuestion } from '@workspace/api-client-react';
import demoRecords from './demo-records.json';
import { SalesforceDataNotice, useSalesforceDemoRecords } from './salesforce-data';
import {
  Activity, ArrowRight, ArrowUpRight, BookOpen, Building2, Check, ChevronRight,
  CircleHelp, Clock3, FileText, Handshake, Headphones, Inbox,
  Layers3, LifeBuoy, MessageSquareText, Search, ShieldCheck, UserRound, Users
} from 'lucide-react';

type Role = 'partner' | 'staff';
type DemoPartner = { id: string; name: string; organization: string; owner: string; dataSource?: string };
type Deal = { id: string; partnerId: string; title: string; status: string; submittedAt: string; expectedClose: string; owner: string; nextStep: string; sourceLabel: string; opportunityStage?: string; lastModifiedAt?: string; salesforceId?: string };
type Quote = { id: string; partnerId: string; product: string; status: string; requestedAt: string; lastUpdatedAt: string; owner: string; nextStep: string; sourceLabel: string };
type SupportRequest = { id: string; partnerId: string; category: string; message: string; status: string; assignee: string; response: string; createdAt: string; updatedAt: string };
type Article = { id: string; title: string; category: string; summary: string; steps: string[]; updatedAt: string; sourceLabel: string };
type AgentAnswer = {
  text: string;
  mode: 'ai'|'fallback';
  provider: string;
  intent: string;
  handoffRequired: boolean;
  handoffCategory: string;
  sources: {label:string;timestamp:string}[];
  trace: string[];
  toolCalls: string[];
};

const daysAgo = (days:number) => new Date(Date.now()-days*86400000).toISOString();
const dateFromNow = (days:number) => new Date(Date.now()+days*86400000).toISOString().slice(0,10);
const PARTNERS: DemoPartner[] = demoRecords.partners;
const DEMO_DEALS: Deal[] = demoRecords.deals.map(record=>({
  id:record.id,partnerId:record.partnerId,title:record.title,status:record.status,
  submittedAt:daysAgo(record.submittedDaysAgo),expectedClose:dateFromNow(record.expectedCloseDaysFromNow),
  owner:record.owner,nextStep:record.nextStep,sourceLabel:record.sourceLabel
}));
const DEMO_QUOTES: Quote[] = demoRecords.quotes.map(record=>({
  id:record.id,partnerId:record.partnerId,product:record.product,status:record.status,
  requestedAt:daysAgo(record.requestedDaysAgo),lastUpdatedAt:daysAgo(record.lastUpdatedDaysAgo),
  owner:record.owner,nextStep:record.nextStep,sourceLabel:record.sourceLabel
}));
const ARTICLES: Article[] = demoRecords.articles.map(article=>({
  id:article.id,title:article.title,category:article.category,summary:article.summary,
  steps:article.steps,updatedAt:daysAgo(article.updatedDaysAgo),sourceLabel:article.sourceLabel
}));

function useDealRecords() {
  const source=useSalesforceDemoRecords();
  return {...source,deals:[...DEMO_DEALS,...(source.data?.registrations??[])] as Deal[]};
}

const STORE_KEY = 'partner-operations-copilot-local-v1';
const PREF_KEY = 'partner-operations-copilot-view-v1';
const threadStorageKey = (partnerId:string) => `partner-agent-thread-${partnerId}`;
const createThreadId = (partnerId:string) =>
  `${partnerId}-${globalThis.crypto?.randomUUID?.() ?? `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`}`;
const getOrCreateThreadId = (partnerId:string) => {
  try {
    const stored=localStorage.getItem(threadStorageKey(partnerId));
    if(stored?.startsWith(`${partnerId}-`))return stored;
  } catch {}
  const threadId=createThreadId(partnerId);
  try { localStorage.setItem(threadStorageKey(partnerId),threadId); } catch {}
  return threadId;
};
const sensitiveCategory = (question:string) => {
  if(/\b(special pricing|discount|price exception|pricing exception|override)\b/i.test(question))return 'Special pricing';
  if(/\b(credit hold|credit limit|credit block|payment terms)\b/i.test(question))return 'Credit hold';
  if(/\b(eligibility|eligible|qualification|qualify|approval|approve|authorize|waive)\b/i.test(question))return 'Eligibility';
  return '';
};
const nowIso = () => new Date().toISOString();
const fmtDate = (v:string) => { const d = new Date(v); return Number.isNaN(d.getTime()) ? 'Date not set' : new Intl.DateTimeFormat('en',{month:'short',day:'numeric',year:'numeric'}).format(d); };
const fmtTime = (v:string) => { const d = new Date(v); return Number.isNaN(d.getTime()) ? 'Timestamp not available' : new Intl.DateTimeFormat('en',{month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}).format(d); };
const makeId = () => `REQ-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2,5).toUpperCase()}`;
const readRequests = ():SupportRequest[] => {
  try { const data = localStorage.getItem(STORE_KEY); const parsed = data ? JSON.parse(data) : []; return Array.isArray(parsed) ? parsed : []; }
  catch { return []; }
};
const readPrefs = () => {
  try { const value = JSON.parse(localStorage.getItem(PREF_KEY) || '{}'); return { role: value.role === 'staff' ? 'staff' as Role : 'partner' as Role, partnerId: PARTNERS.some(p=>p.id===value.partnerId) ? value.partnerId as string : PARTNERS[0].id }; }
  catch { return { role:'partner' as Role, partnerId:PARTNERS[0].id }; }
};
const statusTone = (s:string) => s.toLowerCase().replaceAll(' ','-');
const queryClient = new QueryClient();

function App() {
  const initial = readPrefs();
  const [role,setRole] = useState<Role>(initial.role);
  const [partnerId,setPartnerId] = useState(initial.partnerId);
  const [requests,setRequests] = useState<SupportRequest[]>(readRequests);
  const [toast,setToast] = useState('');
  const [location,setLocation] = useLocation();
  const partner = PARTNERS.find(p=>p.id===partnerId) || PARTNERS[0];
  useEffect(()=>{ try { localStorage.setItem(STORE_KEY,JSON.stringify(requests)); } catch { setToast('Local storage is unavailable. Changes may not persist after closing this page.'); } },[requests]);
  useEffect(()=>{ try { localStorage.setItem(PREF_KEY,JSON.stringify({role,partnerId})); } catch { /* Preference is optional. */ } },[role,partnerId]);
  useEffect(()=>{ if (!toast) return; const timer=window.setTimeout(()=>setToast(''),3200); return ()=>window.clearTimeout(timer); },[toast]);
  const submitRequest = (category:string,message:string) => {
    const stamp=nowIso();
    setRequests(old=>[{id:makeId(),partnerId:partner.id,category,message,status:'Open',assignee:'Unassigned',response:'',createdAt:stamp,updatedAt:stamp},...old]);
    setToast('Support request saved to this browser’s demo queue.');
    setLocation('/requests');
  };
  const updateRequest = (id:string,updates:Partial<SupportRequest>) => setRequests(old=>old.map(r=>r.id===id?{...r,...updates,updatedAt:nowIso()}:r));
  const active = (path:string) => path==='/deals' ? location==='/deals'||location.startsWith('/deals/') : path==='/requests' ? location.startsWith('/requests') : location===path;
  const navLinks = role==='partner'
    ? [{href:'/',label:'Home',icon:<Layers3 size={16}/>},{href:'/deals',label:'Deal registrations',icon:<Handshake size={16}/>},{href:'/quotes',label:'Quote status',icon:<FileText size={16}/>},{href:'/help',label:'Help & support',icon:<LifeBuoy size={16}/>},{href:'/requests',label:'My requests',icon:<Inbox size={16}/>}]
    : [{href:'/',label:'Operations overview',icon:<Activity size={16}/>},{href:'/partners',label:'Partner portfolio',icon:<Building2 size={16}/>},{href:'/deals',label:'Deal registrations',icon:<Handshake size={16}/>},{href:'/quotes',label:'Quote examples',icon:<FileText size={16}/>},{href:'/requests',label:'Request queue',icon:<Inbox size={16}/>}];
  const heading = location==='/deals' ? 'Deal registrations' : location.startsWith('/deals/') ? 'Registration detail' : location==='/quotes' ? 'Quote status' : location==='/help' ? 'Help & support' : location.startsWith('/requests') ? role==='staff'?'Request queue':'My requests' : location==='/partners' ? 'Partner portfolio' : role==='staff'?'Operations overview':'Partner home';

  return <QueryClientProvider client={queryClient}><div className="app-shell">
    <aside className="sidebar">
      <Link href="/" className="brand"><span className="brand-mark"><Handshake size={19}/></span><span><span className="brand-name">Partner Desk</span><span className="brand-sub">Operations copilot</span></span></Link>
      <div className="workspace-label">{role==='staff'?'Staff workspace':'Partner workspace'}</div>
      <nav className="nav-list">{navLinks.map(item=><Link href={item.href} key={item.href} className={`nav-link ${active(item.href)?'active':''}`}>{item.icon}{item.label}{item.href==='/requests'&&role==='staff'&&requests.some(r=>r.status==='Open')&&<span style={{marginLeft:'auto'}}>{requests.filter(r=>r.status==='Open').length}</span>}</Link>)}</nav>
      <div className="sidebar-bottom"><div className="demo-indicator"><span className="demo-dot"/><span><strong>Demo-only workspace</strong><br/>Support queue: this browser. AI memory: server-side.</span></div></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><div className="crumb">Partner Operations <ChevronRight size={12} style={{verticalAlign:'middle',margin:'0 5px'}}/>{heading}</div><div className="top-actions"><span className="mode-tag">{role==='staff'?'Demo-only workspace':partner.dataSource==='salesforce'?'Salesforce · demo records':'Local synthetic examples'}</span><label htmlFor="role-switch">View</label><select id="role-switch" className="role-select" aria-label="Select demo view" value={role} onChange={e=>setRole(e.target.value as Role)}><option value="partner">Partner demo</option><option value="staff">Staff demo</option></select>{role==='partner'&&<select aria-label="Select demo partner identity" className="identity-select" value={partnerId} onChange={e=>setPartnerId(e.target.value)}>{PARTNERS.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select>}</div></header>
      <header className="mobile-head"><Link href="/" className="brand"><span className="brand-mark"><Handshake size={17}/></span><span className="brand-name">Partner Desk</span></Link><select aria-label="Select demo view" className="role-select" value={role} onChange={e=>setRole(e.target.value as Role)}><option value="partner">Partner</option><option value="staff">Staff</option></select></header>
      {role==='partner'&&<div className="mobile-identity"><UserRound size={13}/><select aria-label="Select demo partner identity" className="identity-select" value={partnerId} onChange={e=>setPartnerId(e.target.value)}>{PARTNERS.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></div>}
      <Switch>
        <Route path="/"><Home role={role} partner={partner} requests={requests}/></Route>
        <Route path="/deals"><Deals partner={partner} role={role}/></Route>
        <Route path="/deals/:id">{params=><DealDetail id={params.id} partner={partner} role={role}/>}</Route>
        <Route path="/quotes"><Quotes partner={partner} role={role}/></Route>
        <Route path="/help"><HelpPage partner={partner} onSubmit={submitRequest}/></Route>
        <Route path="/requests"><RequestsPage role={role} partner={partner} requests={requests} onUpdate={updateRequest}/></Route>
        <Route path="/requests/:id">{params=><RequestDetail id={params.id} role={role} partner={partner} requests={requests} onUpdate={updateRequest}/>}</Route>
        <Route path="/partners"><Portfolio role={role} requests={requests}/></Route>
        <Route><NotFound/></Route>
      </Switch>
      {role==='partner'&&<nav className="mobile-nav">{navLinks.map(item=><Link key={item.href} href={item.href} className={active(item.href)?'active':''}>{item.icon}<span>{item.label==='Deal registrations'?'Deals':item.label==='Quote status'?'Quotes':item.label==='Help & support'?'Help':item.label==='My requests'?'Requests':item.label}</span></Link>)}</nav>}
      {role==='staff'&&<nav className="mobile-nav">{navLinks.map(item=><Link key={item.href} href={item.href} className={active(item.href)?'active':''}>{item.icon}<span>{item.label==='Operations overview'?'Home':item.label==='Partner portfolio'?'Partners':'Queue'}</span></Link>)}</nav>}
    </section>
    {toast&&<div className="toast" role="status">{toast}</div>}
  </div></QueryClientProvider>;
}

function DemoNote(){return <div className="notice info"><ShieldCheck size={14}/>Demo-only workspace: Red Valley and Bluewater registrations are read from Salesforce; other records and all quotes are local synthetic examples. Demo roles are not secure authentication. AI questions go to Nebius and conversation state is stored server-side. Support requests stay in this browser. The app does not update Salesforce or send email. Do not enter confidential data.</div>}
function PageHeading({eyebrow,title,subtitle,action}:{eyebrow:string;title:string;subtitle:string;action?:ReactNode}){return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p className="subtitle">{subtitle}</p></div>{action}</div>}
function Status({value}:{value:string}){return <span className={`status ${statusTone(value)}`}>{value}</span>}
function Stat({label,value,foot,icon}:{label:string;value:string|number;foot:string;icon:ReactNode}){return <div className="stat-card"><span className="stat-icon">{icon}</span><div className="stat-label">{label}</div><div className="stat-value">{value}</div><div className="stat-foot">{foot}</div></div>}
function Empty({title,text,action}:{title:string;text:string;action?:ReactNode}){return <div className="empty"><span className="empty-mark"><Inbox size={17}/></span><strong>{title}</strong><p>{text}</p>{action&&<div style={{marginTop:14}}>{action}</div>}</div>}
function Freshness({timestamp,label='Source'}:{timestamp:string;label?:string}){return <span className="subtext">{label} · demo data as of {fmtTime(timestamp)}</span>}

function Home({role,partner,requests}:{role:Role;partner:DemoPartner;requests:SupportRequest[]}) {
  const source=useDealRecords();
  if(role==='staff') {
    const open=requests.filter(r=>r.status==='Open').length;
    const inProgress=requests.filter(r=>r.status==='In progress').length;
    const needsHuman=requests.filter(r=>['Special pricing','Credit hold','Eligibility'].includes(r.category)).length;
    return <main className="main"><PageHeading eyebrow="Staff view · portfolio snapshot" title="A clear queue for the complex parts." subtitle="Review partner-submitted questions and keep sensitive decisions with the people who own them." action={<Link href="/requests" className="button"><Inbox size={14}/> Open request queue</Link>}/>
      <DemoNote/><div className="grid stats-grid" style={{marginTop:16}}><Stat icon={<Building2 size={16}/>} label="Demo partners" value={PARTNERS.length} foot="Sample partner identities"/><Stat icon={<Inbox size={16}/>} label="Open requests" value={open} foot="Waiting for assignment"/><Stat icon={<Clock3 size={16}/>} label="In progress" value={inProgress} foot="Being reviewed locally"/><Stat icon={<ShieldCheck size={16}/>} label="Human-owned topics" value={needsHuman} foot="Pricing, credit, eligibility"/></div>
      <div className="content-grid"><section className="panel"><div className="panel-head"><div><h2>Request queue</h2><div className="panel-meta">All requests saved in this browser</div></div><Link href="/requests" className="button secondary small">View queue <ArrowRight size={13}/></Link></div>
        {requests.length?<div className="panel-body record-list">{requests.slice(0,5).map(r=><RequestCard key={r.id} request={r} partner={PARTNERS.find(p=>p.id===r.partnerId)}/>)}</div>:<Empty title="No support requests yet" text="Partner questions will appear here after they submit a local demo request."/>}
      </section><section className="panel"><div className="panel-head"><div><h2>Partner portfolio</h2><div className="panel-meta">Read-only demo records</div></div><Link href="/partners" className="button secondary small">Portfolio <ArrowRight size={13}/></Link></div><div className="panel-body">{PARTNERS.map(p=><div className="signal-row" key={p.id}><div><strong>{p.name}</strong><small>{p.organization}</small></div><span className="subtext">Owner {p.owner}</span></div>)}</div></section></div>
      <SalesforceDataNotice/><p className="data-note" style={{marginTop:16}}>This portfolio combines live Salesforce demo registrations and labeled local examples. Support activity stays in this browser. Human reviewers own pricing, credit and eligibility outcomes; the app makes no CRM updates.</p></main>;
  }
  const deals=source.deals.filter(d=>d.partnerId===partner.id);
  const quotes=DEMO_QUOTES.filter(q=>q.partnerId===partner.id);
  const myRequests=requests.filter(r=>r.partnerId===partner.id);
  return <main className="main"><PageHeading eyebrow={`Partner view · ${partner.organization}`} title={`Good morning, ${partner.name}.`} subtitle="Check registration and quote status with a clear source for every record." action={<Link href="/help" className="button"><CircleHelp size={14}/> Ask a question</Link>}/>
    <DemoNote/>{partner.dataSource==='salesforce'&&<SalesforceDataNotice/>}<div className="grid stats-grid" style={{marginTop:16}}><Stat icon={<Handshake size={16}/>} label="Deal registrations" value={source.isLoading&&partner.dataSource==='salesforce'?'…':deals.length} foot="Your demo records only"/><Stat icon={<FileText size={16}/>} label="Quotes" value={quotes.length} foot="Local synthetic examples"/><Stat icon={<Inbox size={16}/>} label="Your requests" value={myRequests.length} foot="Saved in this browser"/><Stat icon={<Clock3 size={16}/>} label="Data mode" value={partner.dataSource==='salesforce'?'Salesforce':'Local'} foot={partner.dataSource==='salesforce'?'Read-only test org':'Synthetic examples'}/></div>
    <div className="content-grid"><section className="panel"><div className="panel-head"><div><h2>Deal registration activity</h2><div className="panel-meta">Latest statuses from your demo partner records</div></div><Link href="/deals" className="button secondary small">All deals <ArrowRight size={13}/></Link></div>{deals.length?<div className="table-wrap"><table><thead><tr><th>Registration</th><th>Status</th><th>Submitted</th><th>Next step</th></tr></thead><tbody>{deals.slice(0,4).map(d=><tr key={d.id}><td><Link href={`/deals/${d.id}`} className="record-title">{d.title}</Link><div className="subtext">{d.id}</div></td><td><Status value={d.status}/></td><td>{fmtDate(d.submittedAt)}</td><td>{d.nextStep}</td></tr>)}</tbody></table></div>:<Empty title="No demo registrations" text="There are no deal records for this partner identity."/>}</section>
      <section className="panel"><div className="panel-head"><div><h2>Quote progress</h2><div className="panel-meta">Record status, not a decision promise</div></div><Link href="/quotes" className="button secondary small">View quotes <ArrowRight size={13}/></Link></div><div className="panel-body">{quotes.slice(0,3).map(q=><div className="signal-row" key={q.id}><div><strong>{q.product}</strong><small>{q.id} · updated {fmtDate(q.lastUpdatedAt)}</small></div><Status value={q.status}/></div>)}{quotes.length===0&&<Empty title="No demo quotes" text="There are no quote records for this partner."/>}</div></section></div>
    <section className="panel" style={{marginTop:16}}><div className="panel-head"><div><h2>Need a person to look closer?</h2><div className="panel-meta">Sensitive requests route to the local staff demo queue</div></div><Link href="/help" className="button secondary small">Open help <ArrowRight size={13}/></Link></div><div className="panel-body"><div className="notice caution"><Headphones size={14}/>Special pricing, credit holds and eligibility questions need human review. This demo does not make or promise those decisions.</div></div></section>
  </main>;
}

function Deals({partner,role}:{partner:DemoPartner;role:Role}) {
  const [query,setQuery]=useState('');
  const source=useDealRecords();
  const records=useMemo(()=>source.deals.filter(d=>(role==='staff'||d.partnerId===partner.id)&&`${d.id} ${d.title} ${d.status} ${d.opportunityStage??''}`.toLowerCase().includes(query.toLowerCase())),[source.deals,partner.id,query,role]);
  return <main className="main"><PageHeading eyebrow={role==='partner'?`${partner.name} · demo records`:'Staff preview · demo records'} title="Deal registrations" subtitle="See submission progress, the latest recorded next step, and the source of each status." action={role==='partner'?<Link href="/help" className="button secondary"><BookOpen size={14}/> Registration guide</Link>:<Link href="/partners" className="button secondary"><Users size={14}/> Partner portfolio</Link>}/><DemoNote/>
    <div className="toolbar" style={{marginTop:16}}><div className="search-wrap"><Search size={14}/><input className="field" value={query} onChange={e=>setQuery(e.target.value)} aria-label="Search demo registrations" placeholder="Search registration ID, account, or status"/></div><span className="subtext">{records.length} demo record{records.length===1?'':'s'}{role==='partner'?` for ${partner.name}`:' across all partners'}</span></div>
    {records.length?<div className="record-list">{records.map(d=><DealCard key={d.id} deal={d}/>)}</div>:<Empty title="No registrations match" text="Try a different search or select another demo partner identity."/>}
    {(role==='staff'||partner.dataSource==='salesforce')&&<SalesforceDataNotice/>}
    <p className="data-note" style={{marginTop:15}}>Each record identifies its source. Salesforce demo registrations are live, read-only lookups; local examples are labeled separately. Registration approval is not the same as an Opportunity sales stage.</p></main>;
}
function DealCard({deal}:{deal:Deal}){
  const p=PARTNERS.find(x=>x.id===deal.partnerId)!;
  return <article className="record-card"><div>
    <h3><Link href={`/deals/${deal.id}`} className="record-title">{deal.title}</Link></h3>
    <p>{p.name} · {deal.id} · submitted {fmtDate(deal.submittedAt)}</p>
    <div className="record-meta"><span>Expected close {fmtDate(deal.expectedClose)}</span>
      {deal.opportunityStage&&<span>Opportunity stage: <strong>{deal.opportunityStage}</strong></span>}
      <span>{deal.sourceLabel}</span>
    </div>
  </div><div className="record-actions"><span className="subtext">Registration status</span><Status value={deal.status}/><Link className="icon-link" href={`/deals/${deal.id}`} aria-label={`Open ${deal.id}`}><ArrowUpRight size={15}/></Link></div></article>;
}
function DealDetail({id,partner,role}:{id:string;partner:DemoPartner;role:Role}) {
  const source=useDealRecords();
  const deal=source.deals.find(d=>d.id===id);
  if(!deal&&(source.isLoading||source.isError)&&/^DR-0/.test(id))return <main className="main"><SalesforceDataNotice/><Link href="/deals">Back to registrations</Link></main>;
  if(!deal||(role==='partner'&&deal.partnerId!==partner.id))return <main className="main"><Empty title="Registration not found" text="This record is not available in the selected demo partner view." action={<Link href="/deals" className="button secondary small">Back to registrations</Link>}/></main>;
  if(deal.salesforceId)return <SalesforceDealDetail deal={deal}/>;
  const owner=PARTNERS.find(p=>p.id===deal.partnerId)!;
  return <main className="main"><div className="eyebrow"><Link href="/deals">Deal registrations</Link> / {deal.id}</div><section className="detail-hero"><div className="eyebrow">Demo registration · {owner.name}</div><h1>{deal.title}</h1><p className="subtitle">{deal.id} · {deal.sourceLabel}</p><div className="detail-facts"><div><div className="fact-label">Current status</div><div className="fact-value"><Status value={deal.status}/></div></div><div><div className="fact-label">Submitted</div><div className="fact-value">{fmtDate(deal.submittedAt)}</div></div><div><div className="fact-label">Expected close</div><div className="fact-value">{fmtDate(deal.expectedClose)}</div></div></div></section>
    <div className="detail-grid"><section className="panel"><div className="panel-head"><div><h2>What happens next</h2><div className="panel-meta">Recorded next step; not an outcome guarantee</div></div><ArrowRight size={15}/></div><div className="panel-body"><p style={{fontSize:12,color:'#596a62',lineHeight:1.7,margin:0}}>{deal.nextStep}</p><div className="notice caution" style={{marginTop:14}}><ShieldCheck size={14}/>Registration status is a demo record. Approval and eligibility are determined by authorized people, not by this status lookup.</div></div></section>
      <section className="panel"><div className="panel-head"><div><h2>Evidence and freshness</h2><div className="panel-meta">Source details for this lookup</div></div><FileText size={15}/></div><div className="panel-body source-list"><div className="source-row"><FileText size={15}/><div><strong>{deal.sourceLabel}</strong><small>Local sample record · last refreshed {fmtTime(deal.submittedAt)}</small></div></div><div className="source-row"><UserRound size={15}/><div><strong>Record owner: {deal.owner}</strong><small>{owner.organization} · demo portfolio owner</small></div></div><Freshness timestamp={deal.submittedAt} label="Record timestamp"/></div></section></div>
    <div style={{marginTop:15}}><Link href="/help" className="button secondary"><LifeBuoy size={14}/> Ask about this registration</Link></div></main>;
}

function SalesforceDealDetail({deal}:{deal:Deal}) {
  return <main className="main">
    <div className="eyebrow"><Link href="/deals">Deal registrations</Link> / {deal.id}</div>
    <PageHeading eyebrow="Salesforce · read-only demo record" title={deal.title} subtitle={`${deal.id} · ${deal.sourceLabel}`}/>
    <DemoNote/><SalesforceDataNotice/>
    <section className="panel" style={{marginTop:16}}>
      <div className="panel-head"><h2>Registration and sales progress</h2></div>
      <div className="panel-body detail-facts salesforce-facts">
        <div><div className="fact-label">Registration status</div><Status value={deal.status}/></div>
        <div><div className="fact-label">Opportunity stage</div><div className="fact-value">{deal.opportunityStage}</div></div>
        <div><div className="fact-label">Expected close</div><div className="fact-value">{fmtDate(deal.expectedClose)}</div></div>
      </div>
    </section>
    <div className="detail-grid" style={{marginTop:16}}>
      <section className="panel"><div className="panel-head"><h2>Recorded next step</h2></div><div className="panel-body"><p>{deal.nextStep}</p><div className="notice caution">A registration approval is separate from the Opportunity stage. The agent cannot grant pricing, credit, or eligibility approvals.</div></div></section>
      <section className="panel"><div className="panel-head"><h2>Source evidence</h2></div><div className="panel-body">
        <p>{deal.sourceLabel}</p><p className="subtext">Salesforce record ID: {deal.salesforceId}</p>
        <p className="subtext">Submitted: {fmtTime(deal.submittedAt)}</p>
        <p className="subtext">Last modified in Salesforce: {fmtTime(deal.lastModifiedAt??'')}</p>
        <p className="subtext">The actual administrator's name is hidden in this public demo.</p>
      </div></section>
    </div>
    <Link href="/help" className="button secondary" style={{marginTop:16}}>Ask about this registration</Link>
  </main>;
}

function Quotes({partner,role}:{partner:DemoPartner;role:Role}) {
  const [query,setQuery]=useState('');
  const records=useMemo(()=>DEMO_QUOTES.filter(q=>(role==='staff'||q.partnerId===partner.id)&&`${q.id} ${q.product} ${q.status}`.toLowerCase().includes(query.toLowerCase())),[partner.id,query,role]);
  return <main className="main"><PageHeading eyebrow={role==='partner'?`${partner.name} · demo records`:'Staff preview · demo records'} title="Quote status" subtitle="A transparent snapshot of quote progress with the most recent recorded owner update." action={<Link href="/help" className="button secondary"><Headphones size={14}/> Ask about a quote</Link>}/><DemoNote/>
    <div className="notice caution" style={{marginTop:12}}>All quote examples are synthetic. Native Salesforce Quotes are not connected in this org. Opportunity stages are never presented as quote statuses. Select a local example partner to explore synthetic quotes.</div>
    <div className="toolbar" style={{marginTop:16}}><div className="search-wrap"><Search size={14}/><input className="field" value={query} onChange={e=>setQuery(e.target.value)} aria-label="Search quotes" placeholder="Search quote ID, product, or status"/></div><span className="subtext">{records.length} demo quote{records.length===1?'':'s'}</span></div>
    {records.length?<div className="record-list">{records.map(q=><QuoteCard key={q.id} quote={q}/>)}</div>:<Empty title="No quote records found" text="Try another search or choose another partner demo identity."/>}
    <section className="panel" style={{marginTop:16}}><div className="panel-head"><div><h2>Quote decisions stay human-owned</h2><div className="panel-meta">Pricing, credit and eligibility are not determined here</div></div><ShieldCheck size={16}/></div><div className="panel-body"><div className="notice caution"><CircleHelp size={14}/>Status lookup can explain what a demo record says. For special pricing, credit holds, or eligibility, submit a support request for human review.</div></div></section></main>;
}
function QuoteCard({quote}:{quote:Quote}){return <article className="record-card"><div><h3>{quote.product}</h3><p>{quote.id} · {quote.sourceLabel}</p><div className="record-meta"><span>Requested {fmtDate(quote.requestedAt)}</span><span>Owner {quote.owner}</span><span>Updated {fmtDate(quote.lastUpdatedAt)}</span></div><p style={{marginTop:10}}>{quote.nextStep}</p></div><div className="record-actions"><Status value={quote.status}/></div></article>}

function HelpPage({partner,onSubmit}:{partner:DemoPartner;onSubmit:(category:string,message:string)=>void}) {
  const source=useDealRecords();
  const [question,setQuestion]=useState('');
  const [answer,setAnswer]=useState<AgentAnswer|null>(null);
  const [answerError,setAnswerError]=useState(false);
  const [category,setCategory]=useState('General');
  const [message,setMessage]=useState('');
  const [formError,setFormError]=useState('');
  const lookupToken=useRef(0);
  const [threadId,setThreadId]=useState(()=>getOrCreateThreadId(partner.id));
  const supportFormRef=useRef<HTMLElement|null>(null);
  useEffect(()=>{
    lookupToken.current+=1;
    setAnswer(null);
    setAnswerError(false);
    setThreadId(getOrCreateThreadId(partner.id));
    setQuestion('');
    setMessage('');
    setCategory('General');
    setFormError('');
  },[partner.id]);
  const answerMutation=useAnswerPartnerQuestion();
  const partnerDeals=source.deals.filter(d=>d.partnerId===partner.id);
  const partnerQuotes=DEMO_QUOTES.filter(q=>q.partnerId===partner.id);
  const groundedFallback=(value:string) => {
    const q=value.toLowerCase();
    if(sensitiveCategory(value))return null;
    const requestedIds=new Set((value.match(/\b(?:DR-\d+|Q-\d+)\b/gi)??[]).map(id=>id.toUpperCase()));
    const deal=partnerDeals.find(record=>requestedIds.has(record.id));
    if(deal)return {
      text:`${deal.title} (${deal.id}) is recorded as “${deal.status}” in this local demo record. ${deal.nextStep}`,
      sources:[{label:`${deal.sourceLabel} · ${deal.id} · ${deal.title}`,timestamp:deal.submittedAt}]
    };
    const quote=partnerQuotes.find(record=>requestedIds.has(record.id));
    if(quote)return {
      text:`${quote.product} (${quote.id}) is recorded as “${quote.status}” in this local demo record. ${quote.nextStep}`,
      sources:[{label:`${quote.sourceLabel} · ${quote.id} · ${quote.product}`,timestamp:quote.lastUpdatedAt}]
    };
    if(/guide|register|registration|submit|submission|process|steps|required information/.test(q))
      return {
        text:`${ARTICLES[0].title}: ${ARTICLES[0].summary} ${ARTICLES[0].steps.join(' ')}`,
        sources:[{label:`${ARTICLES[0].sourceLabel} · ${ARTICLES[0].title}`,timestamp:ARTICLES[0].updatedAt}]
      };
    return null;
  };
  const runLookup=async(value:string)=>{
    const trimmed=value.trim();
    if(!trimmed){setAnswer(null);setAnswerError(false);return}
    if(trimmed.length>1000){setAnswer(null);setAnswerError(true);return}
    const token=++lookupToken.current;
    setAnswer(null);setAnswerError(false);
    try {
      const result=await answerMutation.mutateAsync({data:{question:trimmed.slice(0,1000),partnerId:partner.id,threadId}});
      if(token!==lookupToken.current)return;
      setAnswer({
        text:result.answer,mode:result.mode,provider:result.provider,intent:result.intent,
        handoffRequired:result.handoffRequired,handoffCategory:result.handoffCategory,
        sources:result.sources,trace:result.trace,toolCalls:result.toolCalls
      });
    } catch {
      if(token!==lookupToken.current)return;
      setAnswerError(true);
      const fallback=groundedFallback(trimmed);
      setAnswer({
        text:fallback?.text??"I couldn't verify this from the local demo records. Use the support form below to request human help.",
        mode:'fallback',provider:'Local browser fallback',intent:fallback?'exact_match':'unknown',
        handoffRequired:!fallback,handoffCategory:fallback?'':sensitiveCategory(trimmed)||'General',
        sources:fallback?.sources??[],trace:['Agent service unavailable; local exact-match fallback used.'],
        toolCalls:[]
      });
    }
  };
  const lookup=(event:FormEvent)=>{event.preventDefault();void runLookup(question)};
  const submit=(e:FormEvent)=>{e.preventDefault();if(message.trim().length<8){setFormError('Add a little more context so a reviewer can understand the question.');return}setFormError('');onSubmit(category,message.trim());setMessage('');};
  const prepareHandoff=()=>{
    if(!answer)return;
    setCategory(answer.handoffCategory||'General');
    setMessage(question.trim());
    supportFormRef.current?.scrollIntoView({behavior:'smooth',block:'start'});
  };
  const startNewConversation=()=>{
    lookupToken.current+=1;
    const nextThread=createThreadId(partner.id);
    try { localStorage.setItem(threadStorageKey(partner.id),nextThread); } catch {}
    setThreadId(nextThread);
    setAnswer(null);
    setAnswerError(false);
    setQuestion('');
  };
  return <main className="main"><PageHeading eyebrow={`Partner help · ${partner.name}`} title="A quick answer, or a person to help." subtitle="Look up routine status from your demo records. Send sensitive or unusual questions to the local staff queue."/><DemoNote/>
    <div className="question-layout" style={{marginTop:16}}><div className="grid">
      <section className="panel"><div className="panel-head"><div><h2>Ask about deal or quote progress</h2><div className="panel-meta">Stateful LangGraph agent · read-only synthetic partner tools</div></div><Search size={15}/></div><div className="panel-body"><form onSubmit={lookup}><div className="form-field"><label htmlFor="question">Registration ID, quote ID, product, or question</label><input id="question" className="field" maxLength={1000} value={question} onChange={e=>setQuestion(e.target.value)} placeholder="For example: DR-2841 or Q-73108"/></div><span className="helper">Do not enter confidential customer or payment details. Special pricing, credit holds, and eligibility are routed for human review.</span><div className="form-actions"><button className="button" type="submit" disabled={answerMutation.isPending}><Search size={14}/>{answerMutation.isPending?'Running the agent graph…':'Get an answer'}</button><button className="button secondary small" type="button" onClick={startNewConversation}>New conversation</button></div></form>
        {answerMutation.isPending&&<div className="answer-box" aria-live="polite"><div className="loading-block"/><p className="helper" style={{margin:'9px 0 0'}}>Running the safety gate, read-only lookup tools, and answer grounding check…</p></div>}
        {answerError&&<div className="notice caution" role="alert" style={{marginTop:12}}><CircleHelp size={14}/><span>The answer service could not complete this lookup. It may be unavailable or not configured. {answer?'A grounded local fallback is shown below; it is not AI.':'No grounded local answer is available for this question.'}<button type="button" className="button secondary small" style={{marginLeft:9}} onClick={()=>void runLookup(question)} disabled={answerMutation.isPending}>Retry</button></span></div>}
        {answer&&<div className="answer-box" aria-live="polite"><div style={{display:'flex',justifyContent:'space-between',gap:10,alignItems:'center',marginBottom:8}}><h3>{answer.mode==='ai'?'LangGraph + Nebius AI':'Fallback response · not AI'}</h3><span className="subtext">{answer.provider}</span></div><p style={{whiteSpace:'pre-line'}}>{answer.text}</p><div className="source-list" style={{marginTop:11}}><strong className="mini-label">Evidence used for this answer</strong>{answer.sources.length?answer.sources.map((source,index)=><div className="source-row" key={`${source.label}-${index}`}><FileText size={14}/><div><strong>{source.label}</strong><small>Source record timestamp: {fmtTime(source.timestamp)}</small></div></div>):<div className="source-row"><FileText size={14}/><div><strong>No verified source citation</strong><small>The agent withheld an unsupported answer.</small></div></div>}</div><details style={{marginTop:12,borderTop:'1px solid #e6ebe7',paddingTop:10}}><summary className="mini-label" style={{cursor:'pointer'}}>Agent run trace · {answer.toolCalls.length} read-only tool call{answer.toolCalls.length===1?'':'s'}</summary><ol style={{margin:'9px 0 0',paddingLeft:20,fontSize:10,color:'#596a62',lineHeight:1.7}}>{answer.trace.map((step,index)=><li key={`${step}-${index}`}>{step}</li>)}</ol></details>{answer.handoffRequired&&<div className="notice caution" style={{marginTop:12}}><CircleHelp size={14}/><span>{answer.handoffCategory||'Human review'} needed. No decision was made. <button type="button" className="button secondary small" style={{marginLeft:8}} onClick={prepareHandoff}>Prepare support request</button></span></div>}</div>}
      </div></section>
      <section className="panel"><div className="panel-head"><div><h2>Deal registration guide</h2><div className="panel-meta">A short local guide for partners</div></div><BookOpen size={15}/></div><div className="panel-body"><h3>{ARTICLES[0].title}</h3><p style={{fontSize:10,color:'#77827b',lineHeight:1.55,margin:'7px 0 13px'}}>{ARTICLES[0].summary}</p><div className="guide-steps">{ARTICLES[0].steps.map((step,i)=><div className="guide-step" key={step}><span className="step-number">{i+1}</span><p>{step}</p></div>)}</div><p className="data-note" style={{marginTop:12}}>Updated {fmtTime(ARTICLES[0].updatedAt)} · {ARTICLES[0].sourceLabel}</p></div></section>
    </div><section className="panel" ref={supportFormRef}><div className="panel-head"><div><h2>Ask for support</h2><div className="panel-meta">Creates a local request only; no message is sent</div></div><MessageSquareText size={15}/></div><div className="panel-body"><form onSubmit={submit}><div className="form-grid"><div className="form-field full"><label htmlFor="category">Question category</label><select id="category" className="select" style={{width:'100%'}} value={category} onChange={e=>setCategory(e.target.value)}>{['General','Deal registration','Quote status','Product positioning','Renewals','Enablement content','Special pricing','Credit hold','Eligibility'].map(value=><option key={value}>{value}</option>)}</select><span className="helper">Pricing, credit and eligibility decisions are owned by human reviewers.</span></div><div className="form-field full"><label htmlFor="support-message">What should the team know?</label><textarea id="support-message" className="textarea" value={message} onChange={e=>setMessage(e.target.value)} placeholder="Include a deal or quote ID and the context a reviewer needs."/><span className="helper">Your request is stored locally in this browser for the demo. Do not enter sensitive customer or payment data.</span></div></div>{formError&&<p role="alert" style={{color:'#9b4137',fontSize:10,margin:'10px 0 0'}}>{formError}</p>}<div className="form-actions"><button className="button" type="submit"><MessageSquareText size={14}/> Save support request</button></div></form></div></section></div>
    </main>;
}

function RequestsPage({role,partner,requests,onUpdate}:{role:Role;partner:DemoPartner;requests:SupportRequest[];onUpdate:(id:string,updates:Partial<SupportRequest>)=>void}) {
  const [filter,setFilter]=useState('All statuses');
  const [category,setCategory]=useState('All categories');
  const visible=requests.filter(r=>(role==='staff'||r.partnerId===partner.id)&&(filter==='All statuses'||r.status===filter)&&(category==='All categories'||r.category===category));
  return <main className="main"><PageHeading eyebrow={role==='staff'?'Internal workflow · local demo':'Partner support · local demo'} title={role==='staff'?'Support request queue':'Your support requests'} subtitle={role==='staff'?'Review context, assign ownership, update status, and record a human response or decision.':'Track questions you have saved to the local staff demo queue.'} action={role==='partner'?<Link href="/help" className="button"><MessageSquareText size={14}/> New request</Link>:undefined}/><DemoNote/>
    {role==='staff'&&<div className="metric-strip" style={{marginTop:16}}><div className="metric"><strong>{requests.length}</strong><span>Total requests</span></div><div className="metric"><strong>{requests.filter(r=>r.status==='Open').length}</strong><span>Open</span></div><div className="metric"><strong>{requests.filter(r=>r.status==='In progress').length}</strong><span>In progress</span></div><div className="metric"><strong>{requests.filter(r=>r.status==='Resolved').length}</strong><span>Resolved</span></div></div>}
    <div className="toolbar" style={{marginTop:16}}><select className="select" value={filter} onChange={e=>setFilter(e.target.value)} aria-label="Filter requests by status"><option>All statuses</option>{['Open','In progress','Waiting on partner','Resolved'].map(s=><option key={s}>{s}</option>)}</select><select className="select" value={category} onChange={e=>setCategory(e.target.value)} aria-label="Filter requests by category"><option>All categories</option>{['General','Deal registration','Quote status','Product positioning','Renewals','Enablement content','Special pricing','Credit hold','Eligibility'].map(s=><option key={s}>{s}</option>)}</select><span className="subtext">{visible.length} request{visible.length===1?'':'s'}</span></div>
    {visible.length?<div className="record-list">{visible.map(r=><RequestCard key={r.id} request={r} partner={PARTNERS.find(p=>p.id===r.partnerId)} onUpdate={onUpdate}/>)}</div>:<Empty title={role==='staff'?'Queue is clear':'No requests yet'} text={role==='staff'?'New partner demo support requests will appear here.':'Use help to ask for human review of a pricing, credit, eligibility, or general question.'} action={role==='partner'?<Link href="/help" className="button small">Open help</Link>:undefined}/>}</main>;
}
function RequestCard({request,partner,onUpdate}:{request:SupportRequest;partner?:DemoPartner;onUpdate?:(id:string,updates:Partial<SupportRequest>)=>void}) {
  return <article className="request-card"><div><h3><Link href={`/requests/${request.id}`} className="record-title">{request.category} · {partner?.name||'Partner request'}</Link></h3><p>{request.message}</p><div className="request-meta"><span>{request.id}</span><span>Created {fmtDate(request.createdAt)}</span><span>Assigned: {request.assignee||'Unassigned'}</span></div>{request.response&&<p><strong>Recorded response:</strong> {request.response}</p>}</div><div style={{display:'grid',justifyItems:'end',gap:9}}><Status value={request.status}/><Link className="button secondary small" href={`/requests/${request.id}`}>Open details <ArrowRight size={12}/></Link>{onUpdate&&request.status==='Open'&&<button className="button small" onClick={()=>onUpdate(request.id,{status:'In progress',assignee:'Partner operations'})}>Assign to operations</button>}</div></article>;
}
function RequestDetail({id,role,partner,requests,onUpdate}:{id:string;role:Role;partner:DemoPartner;requests:SupportRequest[];onUpdate:(id:string,updates:Partial<SupportRequest>)=>void}) {
  const req=requests.find(r=>r.id===id);
  const [response,setResponse]=useState(req?.response||'');
  const [assignee,setAssignee]=useState(req?.assignee||'Unassigned');
  useEffect(()=>{setResponse(req?.response||'');setAssignee(req?.assignee||'Unassigned');},[id,req?.response,req?.assignee]);
  if(!req||(role==='partner'&&req.partnerId!==partner.id))return <main className="main"><Empty title="Request not found" text="This request is not available in the selected demo view." action={<Link href="/requests" className="button secondary small">Back to requests</Link>}/></main>;
  const owner=PARTNERS.find(p=>p.id===req.partnerId)!;
  const save=()=>onUpdate(req.id,{response:response.trim(),assignee,status:response.trim()&&req.status==='Open'?'In progress':req.status});
  return <main className="main"><div className="eyebrow"><Link href="/requests">{role==='staff'?'Request queue':'My requests'}</Link> / {req.id}</div><PageHeading eyebrow={`${req.category} · ${owner.name}`} title="Request details" subtitle="Review the partner’s context and the local history for this request."/><DemoNote/>
    <div className="detail-grid" style={{marginTop:16}}><section className="panel"><div className="panel-head"><div><h2>Partner context</h2><div className="panel-meta">{req.id} · created {fmtTime(req.createdAt)}</div></div><Status value={req.status}/></div><div className="panel-body"><div className="signal-row"><div><strong>Partner</strong><small>{owner.organization}</small></div><span>{owner.name}</span></div><div className="signal-row"><div><strong>Category</strong><small>Human review routing</small></div><span>{req.category}</span></div><div style={{padding:'14px 0',borderBottom:'1px solid #efede5'}}><div className="mini-label">Partner question</div><p style={{whiteSpace:'pre-wrap',fontSize:12,lineHeight:1.65,color:'#52635b',margin:'7px 0 0'}}>{req.message}</p></div>{req.response&&<div style={{paddingTop:14}}><div className="mini-label">Recorded response or decision</div><p style={{fontSize:11,lineHeight:1.6,color:'#52635b',margin:'7px 0 0'}}>{req.response}</p></div>}</div></section>
      {role==='staff'?<section className="panel"><div className="panel-head"><div><h2>Staff handling</h2><div className="panel-meta">Local status and response record</div></div><ShieldCheck size={15}/></div><div className="panel-body"><div className="request-controls"><div className="form-field"><label htmlFor="request-status">Request status</label><select id="request-status" className="select" style={{width:'100%'}} value={req.status} onChange={e=>onUpdate(req.id,{status:e.target.value})}>{['Open','In progress','Waiting on partner','Resolved'].map(s=><option key={s}>{s}</option>)}</select></div><div className="form-field"><label htmlFor="request-assignee">Assignee</label><select id="request-assignee" className="select" style={{width:'100%'}} value={assignee} onChange={e=>setAssignee(e.target.value)}>{['Unassigned','Partner operations','Channel manager','Pricing team','Credit team','Eligibility team'].map(s=><option key={s}>{s}</option>)}</select></div><div className="form-field"><label htmlFor="request-response">Response or decision note</label><textarea id="request-response" className="textarea" value={response} onChange={e=>setResponse(e.target.value)} placeholder="Record a human-owned response or next step."/><span className="helper">This saves locally only. It is not sent to the partner. Pricing, credit, and eligibility require the appropriate human authority.</span></div><button className="button" onClick={save}><Check size={14}/> Save local response</button></div></div></section>:<section className="panel"><div className="panel-head"><div><h2>Request progress</h2><div className="panel-meta">Visible in this local demo only</div></div><Clock3 size={15}/></div><div className="panel-body"><p style={{color:'#647269',fontSize:11,lineHeight:1.6}}>Status: <Status value={req.status}/></p><p className="data-note">Last updated {fmtTime(req.updatedAt)}. Staff response is recorded here if one has been added.</p><Link href="/help" className="button secondary small">Ask another question</Link></div></section>}
    </div></main>;
}

function Portfolio({role,requests}:{role:Role;requests:SupportRequest[]}) {
  const source=useDealRecords();
  const [search,setSearch]=useState('');
  if(role!=='staff')return <main className="main"><Empty title="Staff view only" text="The partner portfolio is available in the Staff demo view. This role selector is not secure authentication." action={<Link className="button secondary small" href="/">Back to partner home</Link>}/></main>;
  const rows=PARTNERS.filter(p=>`${p.name} ${p.organization} ${p.owner}`.toLowerCase().includes(search.toLowerCase()));
  return <main className="main"><PageHeading eyebrow="Staff workspace · portfolio" title="Partner portfolio" subtitle="Read-only sample records with a clear view of support demand by partner."/><DemoNote/><div className="toolbar" style={{marginTop:16}}><div className="search-wrap"><Search size={14}/><input className="field" aria-label="Search partner portfolio" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search partner, organization, or owner"/></div><span className="subtext">{rows.length} of {PARTNERS.length} partners</span></div>
    <SalesforceDataNotice/>
    {rows.length?<div className="record-list">{rows.map(p=>{const deals=source.deals.filter(d=>d.partnerId===p.id).length;const quotes=DEMO_QUOTES.filter(q=>q.partnerId===p.id).length;const reqs=requests.filter(r=>r.partnerId===p.id);return <article className="record-card" key={p.id}><div><h3>{p.name}</h3><p>{p.organization} · {p.dataSource==='salesforce'?'Salesforce demo records':`partner owner ${p.owner}`}</p><div className="record-meta"><span>{deals} demo registrations</span><span>{quotes} synthetic quotes</span><span>{reqs.length} support requests</span></div></div><Link href="/requests" className="button secondary small">View queue <ArrowRight size={12}/></Link></article>})}</div>:<Empty title="No partner matches" text="Try a different search."/>}
  </main>;
}
function NotFound(){return <main className="main"><Empty title="Page not found" text="This page is not part of the local Partner Operations Copilot demo." action={<Link href="/" className="button secondary small">Return home</Link>}/></main>}

export default App;
