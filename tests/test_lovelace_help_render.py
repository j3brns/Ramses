from pathlib import Path
import subprocess
import sys

from scripts.render_lovelace_help import guide_body, render_region, replace_region


def test_help_region_is_derived_from_canonical_user_guide() -> None:
    guide = guide_body(Path("docs/user-guide.md").read_text(encoding="utf-8"))
    blueprint = Path("target-system/ramses-test-dashboard.yaml").read_text(encoding="utf-8")

    assert "# Ramses Test programmer guide" in guide
    assert render_region(guide) in blueprint
    assert "It does not control the live heating system." in blueprint


def test_help_renderer_check_mode_passes_for_committed_blueprint() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/render_lovelace_help.py", "--check"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "current" in result.stdout


def test_help_renderer_rejects_missing_or_duplicate_markers() -> None:
    region = render_region("# Guide")

    try:
        replace_region("no markers", region)
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("missing markers must fail")

    duplicate = f"{region}\n{region}"
    try:
        replace_region(duplicate, region)
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("duplicate markers must fail")
