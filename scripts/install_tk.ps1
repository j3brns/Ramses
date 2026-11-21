$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolRoot = Join-Path $projectRoot '.tools\tacks-v0.2.4'
$archive = Join-Path $toolRoot 'tacks.zip'
$expectedHash = 'c205bb016ae8bf2af1dd029e7693a470f29db55507976214228568be43c7b2e8'
$download = 'https://github.com/srmccray/tacks/releases/download/v0.2.4/tacks-x86_64-pc-windows-msvc.zip'

if (Test-Path (Join-Path $toolRoot 'tk.exe')) {
  Write-Output 'tk 0.2.4 is already installed.'
  exit 0
}

New-Item -ItemType Directory -Force -Path $toolRoot | Out-Null
Invoke-WebRequest -Uri $download -OutFile $archive
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant() -ne $expectedHash) {
  throw 'Tacks archive checksum mismatch.'
}
Expand-Archive -LiteralPath $archive -DestinationPath $toolRoot -Force
Remove-Item -LiteralPath $archive
Write-Output 'Installed tk 0.2.4 project-locally.'
