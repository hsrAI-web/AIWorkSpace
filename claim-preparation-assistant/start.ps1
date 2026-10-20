$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:HF_HOME = Join-Path $PSScriptRoot 'models/hf'
& (Join-Path $PSScriptRoot '.venv/Scripts/python.exe') -m streamlit run app.py --server.address 127.0.0.1 --server.port 8511 --server.headless true --browser.gatherUsageStats false
