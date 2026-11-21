from pathlib import Path


CONTRACT = Path("docs/programmer-contract.md")


def test_programmer_contract_keeps_manual_evidence_separate_from_project_decisions() -> None:
    text = CONTRACT.read_text(encoding="utf-8")

    assert "## Evidence and implementation status" in text
    assert "## HA decisions still requiring implementation" in text
    assert "## Verification map" in text
    assert "source_checked: 2026-11-21" in text
    assert "Not implemented" in text


def test_programmer_contract_links_implemented_slices_to_evidence() -> None:
    text = CONTRACT.read_text(encoding="utf-8")

    assert "tests/test_timer.py" in text
    assert "tests/test_ha_schedule.py" in text
    assert "tests/test_ha_climate.py" in text
