param(
    [switch]$RemoveVolumes = $false,
    [switch]$Prune = $false
)

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

function Stop-ByPort {
    param(
        [int]$Port,
        [string]$Name
    )

    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    if (-not $listeners) {
        Write-Info "$Name is not running on port $Port"
        return
    }

    foreach ($procId in $listeners) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Ok "Stopped $Name (PID $procId) on port $Port"
        } catch {
            Write-Warn "Could not stop PID $procId on port ${Port}: $($_.Exception.Message)"
        }
    }
}

Write-Info "Stopping CleanGrid development services..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI not found. Please install Docker Desktop first."
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Stop-ByPort -Port 3000 -Name "Frontend"
Stop-ByPort -Port 8000 -Name "Backend"
Stop-ByPort -Port 8001 -Name "AI Service"

$downArgs = @('compose', 'down', '--remove-orphans')
if ($RemoveVolumes) {
    $downArgs += '-v'
}

Write-Info "Stopping docker services (db + redis)"
Write-Info "Running: docker $($downArgs -join ' ')"
& docker @downArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to stop Docker Compose services."
}

if ($Prune) {
    Write-Info "Pruning dangling Docker artifacts..."
    & docker system prune -f
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "docker system prune returned a non-zero exit code."
    }
}

Write-Ok "Development services stopped."
