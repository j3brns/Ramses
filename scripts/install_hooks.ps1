$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
git -C $projectRoot config core.hooksPath .githooks
Write-Output 'Installed repository Git hooks.'
