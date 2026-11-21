# Observed derived data

`topology.json`, `samples.json`, and `packets.json` are generated from the live `ramses_cc` packet cache. The first two are sanitised; `packets.json` is an intentionally retained, bounded raw RAMSES-II packet corpus. The full ingestion contract is in `docs/ingest-contract.md`.

Refresh locally with a pipeline that does not save the raw export:

```powershell
ssh ha "sudo -n cat /homeassistant/.storage/ramses_cc" |
  py scripts/refresh_observations.py --input -
```

Review the resulting diff, run `scripts/check.ps1`, then commit it with any corresponding target-system and documentation update.
