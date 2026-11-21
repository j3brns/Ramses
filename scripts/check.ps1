$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $projectRoot
try {
  $env:PYTHONPATH = Join-Path $projectRoot 'src'
  py scripts/secret_scan.py
  py -m compileall -q src
  py -m pytest -m "not integration"
  py -m pytest -m integration
}
finally {
  Pop-Location
}
