[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^[A-Za-z0-9._-]+$')]
  [string]$SshHost,

  [Parameter(Mandatory = $true)]
  [ValidateNotNullOrEmpty()]
  [string]$Destination,

  [ValidatePattern('^/[A-Za-z0-9._/-]+$')]
  [string]$RemotePath = '/home/hassio/kitchen_schedule_watch.ndjson',

  [ValidateRange(1, 16777216)]
  [int]$MaxBytes = 2097152,

  [switch]$Force,

  # Test-only transport seam: an ASCII base64 file produced by the remote command.
  [string]$Base64Input
)

$ErrorActionPreference = 'Stop'

if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
  throw "Destination exists; use -Force to replace it: $Destination"
}

if ($Base64Input) {
  $encoded = [System.IO.File]::ReadAllText($Base64Input, [System.Text.Encoding]::ASCII)
}
else {
  # Base64 is ASCII. Keeping it in a PowerShell string is safe; never redirect the
  # NDJSON itself because Windows PowerShell redirection writes UTF-16 by default.
  $encoded = (& ssh $SshHost "base64 -w 0 -- $RemotePath") -join ''
  if ($LASTEXITCODE -ne 0) {
    throw "SSH/base64 fetch failed with exit code $LASTEXITCODE"
  }
}

try {
  [byte[]]$bytes = [Convert]::FromBase64String($encoded)
}
catch {
  throw "Capture transport was not valid base64: $($_.Exception.Message)"
}

if ($bytes.Length -gt $MaxBytes) {
  throw "Capture is $($bytes.Length) bytes, above the $MaxBytes byte limit"
}

$parent = Split-Path -Parent $Destination
if (-not $parent -or -not (Test-Path -LiteralPath $parent -PathType Container)) {
  throw "Destination directory does not exist: $parent"
}

# This is a byte-for-byte write, not a text write. It preserves NDJSON for the
# Python selector and prevents PowerShell's UTF-16 output encoding from leaking in.
[System.IO.File]::WriteAllBytes($Destination, $bytes)
Write-Output ("{0} bytes written to {1}" -f $bytes.Length, $Destination)
