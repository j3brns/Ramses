param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

$projectRoot = Split-Path -Parent $PSScriptRoot
$binary = Join-Path $projectRoot '.tools\tacks-v0.2.4\tk.exe'
if (-not (Test-Path $binary)) {
  & (Join-Path $PSScriptRoot 'install_tk.ps1')
}
& $binary @Arguments
exit $LASTEXITCODE
