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
        "desktop",
        "mobile",
        "Return to schedule",
    ):
        assert required in contract


def test_user_guide_remains_the_canonical_help_source() -> None:
    guide = Path("docs/user-guide.md").read_text(encoding="utf-8")
    contract = Path("docs/lovelace-ui-contract.md").read_text(encoding="utf-8")

    assert "source_contract: programmer-contract.md" in guide
    assert "canonical_help: user-guide.md" in contract
    assert "`docs/user-guide.md` is canonical" in contract
