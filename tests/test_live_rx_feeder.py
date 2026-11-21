import importlib.util
import io
from pathlib import Path

import pytest


def _load_feeder():
    path = Path("scripts/feed_live_rx.py")
    spec = importlib.util.spec_from_file_location("feed_live_rx", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_feeder_preserves_order_and_caps_passive_rx_events() -> None:
    feeder = _load_feeder()
    source = io.StringIO(
        '\n'.join(
            [
                '{"topic":"RAMSES/GATEWAY/18:016440/rx","payload":{"msg":"first","ts":"2026-11-21T07:00:00+00:00"}}',
                '{"topic":"RAMSES/GATEWAY/18:016440/rx","payload":{"msg":"second","ts":"2026-11-21T07:00:01+00:00"}}',
                '{"topic":"RAMSES/GATEWAY/18:016440/rx","payload":{"msg":"third","ts":"2026-11-21T07:00:02+00:00"}}',
            ]
        )
    )

    events, discarded = feeder.feed(source, "RAMSES/GATEWAY", 2)

    assert [event["msg"] for event in events] == ["first", "second"]
    assert discarded == 1
    output = io.StringIO()
    feeder.write_ndjson(events, output)
    assert output.getvalue().count("\n") == 2
    assert '"topic":"RAMSES/GATEWAY/18:016440/rx"' in output.getvalue()


@pytest.mark.parametrize(
    "line",
    [
        '{"topic":"RAMSES/GATEWAY/18:016440/tx","payload":{"msg":"no","ts":"2026-11-21T07:00:00+00:00"}}',
        '{"topic":"RAMSES/TEST/18:990001/rx","payload":{"msg":"no","ts":"2026-11-21T07:00:00+00:00"}}',
        '{"topic":"RAMSES/GATEWAY/18:016440/rx","payload":{"msg":"","ts":"2026-11-21T07:00:00+00:00"}}',
    ],
)
def test_feeder_rejects_non_passive_or_invalid_input(line: str) -> None:
    feeder = _load_feeder()

    with pytest.raises(ValueError):
        feeder.feed(io.StringIO(line), "RAMSES/GATEWAY", 500)
