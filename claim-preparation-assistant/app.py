"""Local claim-preparation interface. Credentials stay out of graph state."""
import json
import threading
import hashlib
import importlib
from time import perf_counter
from urllib.parse import urlparse
import streamlit as st
# Streamlit can rerun this file while imported local functions remain cached.
# Refresh these lightweight modules in dependency order without restarting the
# server or clearing the session-only provider settings.
import claim_workflow as _workflow
import live_evaluation as _evaluation
importlib.reload(_workflow)
importlib.reload(_evaluation)
from claim_workflow import UIN, build_graph, provider_generator, GROUNDING_PROMPT
from retrieval import Retriever
from live_evaluation import run_suite
from retrieval import ROOT

st.set_page_config(page_title='Claim preparation assistant',page_icon=':material/checklist:',layout='centered')
st.session_state.setdefault('result',None)
st.session_state.setdefault('evaluation',None)
st.session_state.setdefault('regression',None)

@st.cache_resource(max_entries=1)
def retrieval_resource(index_version):
    return Retriever(), threading.Lock()

def current_index_version():
    return hashlib.sha256((ROOT/'data/chunks-section.json').read_bytes()).hexdigest()

def clear_private_session():
    st.session_state['api_key']=''
    st.session_state['result']=None
    st.session_state['evaluation']=None
    st.session_state['regression']=None

st.title('Claim preparation assistant')
st.caption('Know what to prepare. See what is missing. Check every source.')
st.caption('HDFC ERGO my:Optima Secure · Reimbursement paperwork')
with st.expander('About this assistant and its document scope'):
    st.write(f'This learning prototype uses the claim manual and reviewed form passages for UIN {UIN}. It cannot verify your issued policy, approve a claim, or check live claim status. Use fictional examples while testing.')

with st.sidebar:
    st.header('Your assistant')
    st.caption('Submission guidance, backed by source documents.')
    configured=bool(st.session_state.get('api_key','').strip() and st.session_state.get('model','').strip() and urlparse(st.session_state.get('endpoint','').strip()).scheme=='https' and urlparse(st.session_state.get('endpoint','').strip()).hostname)
    if configured:
        st.success('AI answers enabled',icon=':material/check_circle:')
    else:
        st.info('Checklist and sources available. Connect AI below for a written answer.')
    with st.expander('AI connection',expanded=not configured):
        st.text_input('Nebius API key',type='password',key='api_key')
        endpoint=st.text_input('API base URL',placeholder='Copy the OpenAI-compatible endpoint from your provider console',key='endpoint')
        model=st.text_input('Model ID',placeholder='Exact model identifier from your console',key='model')
        if st.button('Test API connection'):
            from openai import OpenAI
            if st.session_state.get('api_key') and model and urlparse(endpoint).scheme=='https':
                try:
                    with OpenAI(api_key=st.session_state.api_key,base_url=endpoint,timeout=12,max_retries=0) as client:
                        client.chat.completions.create(model=model,max_tokens=16,
                            messages=[{'role':'user','content':'Reply with OK.'}])
                    st.success('Provider and model responded successfully.')
                except Exception as exc:
                    cause=type(exc.__cause__).__name__ if exc.__cause__ else ''
                    st.error(f'Connection test failed: {type(exc).__name__} ({cause}).')
            else:
                st.error('Enter your key, HTTPS base URL and model ID first.')
        st.caption('The key stays in this local server session. It is not saved to project files or included in results.')
        st.button('Clear key and result',on_click=clear_private_session)
        st.caption('Asking with AI connected sends your question, document names and source passages to your provider.')

with st.form('claim_question'):
    st.subheader('How can we help?')
    question=st.text_area('What do you need help with?',
        value='',placeholder='For example: I have my discharge summary and hospital bill. What else do I need?',height=110,key='question')
    have=st.text_area('Documents you already have (one name per line)',
                      value='',placeholder='Discharge summary\nHospital bill',height=90,key='have')
    st.caption('Enter document names only. Do not enter identity numbers, bank details or medical records.')
    context={}
    with st.expander('Optional details · make your checklist more specific'):
        claim_type=st.selectbox('Claim type',['Reimbursement','Cashless','Not sure'],key='claim_type')
        checklist_scope=st.selectbox('Document checklist scope',
            ['Hospitalisation / day care','Other / not sure'],key='checklist_scope')
        for key,label in [('accident','Was this an accident?'),('implant','Was an implant used?'),
                          ('non_network','Was the hospital outside the network?'),
                          ('death','Does the claim involve a death?'),
                          ('ambulance','Are ambulance expenses being claimed?'),
                          ('vaccination','Are vaccination expenses being claimed?'),
                          ('requested_indoor','Has the insurer requested indoor case papers?'),
                          ('legal_heir','Has a legal heir/succession certificate been requested or confirmed applicable?')]:
            answer=st.selectbox(label,['Not sure','Yes','No'],key='context_'+key)
            context[key]={'Yes':'yes','No':'no','Not sure':'unknown'}[answer]
        amount=st.selectbox('Claim amount band',['Not sure','Above INR 100,000','INR 100,000 or below'],key='amount_band')
        context['amount_band']='above_100000' if amount=='Above INR 100,000' else 'unknown_or_below'
    submitted=st.form_submit_button('Ask assistant',type='primary',icon=':material/arrow_forward:',width='stretch')
    st.caption('You will get a document checklist and sources. AI adds a cited draft answer when connected.')

