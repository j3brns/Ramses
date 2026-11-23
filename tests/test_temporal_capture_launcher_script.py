from pathlib import Path


SCRIPT = Path("scripts/start_temporal_rx_capture.ps1")


def test_launcher_is_bounded_and_receive_only() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "timeout" in text
    assert "awk -v limit" in text
    assert "RAMSES/GATEWAY/+/rx" in text
    assert "mosquitto_sub" in text
    assert "mosquitto_pub" not in text
    assert "RAMSES/TEST" not in text


def test_launcher_has_known_runner_recovery_guard() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "setsid sh" in text
    assert "known_runner" in text
    assert "ReplaceKnownRun" in text
    assert "refusing to change it" in text
    assert 'kill -TERM -- "-`$prior"' in text


def test_launcher_does_not_embed_credentials() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "ramses-rx.conf" in text
    assert "password" not in text.lower()
    assert "mosquitto_sub -o" in text
