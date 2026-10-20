from pathlib import Path
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from types import SimpleNamespace
import json

app=Path(__file__).resolve().with_name('app.py')
at=AppTest.from_file(str(app),default_timeout=90).run()
assert not at.exception
assert not at.radio
assert not any(c.key=='confirmed' for c in at.checkbox)
# Missing context should stop before models/API calls.
at.form_submit_button[0].click().run()
assert not at.exception
assert at.session_state['result']['state']['status']=='needs_clarification'
# Fictional matching product: exercise real retrieval, no generation.
at.text_area(key='question').set_value('I have my discharge summary and hospital bill. What else do I need?')
at.text_area(key='have').set_value('Discharge summary\nHospital bill')
at.form_submit_button[0].click().run()
assert not at.exception
state=at.session_state['result']['state']
assert state['status']=='evidence_only' and len(state['evidence'])==5
assert 'api_key' not in state
assert [t.label for t in at.tabs]==['Answer','Document checklist','Sources']
assert state['uin']=='HDFHLIP25041V062425'
# Valid configuration automatically enables generation, without a mode switch.
at.text_input(key='api_key').set_value('test-only-key')
at.text_input(key='endpoint').set_value('https://example.invalid/v1')
at.text_input(key='model').set_value('mock-model')
with patch('openai.OpenAI') as provider:
    raw=json.dumps(dict(statements=[],clarification_questions=[],insufficient_evidence=True))
    provider.return_value.chat.completions.create.return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=raw))])
    at.form_submit_button[0].click().run()
    assert not at.exception
    assert provider.called
    state=at.session_state['result']['state']
    assert state['generate'] and state['status']=='insufficient_evidence'
    assert 'test-only-key' not in json.dumps(state)
# An incomplete connection preserves checklist and source access.
at.text_input(key='endpoint').set_value('http://example.invalid/v1')
at.form_submit_button[0].click().run()
assert not at.exception
assert at.session_state['result']['state']['status']=='evidence_only'
print('Interface checks passed: simplified controls, clarification, real retrieval, automatic AI routing, incomplete-connection fallback, credential exclusion.')

