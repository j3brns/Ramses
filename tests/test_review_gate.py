import runpy


gate = runpy.run_path("scripts/check_adversarial_review.py")


def test_review_gate_requires_a_review_for_model_changes() -> None:
    assert gate["requires_review"](["src/ramses_twin/model.py"])
    assert gate["review_errors"]({})


def test_review_gate_excludes_documentation_only_changes() -> None:
    assert not gate["requires_review"](["docs/guide.md"])


def test_review_gate_accepts_a_complete_review() -> None:
    review = "\n".join(
        ("# Adversarial review", "## Scope", "## Failure modes", "## Evidence and tests", "## Decision", "## Rollback")
    )
    assert gate["review_errors"]({"docs/reviews/example.md": review}) == []
