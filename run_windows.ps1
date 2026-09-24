$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "============================================================"
Write-Host "  CyberSentinel EU v1.5.1 - Windows PowerShell Launcher"
Write-Host "============================================================"
Write-Host ""

$python = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $python = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $python = "python" }

if (-not $python) {
    Write-Host "[ERROR] Python was not found." -ForegroundColor Red
    Write-Host "Install Python 3.11 or 3.12 from python.org and enable Add Python to PATH."
    Read-Host "Press Enter to close"
    exit 1
}

& $python -c "import sys; print('Python', sys.version.split()[0]); raise SystemExit(0 if (3,11) <= sys.version_info[:2] <= (3,13) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Supported Python versions: 3.11, 3.12, 3.13." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $python -m venv .venv
}
$venvPy = ".venv\Scripts\python.exe"

& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt
& $venvPy -c "import fastapi, uvicorn, sqlalchemy, jinja2, psycopg; print('Dependency verification: OK')"

if (-not $env:CYBERSENTINEL_SESSION_SECRET) {
    $env:CYBERSENTINEL_SESSION_SECRET = "local-development-only-change-this-before-production"
}

Write-Host ""
Write-Host "Open http://127.0.0.1:8000"
Write-Host "Development login: admin / ChangeMe!2026"
Write-Host "Keep this window open while the server is running."
Write-Host ""

& $venvPy -m uvicorn app.main:app --host 127.0.0.1 --port 8000

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] CyberSentinel stopped unexpectedly." -ForegroundColor Red
    Read-Host "Press Enter to close"
}
