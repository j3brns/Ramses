"""Small atomic state store for bounded test-world recovery state."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from ramses_twin.thermal import ThermalModel


@dataclass(frozen=True)
class SavedState:
    """The bounded state needed to restart a test-world runtime.

    Observations and broker traffic are deliberately excluded.  ``overrides``
    is a transport-neutral, JSON-safe mapping owned by ``TwinRuntime``.
    """

    models: dict[str, ThermalModel]
    overrides: dict[str, dict[str, object]]


class JsonStateStore:
    """Atomically persist learned coefficients and current zone overrides."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load_models(self) -> dict[str, ThermalModel]:
        return self.load().models

    def load(self) -> SavedState:
        if not self.path.exists():
            return SavedState({}, {})
        content: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        if content.get("format") == 1 and isinstance(content.get("zones"), dict):
            # v1 stored thermal coefficients only.  Retain this migration path
            # so an existing test runtime can restart without intervention.
            return SavedState(
                {zone_id: ThermalModel.from_state(model) for zone_id, model in content["zones"].items()},
                {},
            )
        if content.get("format") != 2 or not isinstance(content.get("models"), dict) or not isinstance(content.get("overrides"), dict):
            raise ValueError("invalid Ramses Twin state store")
        if any(not isinstance(value, dict) for value in content["overrides"].values()):
            raise ValueError("invalid Ramses Twin override state")
        return SavedState(
            {zone_id: ThermalModel.from_state(model) for zone_id, model in content["models"].items()},
            content["overrides"],
        )

    def save_models(self, models: dict[str, ThermalModel]) -> None:
        self.save(models, self.load().overrides)

    def save(self, models: dict[str, ThermalModel], overrides: dict[str, dict[str, object]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "format": 2,
            "models": {zone_id: model.to_state() for zone_id, model in sorted(models.items())},
            "overrides": {zone_id: overrides[zone_id] for zone_id in sorted(overrides)},
        }
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as temporary:
            temporary.write(json.dumps(document, indent=2) + "\n")
            temporary_path = Path(temporary.name)
        temporary_path.replace(self.path)
