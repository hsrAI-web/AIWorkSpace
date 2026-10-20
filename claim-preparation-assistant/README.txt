HEALTH CLAIM PREPARATION ASSISTANT
Gen Academy Week 2 — educational RAG prototype

START
1. Install Python 3.11 or newer on Windows.
2. In PowerShell, open the extracted project directory and run ./setup.ps1.
3. Run ./start.ps1 and open http://127.0.0.1:8511.
4. Enter a question and optional document names, then click Ask assistant.
5. Open AI connection in the sidebar to enter your own Nebius settings.
   With a complete configuration the app adds a cited draft automatically;
   otherwise the checklist and source passages work without generation.
   Tested endpoint: https://api.tokenfactory.nebius.com/v1/
   Tested model: Qwen/Qwen3-30B-A3B-Instruct-2507

The first retrieval downloads public embedding and reranking models and may
take several minutes. Later runs reuse models/ and data/vectors-*.npz.
Internet access is required for the initial downloads and generated answers.
The prepared corpus and chunk files are included; rebuilding is optional.

REBUILD THE CORPUS
Use the project .venv/Scripts/python.exe to run these files in order:
prepare_sources.py, build_chunks.py, build_semantic_chunks.py.
Then run evaluate_retrieval.py and write_reports.py to refresh comparison reports.
Before refreshing, verify source versions using SOURCES.txt and manifest.json.
The pipeline reads the local PDFs; it does not automatically download updates.

VERIFY
./.venv/Scripts/python.exe -m unittest discover -p 'test_*.py'
This includes 26 unit tests and interface checks with real local retrieval.
Run the separate 15-question live evaluation in the app only when you want
paid provider calls. It allows one structural correction per answer, then
checks citations, quotes, observed logic errors and model-grounded support.
An interrupted evaluation resumes compatible saved progress.

FILES
PROJECT-REPORT.docx: project overview, decisions, comparisons and limitations.
PROMPTS.txt: complete generation and grounding instructions.
data/live-evaluation.json: final full live test evidence and timing.
SOURCE-REVIEW.txt: assistant review of the final answers against retrieved text.
data/retrieval-evaluation.json: four strategies by four retrieval modes.
sources/: original official PDFs. data/manifest.json contains their hashes.
test_*.py: regression and interface checks.

SCOPE AND LIMITS
Fictional examples for HDFC ERGO my:Optima Secure, UIN HDFHLIP25041V062425.
The corpus contains the complete two-page manual and reviewed form passages.
It does not include every table or form field. An actual issued policy may differ.
The app organises submission paperwork; it does not determine coverage, payout,
approval or live status. Reported document names do not verify possession.
Automated grounding and assistant review are not independent human evaluation.
Use the report's observed outcomes, not an assumed 95% accuracy claim.

DATA AND CREDENTIALS
Use fictional examples. Do not enter account numbers, IDs or medical records.
Provider settings remain in local Streamlit memory. The key is not exported.
Provider generation transmits the question, document names and public evidence.
No credentials, virtual environment or downloaded model weights are in the ZIP.
No deployment, public sharing or real insurance submission is performed.

REPRODUCIBILITY
requirements-lock.txt records the tested environment. First model downloads
depend on upstream hosting; model IDs and API availability can change.
Historical runs are retained to explain failures and iterations. Treat the final
report as a dated snapshot, not a guarantee that stochastic outputs will repeat.
Official source documents belong to their respective owner; this project is
not affiliated with or endorsed by the insurer.
