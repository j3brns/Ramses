# Hardware foundation

## Role in the experiment

The physical observation and MQTT boundary is an **Elecram Sub‑GHz 855–925 MHz Bridge – ESP32‑C6 WiFi/Zigbee** board running [`ramses_esp`](https://github.com/IMMRMKW/ramses_esp). It receives RAMSES-II radio traffic and makes decoded gateway traffic available to Home Assistant/MQTT. The digital twin does not emulate, replace, reflash or transmit through this board.

## Attribution and reference material

- Hardware: [Elecram](https://elecram.com/) — [exact board product page](https://elecram.com/products/esp32-c6-wifi-zigbee-to-855-925mhz-wireless?variant=52605637099853).
- Producer: [Marcel / Elecram about page](https://elecram.com/pages/about).
- Gateway firmware: [IMMRMKW/ramses_esp](https://github.com/IMMRMKW/ramses_esp).
- Protocol/Home Assistant library: [ramses-rf/ramses_cc](https://github.com/ramses-rf/ramses_cc).

This attribution identifies the upstream hardware and software on which the experiment depends. It does not imply endorsement by Elecram, Marcel, IMMRMKW, or the RAMSES RF project.

## Connection boundary

```text
RAMSES-II RF
     |
     v
Elecram Sub-GHz Bridge + ramses_esp
     |
     v
MQTT broker
  |          |
  v          v
Home Assistant  passive collection -> bounded fixtures -> digital twin
```

The live gateway root and credentials are private. Simulator code and fixtures must use only `RAMSES/TEST/...`; see the [test transport contract](contract.md). The gateway serial port is a diagnostic interface, not a required component of the Wi-Fi/MQTT deployment.

## Non-negotiable handling rules

- Do not commit Wi-Fi, MQTT, Home Assistant, serial, gateway or device credentials.
- Do not enable RF transmission, change device bindings, reflash the board, or change its live configuration under this project.
- Do not treat a test MQTT publisher as permission to publish to the board’s live topic root.
- Keep raw packet fixtures bounded and sanitised according to the [ingest contract](ingest-contract.md).