if submitted:
    st.session_state.result=None
    api_key=st.session_state.get('api_key','').strip()
    config_ok=bool(api_key and model.strip() and urlparse(endpoint.strip()).scheme=='https'
                   and urlparse(endpoint.strip()).hostname)
    generate=config_ok
    state=dict(question=question.strip(),uin=UIN,
               claim_type='reimbursement' if claim_type=='Reimbursement' else '',
               documents_reported=[x.strip() for x in have.splitlines() if x.strip()],generate=generate,
               context=context,checklist_scope='hospitalisation' if checklist_scope=='Hospitalisation / day care' else 'other')
    try:
        with st.spinner('Finding relevant requirements…'):
            start=perf_counter()
            if state['uin'] and state['claim_type'] and state['question']:
                engine,lock=retrieval_resource(current_index_version())
                callback=provider_generator(api_key,model.strip(),endpoint.strip()) if generate else None
                verifier=provider_generator(api_key,model.strip(),endpoint.strip(),GROUNDING_PROMPT) if generate else None
                with lock:
                    result=build_graph(engine,callback,verifier).invoke(state)
            else:
                result=build_graph().invoke(state)
            st.session_state.result={'state':result,'seconds':perf_counter()-start}
    except Exception as exc:
        st.error(f'Could not complete retrieval ({type(exc).__name__}). Your key has not been included in this error.')

if st.session_state.result:
    result=st.session_state.result['state']
    st.divider()
    st.subheader('Your guidance')
    st.caption('For: '+result.get('question',''))
    st.caption(f"Completed in {st.session_state.result['seconds']:.2f} seconds · Based on the selected document set")
    answer_tab, checklist_tab, sources_tab=st.tabs(['Answer','Document checklist','Sources'])
    with answer_tab:
        for question_to_ask in result.get('questions',[]):
            st.info(question_to_ask)
        if result.get('error'):
            st.warning('We could not verify a reliable answer. You can still inspect the checklist and source passages.')
            with st.expander('Why was the answer withheld?'):
                st.text(result['error'])
        answer=result.get('answer')
        if answer:
            if result['status']=='generated_checked':
                st.warning('Draft answer: citation IDs and a model-based grounding check passed. Review against the sources; these checks do not guarantee correctness.')
            elif result['status']!='insufficient_evidence':
                st.warning('Earlier draft: citation IDs were checked, but no model grounding pass is recorded for this answer.')
            if answer['insufficient_evidence']:
                st.info('The retrieved evidence is insufficient for part or all of this question.')
            for number,statement in enumerate(answer['statements'],1):
                st.text(statement['text'])
                st.caption('Sources: '+', '.join(statement['citations']))
                if statement.get('evidence_quotes'):
                    with st.expander(f'Supporting excerpts for statement {number}'):
                        for quote in statement['evidence_quotes']:
                            st.caption(quote['citation'])
                            st.text(quote['quote'])
            for followup in answer['clarification_questions']:
                st.info(followup)
        elif result.get('status')=='evidence_only':
            st.info('Your checklist and source passages are ready. Open AI connection in the sidebar to add a written explanation.')
            st.caption('Choose Document checklist to see requirements and reported documents, or Sources to read the evidence.')
    with checklist_tab:
        checklist=result.get('checklist')
        if checklist:
            st.subheader('Document checklist')
            st.caption('Based on the reported document names and details you selected. This does not certify submission readiness.')
            rows=[{'Document':i['requirement'],'Applicability':i['applicability'].replace('_',' '),
                   'Your report':i['possession'].replace('_',' '),'Source':i['section']} for i in checklist['items']]
            if rows:
                st.dataframe(rows,hide_index=True,alt='Document requirements, applicability, reported possession and source clauses')
                with st.expander('Check the exact source requirements'):
                    for item in checklist['items']:
                        st.text(f"{item['requirement']} — {item['section']}")
                        st.text(item['source_text'])
                        st.link_button(f"Open {item['section']}",item['url']+f"#page={item['pages'][0]}")
            if checklist['unmatched_reported']:
                st.info('Names needing clarification: '+', '.join(checklist['unmatched_reported'])+'. Try a complete document name; unmatched does not mean rejected.')
            for followup in checklist['questions']:
                st.caption(followup)
    with sources_tab:
        if result.get('evidence'):
            st.subheader('Source passages')
            for passage in result['evidence']:
                pages=', '.join(map(str,passage['pages']))
                with st.expander(f"{passage['id']} · {passage['source_id']} · page(s) {pages}"):
                    st.caption(passage['section'])
                    st.text(passage['text'])
                    st.link_button('Open original source',passage['url']+f"#page={passage['pages'][0]}")
            st.download_button('Download result (no API key)',json.dumps(result,ensure_ascii=False,indent=2),
                               file_name='claim-preparation-result.json',mime='application/json')

