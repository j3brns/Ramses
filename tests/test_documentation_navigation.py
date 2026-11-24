from pathlib import Path


def test_readme_routes_agents_and_household_users_to_canonical_documents() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for required in (
        "docs/programmer-contract.md",
        "docs/hardware-foundation.md",
        "docs/ingest-contract.md",
        "docs/scenario-recording.md",
        "docs/scenario-qualification.md",
        "docs/lovelace-ui-contract.md",
        "docs/test-view-computer-use-runbook.md",
        "docs/user-guide.md",
        "The isolated transport core is complete",
        "the dashboard is not deployed",
        "## Logical household system",
        "Sonoff Zigbee radio",
        "The Home Assistant mobile app provides household access and identity.",
        "This project is a digital twin above the RAMSES-II data-link layer.",
    ):
        assert required in readme


def test_docs_map_preserves_agent_and_household_test_view_paths() -> None:
    docs_map = Path("docs/README.md").read_text(encoding="utf-8")

    for required in (
        "Agent onboarding",
        "Household/Test View path",
        "../AGENTS.md",
        "user-guide.md",
        "lovelace-ui-contract.md",
        "test-view-computer-use-runbook.md",
        "scenario-qualification.md",
    ):
        assert required in docs_map


def test_user_guide_identifies_its_test_only_help_and_deployment_boundary() -> None:
    guide = Path("docs/user-guide.md").read_text(encoding="utf-8")

    assert "canonical" in guide
    assert "test-view-computer-use-runbook.md" in guide
    assert "Ramses Test → Programmer" in guide
    assert "changes only the simulated programme" in guide
