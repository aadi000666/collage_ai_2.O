Write-Host "=== College AI Assistant Setup ===" -ForegroundColor Cyan

Write-Host "`nCreating virtual environment (.venv)..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment created!" -ForegroundColor Green

Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "`nCreating .env file..." -ForegroundColor Yellow
    "GEMINI_API_KEY=your_gemini_api_key_here" | Set-Content ".env"
    Write-Host ".env file created!" -ForegroundColor Green
    Write-Host "IMPORTANT: Edit .env and add your real GEMINI_API_KEY" -ForegroundColor Red
    Write-Host "Get your API key from: https://aistudio.google.com/app/apikey" -ForegroundColor Cyan
} else {
    Write-Host ".env file already exists." -ForegroundColor Green
}

New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "uploads" | Out-Null

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env and add your GEMINI_API_KEY"
Write-Host "  2. Run: .\.venv\Scripts\Activate.ps1"
Write-Host "  3. Run: python main.py"
