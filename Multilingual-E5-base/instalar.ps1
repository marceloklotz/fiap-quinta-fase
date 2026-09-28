$ErrorActionPreference = "Stop"

Write-Host "==============================================="
Write-Host "Instalação - Guardiã AI / Etapa 3.1 local"
Write-Host "==============================================="

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python não encontrado. Instale Python 3.11 ou 3.12 e tente novamente."
    exit 1
}

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "Arquivo .env criado a partir de .env.example."
    Write-Host "Edite o .env antes da primeira execução."
}

Write-Host ""
Write-Host "Instalação concluída."
Write-Host "Para executar:"
Write-Host "  .\.venv\Scripts\python.exe .\etapa3_1_local.py"
