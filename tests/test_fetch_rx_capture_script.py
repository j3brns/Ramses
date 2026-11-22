from pathlib import Path


SCRIPT = Path("scripts/fetch_rx_capture.ps1")


def test_fetch_script_uses_ascii_transport_and_byte_write() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "base64 -w 0" in text
    assert "[Convert]::FromBase64String" in text
    assert "[System.IO.File]::WriteAllBytes" in text
    assert "MaxBytes" in text
    assert "[string]$SshHost" in text


def test_fetch_script_never_uses_powershell_text_redirection_for_capture() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for unsafe_text_writer in ("Out-File", "Set-Content", "Add-Content"):
        assert unsafe_text_writer not in text
