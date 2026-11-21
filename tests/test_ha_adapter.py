import importlib
import sys

import pytest


def test_ha_adapter_imports_without_home_assistant_runtime() -> None:
    sys.modules.pop("homeassistant", None)
    adapter = importlib.import_module("ramses_twin.ha_adapter")

    assert "homeassistant" not in sys.modules
    descriptor = adapter.TestAdapterDescriptor("18:990001", "Kitchen")
    assert descriptor.climate_entity_id == "climate.ramses_test_kitchen"
    assert descriptor.mqtt_topics == {
        "rx": "RAMSES/TEST/18:990001/rx",
        "tx": "RAMSES/TEST/18:990001/tx",
    }


def test_ha_adapter_rejects_unsafe_entity_fragments_and_live_roots() -> None:
    adapter = importlib.import_module("ramses_twin.ha_adapter")

    with pytest.raises(ValueError):
        _ = adapter.TestAdapterDescriptor("18:990001", "Kitchen/Live").climate_entity_id
    with pytest.raises(ValueError):
        _ = adapter.TestAdapterDescriptor("18:990001/../GATEWAY", "Kitchen").mqtt_topics
