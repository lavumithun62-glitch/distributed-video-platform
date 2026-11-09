
$project = "C:\Projects\distributed-video-platform"
$python = Join-Path $project ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Python virtual environment not found!" -ForegroundColor Red
    exit 1
}

$services = @(
    @{
        Name = "Upload Service"
        Module = "backend.upload_service.app.main:app"
        Port = 8001
    },
    @{
        Name = "Metadata Service"
        Module = "backend.metadata_service.app.main:app"
        Port = 8002
    },
    @{
        Name = "Orchestrator Service"
        Module = "backend.orchestrator_service.app.main:app"
        Port = 8003
    },
    @{
        Name = "Thumbnail Service"
        Module = "backend.thumbnail_service.app.main:app"
        Port = 8004
    },
    @{
        Name = "Delivery Service"
        Module = "backend.delivery_service.app.main:app"
        Port = 8005
    }
)

Write-Host "Starting Distributed Video Processing Platform..." -ForegroundColor Green

foreach ($service in $services) {
    $module = $service.Module
    $port = $service.Port
    $name = $service.Name

    $command = "& '$python' -m uvicorn $module --host 127.0.0.1 --port $port"

    Start-Process powershell.exe `
        -WorkingDirectory $project `
        -ArgumentList @("-NoExit", "-Command", $command)

    Write-Host "$name launched on port $port" -ForegroundColor Cyan
    Start-Sleep -Seconds 2
}

$gatewayCommand = "& '$python' -m uvicorn backend.gateway.app.main:app --host 127.0.0.1 --port 8000"

Start-Process powershell.exe `
    -WorkingDirectory $project `
    -ArgumentList @("-NoExit", "-Command", $gatewayCommand)

Write-Host "Gateway launched on port 8000" -ForegroundColor Green
Write-Host "Wait 15 seconds, then open http://127.0.0.1:8000/docs" -ForegroundColor Yellow
