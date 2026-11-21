# Observed derived data

`topology.json` and `samples.json` are generated from the live `ramses_cc` packet cache by the sanitising collector. They keep only last-three-digit device labels and an allow-list of decoded values. The full ingestion contract is in `docs/ingest-contract.md`.

Refresh locally with a pipeline that does not save the raw export:

```powershell
ssh ha "sudo -n cat /homeassistant/.storage/ramses_cc" |
  py scripts/refresh_observations.py --input -
```

Review the resulting diff, run `scripts/check.ps1`, then commit it with any corresponding target-system and documentation update.
