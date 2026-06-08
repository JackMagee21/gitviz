# gitviz installer for Windows
# Run from the root of the cloned repository:
#   .\scripts\install.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "gitviz installer" -ForegroundColor Cyan
Write-Host "----------------" -ForegroundColor Cyan

# 1. Check Python is available
Write-Host ""
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Download it from https://python.org" -ForegroundColor Red
    Write-Host "During installation, make sure to tick 'Add Python to PATH'." -ForegroundColor Red
    exit 1
}

# 2. Install the package
Write-Host ""
Write-Host "Installing gitviz..." -ForegroundColor Yellow
python -m pip install . --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed." -ForegroundColor Red
    exit 1
}
Write-Host "Package installed." -ForegroundColor Green

# 3. Find the Scripts folder
Write-Host ""
Write-Host "Locating Scripts folder..." -ForegroundColor Yellow
$location = python -m pip show gitviz | Select-String "^Location:" | ForEach-Object { $_.ToString().Replace("Location: ", "").Trim() }
# Scripts sits one level up from site-packages
$scriptsPath = Join-Path (Split-Path $location -Parent) "Scripts"

if (-not (Test-Path $scriptsPath)) {
    Write-Host "WARNING: Could not find Scripts folder at: $scriptsPath" -ForegroundColor Yellow
    Write-Host "You may need to add it to PATH manually." -ForegroundColor Yellow
} else {
    Write-Host "Found: $scriptsPath" -ForegroundColor Green
}

# 4. Add to PATH if not already present
$currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($currentPath -like "*$scriptsPath*") {
    Write-Host "Scripts folder is already on PATH." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Adding Scripts folder to your PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable(
        "Path",
        $currentPath + ";" + $scriptsPath,
        [EnvironmentVariableTarget]::User
    )
    Write-Host "PATH updated." -ForegroundColor Green
}

# 5. Done
Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Open a new PowerShell window, then run:" -ForegroundColor Cyan
Write-Host "  gitviz --help" -ForegroundColor White
Write-Host ""