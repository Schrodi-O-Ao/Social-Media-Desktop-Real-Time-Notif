param(
    [string]$ProjectPath = (Split-Path -Parent $PSScriptRoot)
)

$project = [System.IO.Path]::GetFullPath($ProjectPath)
$appFile = Join-Path $project "aoo.py"
$packageFile = Join-Path $project "aoo\app.py"
$channelsFile = Join-Path $project "channels.json"
$stateFile = Join-Path $project "last_seen.json"

if ((Test-Path -LiteralPath $appFile -PathType Leaf) -and (Test-Path -LiteralPath $packageFile -PathType Leaf)) {
    Write-Host "Aoo project: found at $project"
} else {
    Write-Host "Aoo project: not found at $project"
}

if ((Test-Path -LiteralPath $channelsFile -PathType Leaf) -or (Test-Path -LiteralPath $stateFile -PathType Leaf)) {
    Write-Host "Aoo saved data: found"
} else {
    Write-Host "Aoo saved data: not found"
}
