param()

$ErrorActionPreference = 'Stop'

function Write-Info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "[OK]   $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

function Test-PortListening {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $conn
}

function Start-DevTerminal {
    param(
        [string]$Name,
        [string]$WorkingDir,
        [string]$Command
    )

    Write-Info "Launching $Name in a new terminal..."
    Start-Process -FilePath "pwsh" -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$WorkingDir'; $Command"
    ) | Out-Null
}

function Ensure-SharedVenv {
    param(
        [string]$VenvDir
    )

    $venvPython = Join-Path $VenvDir "Scripts\python.exe"
    $venvCfg = Join-Path $VenvDir "pyvenv.cfg"
    $needsRecreate = $false

    if (-not (Test-Path $venvPython) -or -not (Test-Path $venvCfg)) {
        $needsRecreate = $true
    } else {
        & $venvPython -c "import sys" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $needsRecreate = $true
        }
    }

    if ($needsRecreate) {
        Write-Warn "Shared backend venv is missing or corrupted. Recreating '$VenvDir'..."
        if (Test-Path $VenvDir) {
            Remove-Item $VenvDir -Recurse -Force
        }

        $bootstrapPython = "python"
        if (-not (Get-Command $bootstrapPython -ErrorAction SilentlyContinue)) {
            throw "No system Python found to recreate virtual environment."
        }

        & $bootstrapPython -m venv $VenvDir | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to recreate virtual environment at '$VenvDir'"
        }

        & (Join-Path $VenvDir "Scripts\python.exe") -m pip install --upgrade pip | Out-Null
        Write-Ok "Shared backend venv recreated successfully."
    }

    return (Join-Path $VenvDir "Scripts\python.exe")
}

function Ensure-PythonModule {
    param(
        [string]$PythonExe,
        [string]$ModuleName,
        [string]$InstallSpec,
        [string]$ServiceName
    )

    & $PythonExe -c "import $ModuleName" 2>$null
    if ($LASTEXITCODE -eq 0) {
        return
    }

    Write-Warn "$ServiceName is missing Python module '$ModuleName'. Installing '$InstallSpec'..."
    & $PythonExe -m pip install $InstallSpec
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install package '$InstallSpec' for $ServiceName"
    }

    & $PythonExe -c "import $ModuleName" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "$ServiceName still cannot import module '$ModuleName' after dependency installation."
    }
    Write-Ok "$ServiceName dependencies are ready."
}

Write-Info "Starting CleanGrid development environment (fast mode)..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI not found. Please install Docker Desktop first."
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Info "Starting only Docker services needed for local dev: db + redis"
& docker compose up -d db redis
if ($LASTEXITCODE -ne 0) {
    throw "Failed to start Docker Compose services (db/redis)."
}

Write-Info "Stopping dockerized app services (backend, ai-service, frontend) for hybrid local mode"
& docker compose stop backend ai-service frontend | Out-Null

Write-Info "Current Docker service status:"
& docker compose ps

$backendDir = Join-Path $root "backend"
$aiDir = Join-Path $root "ai-service"
$frontendDir = Join-Path $root "frontend"

$sharedVenvDir = Join-Path $backendDir ".venv"
$sharedPython = Ensure-SharedVenv -VenvDir $sharedVenvDir

Ensure-PythonModule -PythonExe $sharedPython -ModuleName "fastapi" -InstallSpec "fastapi>=0.104.1" -ServiceName "Backend"
Ensure-PythonModule -PythonExe $sharedPython -ModuleName "uvicorn" -InstallSpec "uvicorn[standard]>=0.24.0" -ServiceName "Backend"
Ensure-PythonModule -PythonExe $sharedPython -ModuleName "sqlalchemy" -InstallSpec "sqlalchemy>=2.0.23" -ServiceName "Backend"
Ensure-PythonModule -PythonExe $sharedPython -ModuleName "asyncpg" -InstallSpec "asyncpg>=0.29.0" -ServiceName "Backend"
Ensure-PythonModule -PythonExe $sharedPython -ModuleName "structlog" -InstallSpec "structlog>=23.2.0" -ServiceName "Backend"
Ensure-PythonModule -PythonExe $sharedPython -ModuleName "PIL" -InstallSpec "pillow>=10.2.0" -ServiceName "AI Service"
Ensure-PythonModule -PythonExe $sharedPython -ModuleName "httpx" -InstallSpec "httpx>=0.25.2" -ServiceName "AI Service"

if (-not (Test-PortListening -Port 8000)) {
    Start-DevTerminal -Name "Backend" -WorkingDir $backendDir -Command "`$env:PYTHONPATH='.'; `$env:DATABASE_URL='postgresql+asyncpg://cleangrid:cleangrid@localhost:5433/cleangrid'; `$env:REDIS_URL='redis://localhost:6380/0'; & '$sharedPython' -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
} else {
    Write-Warn "Port 8000 already in use. Skipping backend launch."
}

if (-not (Test-PortListening -Port 8001)) {
    Start-DevTerminal -Name "AI Service" -WorkingDir $aiDir -Command "`$env:PYTHONPATH='.'; & '$sharedPython' -m app.main"
} else {
    Write-Warn "Port 8001 already in use. Skipping AI service launch."
}

if (-not (Test-PortListening -Port 3000)) {
    Start-DevTerminal -Name "Frontend" -WorkingDir $frontendDir -Command "npm run dev"
} else {
    Write-Warn "Port 3000 already in use. Skipping frontend launch."
}

Write-Ok "Startup sequence completed."
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "- Docker: db, redis" -ForegroundColor White
Write-Host "- Local terminals: backend (8000), ai-service (8001), frontend (3000)" -ForegroundColor White