st.divider()
with st.expander('Developer tools · project evaluation'):
    st.caption('Uses the provider settings above. Up to 30 generation calls (one correction per question) plus 15 grounding-review calls; consumes credits. Fictional results are saved locally without credentials. Independent human review is needed to measure faithfulness.')
    run_evaluation=st.button('Run 15-question evaluation',key='run_evaluation')
    run_regression=st.button('Retest revised answer checks (9 questions)',key='run_regression')
    if st.button('Show last completed evaluation'):
        saved=ROOT/'data/live-evaluation.json'
        if saved.exists():
            st.session_state.evaluation=json.loads(saved.read_text(encoding='utf-8'))
            st.session_state.regression=None
        else:
            st.info('No completed evaluation has been saved yet.')
    if run_evaluation or run_regression:
        key=st.session_state.get('api_key','').strip()
        if not key or not model.strip() or urlparse(endpoint.strip()).scheme!='https' or not urlparse(endpoint.strip()).hostname:
            st.error('Enter valid provider settings in the sidebar first.')
        else:
            if run_regression:
                st.session_state.regression=None
            else:
                st.session_state.evaluation=None
                st.session_state.regression=None
            progress=st.progress(0,text='Preparing local retrieval')
            try:
                engine,lock=retrieval_resource(current_index_version())
                callback=provider_generator(key,model.strip(),endpoint.strip())
                verifier=provider_generator(key,model.strip(),endpoint.strip(),GROUNDING_PROMPT)
                with lock:
                    report=run_suite(engine,callback,model.strip(),
                        lambda n,total:progress.progress(n/total,text=f'Completed {n} of {total} questions'),
                        verifier=verifier,case_ids=['01','02','03','05','06','08','13','14','15'] if run_regression else None,
                        checkpoint_path=ROOT/('data/live-progress-focused.json' if run_regression else 'data/live-progress-full.json'))
                if run_regression:
                    st.session_state.regression=report
                else:
                    st.session_state.evaluation=report
            except Exception as exc:
                st.error(f'Evaluation could not start ({type(exc).__name__}).')
    report=st.session_state.evaluation
    if st.session_state.regression:
        regression=st.session_state.regression
        (ROOT/'data/live-regression.json').write_text(json.dumps(regression,ensure_ascii=False,indent=2),encoding='utf-8')
        st.caption('Latest focused retest: '+', '.join(f"{c['case']}: {c['result']['status']}" for c in regression['cases']))
    if report:
        # Persist the explicitly requested fictional test results, never credentials.
        (ROOT/'data/live-evaluation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        summary=report['automatic_summary']
        if 'grounding_passed' in summary:
            st.info(f"{summary['generated']}/{summary['total']} questions produced answer drafts; {summary['grounding_passed']} passed the model grounding check. This is not an accuracy score.")
        else:
            st.info(f"{summary['generated']}/{summary['total']} questions produced drafts. Grounding was not run for this earlier report.")
        st.download_button('Download evaluation for review',json.dumps(report,ensure_ascii=False,indent=2),
            file_name='claim-assistant-live-evaluation.json',mime='application/json',key='download_evaluation')
        for row in report['cases']:
            with st.expander(f"Question {row['case']} · {row['result']['status']}"):
                st.text(row['question'])
                st.caption('Review against: '+row['expectation'])
                st.json(row['result'].get('answer',row['result'].get('error','No generated answer')))
