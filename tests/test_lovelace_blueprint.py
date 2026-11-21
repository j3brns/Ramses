"""Static contract tests for the un-deployed Ramses Test Lovelace blueprint."""

from pathlib import Path
import re


BLUEPRINT = Path("target-system/ramses-test-dashboard.yaml")


def test_test_view_blueprint_uses_native_sections_and_required_cards() -> None:
    blueprint = BLUEPRINT.read_text(encoding="utf-8")

    for required in (
        "type: sections",
        "type: thermostat",
        "type: entities",
        "type: tile",
        "type: markdown",
        "path: help",
        "subview: true",
        "back_path: /ramses-test",
        "navigation_path: /ramses-test/help",
        "Weekly programme",
        "Next change",
        "Temporary override ends",
    ):
        assert required in blueprint


def test_test_view_blueprint_has_only_test_entities_and_no_live_transport() -> None:
    blueprint = BLUEPRINT.read_text(encoding="utf-8")
    entity_ids = re.findall(
        r"^\s*-?\s*entity:\s*([a-z_]+\.[a-z0-9_]+)\s*$",
        blueprint,
        flags=re.MULTILINE,
    )

    assert entity_ids
    assert all(".ramses_test_" in entity_id for entity_id in entity_ids)
    assert "RAMSES/GATEWAY" not in blueprint
    assert "RAMSES/TEST/..." in blueprint
