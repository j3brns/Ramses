[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]*$')]
    [string]$SshHost = 'ha',
    [ValidateRange(5, 21600)]
    [int]$DurationSeconds = 3600
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
$priorPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $root 'src'
    py -u scripts/follow_relay_shadow.py $SshHost $DurationSeconds
    exit $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $priorPath
    Pop-Location
}
