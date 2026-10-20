$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    py -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or newer is required. Install Python and run setup.ps1 again.' }
}
& .venv/Scripts/python.exe -m pip install -r requirements-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Host 'Setup complete. Run ./start.ps1. First retrieval downloads public embedding and reranking models.'
