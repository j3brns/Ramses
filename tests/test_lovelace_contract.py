from pathlib import Path


def test_lovelace_contract_keeps_test_boundary_and_acceptance_matrix() -> None:
    contract = Path("docs/lovelace-ui-contract.md").read_text(encoding="utf-8")

    for required in (
        "Ramses Test",
        "RAMSES/TEST/...",
        "Sunnydays",
        "user-guide.md",
        "UI-01",
        "UI-07",
        "UI-08",
        "desktop",
        "mobile",
        "Return to schedule",
        "test-view-computer-use-runbook.md",
    ):
        assert required in contract


def test_user_guide_remains_the_canonical_help_source() -> None:
    guide = Path("docs/user-guide.md").read_text(encoding="utf-8")
    contract = Path("docs/lovelace-ui-contract.md").read_text(encoding="utf-8")

    assert "source_contract: programmer-contract.md" in guide
    assert "canonical_help: user-guide.md" in contract
    assert "`docs/user-guide.md` is canonical" in contract


def test_computer_use_runbook_is_deployment_gated_and_evidence_calibrated() -> None:
    runbook = Path("docs/test-view-computer-use-runbook.md").read_text(encoding="utf-8")

    for required in (
        "Ramses Test-only",
        "RAMSES/TEST/...",
        "RAMSES/GATEWAY/...",
        "1280 × 800",
        "390 × 844",
        "Baseline",
        "Candidate",
        "Qualified",
        "broker receipt time",
        "1970 epoch",
        "Baseline traffic",
        "Kitchen schedule change",
        "Local override expiry",
        "Restart or reconnect",
        "not run",
    ):
        assert required in runbook

    assert "does not authorise importing the blueprint" in runbook
    assert "Do not set a target" in runbook
