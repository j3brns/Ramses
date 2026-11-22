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
        "Evidence status",
        "Latest broker receipt time",
        "Gateway time valid for elapsed-time claims",
        "Bounded event count",
        "Baseline traffic",
        "Kitchen schedule change",
        "Local override expiry",
        "Restart or reconnect",
        "Qualified",
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


def test_evidence_status_is_test_only_and_does_not_claim_live_packet_access() -> None:
    blueprint = BLUEPRINT.read_text(encoding="utf-8")

    for entity_id in (
        "sensor.ramses_test_capture_receipt_time",
        "binary_sensor.ramses_test_capture_time_valid",
        "sensor.ramses_test_capture_event_count",
        "sensor.ramses_test_evidence_baseline",
        "sensor.ramses_test_evidence_kitchen_schedule",
        "sensor.ramses_test_evidence_local_override",
        "sensor.ramses_test_evidence_restart_reconnect",
    ):
        assert entity_id in blueprint

    # Generated Help may describe the safety boundary, but it must not offer
    # packet-console access as a dashboard capability.
    assert "never exposes a live packet stream" in blueprint.lower()
    assert "view live packet stream" not in blueprint.lower()
