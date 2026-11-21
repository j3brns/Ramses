"""Small atomic state store for learned per-zone thermal coefficients."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from ramses_twin.thermal import ThermalModel


class JsonStateStore:
    """Persist only learned model coefficients; observations remain bounded elsewhere."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load_models(self) -> dict[str, ThermalModel]:
        if not self.path.exists():
            return {}
        content: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        if content.get("format") != 1 or not isinstance(content.get("zones"), dict):
            raise ValueError("invalid Ramses Twin state store")
        return {zone_id: ThermalModel.from_state(model) for zone_id, model in content["zones"].items()}

    def save_models(self, models: dict[str, ThermalModel]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {"format": 1, "zones": {zone_id: model.to_state() for zone_id, model in sorted(models.items())}}
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as temporary:
            temporary.write(json.dumps(document, indent=2) + "\n")
            temporary_path = Path(temporary.name)
        temporary_path.replace(self.path)
