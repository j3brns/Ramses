[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^[A-Za-z0-9._-]+$')]
  [string]$SshHost,

  [ValidatePattern('^/[A-Za-z0-9._/-]+$')]
  [string]$RemoteDirectory = '/home/hassio/.config/ramses-temporal-capture',

  [ValidatePattern('^/[A-Za-z0-9._/-]+$')]
  [string]$RemoteOptionsFile = '/home/hassio/.config/ramses-rx.conf',

  [ValidateRange(60, 86400)]
  [int]$DurationSeconds = 21600,

  [ValidateRange(1024, 16777216)]
  [int]$MaxBytes = 2097152,

  [switch]$ReplaceKnownRun,
  [switch]$Status
)

$ErrorActionPreference = 'Stop'

# All remote values are constrained above, then transported as base64. This keeps
# credentials out of this script and prevents local shell quoting from altering the
# receive-only runner.
$mode = if ($Status) { 'status' } elseif ($ReplaceKnownRun) { 'replace' } else { 'start' }
$remoteScript = @"
set -eu
directory='$RemoteDirectory'
options='$RemoteOptionsFile'
duration='$DurationSeconds'
limit='$MaxBytes'
mode='$mode'
runner="`$directory/kitchen-temporal-runner.sh"
pidfile="`$directory/kitchen-temporal-runner.pid"
output="`$directory/kitchen-rx.ndjson"
error="`$directory/kitchen-rx.err"

mkdir -p "`$directory"

known_runner() {
  pid="`$1"
  test -r "/proc/`$pid/cmdline" || return 1
  command=`$(tr '\000' ' ' < "/proc/`$pid/cmdline")
  case "`$command" in
    *"`$runner"*) return 0 ;;
    *) return 1 ;;
  esac
}

if test -f "`$pidfile"; then
  prior=`$(cat "`$pidfile" 2>/dev/null || true)
  case "`$prior" in ''|*[!0-9]*) echo "invalid capture pid file; refusing to change it" >&2; exit 2;; esac
  if kill -0 "`$prior" 2>/dev/null; then
    if ! known_runner "`$prior"; then
      echo "pid file belongs to an unexpected process; refusing to change it" >&2
      exit 2
    fi
    if test "`$mode" = status; then
      echo "active pid=`$prior output=`$output"
      exit 0
    fi
    if test "`$mode" != replace; then
      echo "known capture already active (pid=`$prior); use -ReplaceKnownRun to replace it" >&2
      exit 2
    fi
    pgid=`$(ps -o pgid= -p "`$prior" | tr -d ' ')
    if test "`$pgid" != "`$prior"; then
      echo "known runner is not an isolated process group; refusing to stop it" >&2
      exit 2
    fi
    kill -TERM -- "-`$prior"
    for attempt in 1 2 3 4 5; do
      kill -0 "`$prior" 2>/dev/null || break
      sleep 1
    done
    if kill -0 "`$prior" 2>/dev/null; then
      echo "known runner did not stop; refusing to start another" >&2
      exit 2
    fi
  fi
  rm -f "`$pidfile"
fi

if test "`$mode" = status; then
  echo "inactive output=`$output"
  exit 0
fi

cat > "`$runner" <<'RUNNER'
#!/bin/sh
set -u
directory='__DIRECTORY__'
options='__OPTIONS__'
duration='__DURATION__'
limit='__LIMIT__'
pidfile="`$directory/kitchen-temporal-runner.pid"
output="`$directory/kitchen-rx.ndjson"
temporary="`$directory/kitchen-rx.ndjson.tmp"
error="`$directory/kitchen-rx.err"
cleanup() { rm -f "`$pidfile"; exit 0; }
trap cleanup HUP INT TERM
rm -f "`$temporary"
timeout "`$duration" mosquitto_sub -o "`$options" -h 127.0.0.1 -p 1883 -t 'RAMSES/GATEWAY/+/rx' -R -F '%J' 2>"`$error" |
  awk -v limit="`$limit" 'BEGIN { bytes=0 } { size=length(`$0)+1; if (bytes + size > limit) exit; print; bytes += size }' >"`$temporary"
if test -s "`$temporary"; then mv -f "`$temporary" "`$output"; else rm -f "`$temporary"; fi
rm -f "`$pidfile"
RUNNER
sed -i "s|__DIRECTORY__|`$directory|g; s|__OPTIONS__|`$options|g; s|__DURATION__|`$duration|g; s|__LIMIT__|`$limit|g" "`$runner"
chmod 700 "`$runner"
nohup setsid sh "`$runner" >/dev/null 2>&1 &
pid=`$!
printf '%s\n' "`$pid" > "`$pidfile"
sleep 1
if ! kill -0 "`$pid" 2>/dev/null || ! known_runner "`$pid"; then
  rm -f "`$pidfile"
  echo "capture runner failed to start" >&2
  exit 2
fi
echo "started pid=`$pid output=`$output duration_seconds=`$duration max_bytes=`$limit"
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($remoteScript))
$response = & ssh $SshHost "printf '%s' '$encoded' | base64 -d | sh"
if ($LASTEXITCODE -ne 0) {
  throw "Temporal capture launcher failed with exit code $LASTEXITCODE"
}
$response
