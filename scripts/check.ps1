$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $projectRoot
try {
  $env:PYTHONPATH = Join-Path $projectRoot 'src'
  py scripts/secret_scan.py
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  py scripts/check_adversarial_review.py --working
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  py -m compileall -q src
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  py -m pytest -m "not integration"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  py -m pytest -m integration
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
  Pop-Location
}
