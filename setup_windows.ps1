param(
    [string]$PythonVersion = "3.11"
)

$ErrorActionPreference = "Stop"

function Get-PythonLauncherVersionPath {
    param([string]$Version)
    try {
        $path = & py "-$Version" -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $path) {
            return $path.Trim()
        }
    } catch { return $null }
    return $null
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan

# ---------- Find Python ----------
$selectedPython = Get-PythonLauncherVersionPath -Version $PythonVersion
if (-not $selectedPython) {
    $selectedPython = Get-PythonLauncherVersionPath -Version "3.10"
}
if (-not $selectedPython) {
    Write-Host "Python 3.10 or 3.11 is required." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Using Python: $selectedPython" -ForegroundColor Green

# ---------- Verify requirements.txt ----------
$requirementsPath = Join-Path $projectRoot "requirements.txt"
if (-not (Test-Path $requirementsPath)) {
    Write-Host "requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# ---------- Create venv ----------
$venvPath = Join-Path $projectRoot ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    & $selectedPython -m venv $venvPath
}
$venvPython = Join-Path $venvPath "Scripts\python.exe"

# ---------- Upgrade pip ----------
Write-Host "Upgrading pip/setuptools/wheel..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade "pip" "setuptools<70.0.0" "wheel"

# ---------- Install deps ----------
Write-Host "Installing dependencies..." -ForegroundColor Cyan
try {
    & $venvPython -m pip install -r $requirementsPath
} catch {
    Write-Host "First install failed. Retrying..." -ForegroundColor Yellow
    & $venvPython -m pip install -r $requirementsPath
}

# ---------- Secrets template ----------
$secretsDir  = Join-Path $projectRoot ".streamlit"
$secretsPath = Join-Path $secretsDir  "secrets.toml"
if (-not (Test-Path $secretsDir))  { New-Item -ItemType Directory -Path $secretsDir | Out-Null }
if (-not (Test-Path $secretsPath)) {
    @"
# Fill in your Supabase credentials.
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR-ANON-KEY"
"@ | Set-Content -Path $secretsPath
    Write-Host "Created .streamlit/secrets.toml - fill in your Supabase keys." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "If dlib fails, install Visual Studio C++ Build Tools:" -ForegroundColor Yellow
Write-Host "  https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Run the app with:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe -m streamlit run app.py"
Write-Host ""

$runNow = Read-Host "Start the app now? (y/n)"
if ($runNow -eq "y") {
    & $venvPython -m streamlit run app.py
}
