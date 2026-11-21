"""Pure-Python descriptor for the future Home Assistant Test adapter.

This module deliberately does not import Home Assistant, an MQTT client, or an
RF gateway. A Home Assistant integration may consume this descriptor later;
unit tests and the digital twin can import it today.
"""

from __future__ import annotations

from dataclasses import dataclass

from ramses_twin.mqtt import topics


TEST_ENTITY_PREFIX = "ramses_test"


def _entity_fragment(value: str) -> str:
    fragment = value.strip().lower().replace("-", "_").replace(" ", "_")
    if not fragment or not all(character.isalnum() or character == "_" for character in fragment):
        raise ValueError("zone id must produce a safe Home Assistant entity fragment")
    return fragment


@dataclass(frozen=True)
class TestAdapterDescriptor:
    """Test-only names and transport settings for one future HA zone adapter."""

    gateway_id: str
    zone_id: str

    @property
    def climate_entity_id(self) -> str:
        return f"climate.{TEST_ENTITY_PREFIX}_{_entity_fragment(self.zone_id)}"

    @property
    def mqtt_topics(self) -> dict[str, str]:
        """Return only the already-validated test-world topics."""
        return topics(self.gateway_id)


__all__ = ["TEST_ENTITY_PREFIX", "TestAdapterDescriptor"]
