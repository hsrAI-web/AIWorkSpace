from pathlib import Path
from streamlit.testing.v1 import AppTest

app=Path(__file__).resolve().with_name('app.py')
at=AppTest.from_file(str(app),default_timeout=90).run()
assert not at.exception
# Missing context should stop before models/API calls.
at.form_submit_button[0].click().run()
assert not at.exception
assert at.session_state['result']['state']['status']=='needs_clarification'
# Fictional matching product: exercise real retrieval, no generation.
at.checkbox(key='confirmed').check()
at.selectbox(key='claim_type').select('Reimbursement')
at.form_submit_button[0].click().run()
assert not at.exception
state=at.session_state['result']['state']
assert state['status']=='evidence_only' and len(state['evidence'])==5
assert 'api_key' not in state
# Generation cannot proceed without valid provider configuration.
at.radio(key='mode').set_value('Generate answer').run()
at.form_submit_button[0].click().run()
assert not at.exception
assert at.error and at.session_state['result'] is None
print('Interface checks passed: initial render, clarification, real retrieval, credential gate.')

