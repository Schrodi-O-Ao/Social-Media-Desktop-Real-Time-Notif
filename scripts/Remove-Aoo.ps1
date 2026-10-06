param(
    [switch]$DataOnly,
    [string]$ProjectPath = (Split-Path -Parent $PSScriptRoot)
)

$project = [System.IO.Path]::GetFullPath($ProjectPath)
$appFile = Join-Path $project "aoo.py"
$packageFile = Join-Path $project "aoo\app.py"
$projectRoot = [System.IO.Path]::GetPathRoot($project)

if ($project -eq $projectRoot -or -not (Test-Path -LiteralPath $appFile -PathType Leaf) -or -not (Test-Path -LiteralPath $packageFile -PathType Leaf)) {
    throw "This does not look like an Aoo project folder. Nothing was removed."
}

$dataFiles = @(
    (Join-Path $project "channels.json"),
    (Join-Path $project "last_seen.json")
)

if ($DataOnly) {
    $answer = Read-Host "Remove Aoo's saved channels and history from '$project'? Type REMOVE to continue"
    if ($answer -ne "REMOVE") {
        Write-Host "Nothing was removed."
        exit 0
    }
    foreach ($file in $dataFiles) {
        if (Test-Path -LiteralPath $file -PathType Leaf) {
            Remove-Item -LiteralPath $file -Force
        }
    }
    Write-Host "Aoo's saved data was removed."
    exit 0
}

$answer = Read-Host "Remove the whole Aoo project at '$project'? Type REMOVE to continue"
if ($answer -ne "REMOVE") {
    Write-Host "Nothing was removed."
    exit 0
}

Write-Host "Close Aoo now. The project folder will be removed in a few seconds."
$command = "timeout /t 3 /nobreak >nul & rmdir /s /q `"$project`""
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $command -WindowStyle Hidden
