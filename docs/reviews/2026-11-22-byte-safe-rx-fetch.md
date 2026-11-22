# Adversarial review: byte-safe passive RX fetch

## Scope

Add a local Windows PowerShell helper that copies an already completed,
bounded passive RX NDJSON capture from Home Assistant without changing its
bytes.

## Failure modes

- PowerShell text redirection can encode NDJSON as UTF-16 and leave the Python
  selector unable to parse it.
- SSH failure or non-base64 output could be written as if it were evidence.
- A malformed or unexpectedly large remote file could consume local storage or
  replace a useful local capture.
- A fetch helper could accidentally acquire MQTT credentials or a publish path.

## Evidence and tests

The helper transports only ASCII base64, rejects failed SSH and invalid base64,
enforces a two-megabyte default byte cap, and writes with `WriteAllBytes`.
Static tests reject PowerShell text writers and require the binary transport and
limit. A live validation fetched a completed 118650-byte passive window and
the Kitchen selector read it successfully; the selector found no candidate.

## Decision

Use the helper only after the separate bounded receive-only subscriber has
completed a capture. Keep its destination outside the repository until normal
scenario review and qualification decide that a fixture should be retained.
The helper has no MQTT client, credentials, broker mutation, RF path, or Home
Assistant write operation.

## Rollback

Remove the helper, its documentation, test and this review. Existing captures
and all live Home Assistant, MQTT, RF and heating state remain unchanged.
