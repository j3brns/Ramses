# Observed derived data

`topology.json` is generated from the live `ramses_cc` packet cache by the sanitising collector. It keeps only last-three-digit device labels, controller/zone membership, and TRV groupings.

Refresh locally with a pipeline that does not save the raw export:

```powershell
ssh ha "sudo -n cat /homeassistant/.storage/ramses_cc" |
  py scripts/refresh_observations.py --input -
```

Review the resulting diff, run `scripts/check.ps1`, then commit it with any corresponding target-system and documentation update.
