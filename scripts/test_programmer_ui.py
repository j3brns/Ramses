"""Render native HA helper definitions and a Lovelace view for Ramses Test."""

from __future__ import annotations

import json

ROOMS = {"kitchen": "Kitchen", "ejmb_rdgb": "EJMB + RDGB", "lounge": "Lounge",
         "cmq_jgb": "CMQ JGB"}
WEEK = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def build():
    schedules, expiries, scripts, sections = {}, {}, {}, []
    for slug, label in ROOMS.items():
        prefix = f"ramses_test_{slug}"
        programme = f"{prefix}_test_timetable"
        expires = f"{prefix}_boost_expiry"
        schedule = f"schedule.{programme}"
        expiry = f"input_number.{expires}"
        schedules[programme] = {"name": programme.replace("_", " ").title(),
                                **{d: [{"from": "07:00:00", "to": "22:00:00",
                                        "data": {"target_temperature": 20}}] for d in WEEK}}
        # Persist the absolute deadline across restarts and ambiguous local times.
        expiries[expires] = {"name": expires.replace("_", " ").title(), "mode": "box",
                             "min": 0, "max": 4102444800, "step": 1}
        next_event = "as_timestamp(state_attr('" + schedule + "', 'next_event'), 0)"
        button_cards = []
        for action, title, icon in [("boost", "Boost to 22°C", "mdi:fire"),
                                    ("cancel", "Return to schedule", "mdi:calendar-clock")]:
            script = f"{prefix}_{action}"
            steps = []
            if action == "boost":
                steps.extend([{"variables": {"deadline": "{{ " + next_event + " }}"}},
                              {"condition": "template",
                               "value_template": "{{ deadline | float(0) > as_timestamp(now()) }}"}])
            steps.append({"action": "input_number.set_value", "target": {"entity_id": expiry},
                          "data": {"value": "{{ deadline }}" if action == "boost" else 0}})
            scripts[script] = {"alias": script.replace("_", " ").title(), "sequence": steps,
                               "mode": "single"}
            button_cards.append({"type": "button", "name": title, "icon": icon,
                                 "tap_action": {"action": "perform-action", "perform_action": "script." + script},
                                 "hold_action": {"action": "none"}})
        status = """
{% set expiry = states('EXPIRY') | float(0) %}
{% set target = state_attr('SCHEDULE', 'target_temperature') if is_state('SCHEDULE','on') else 16 %}
{% if not has_value('SCHEDULE') or not has_value('EXPIRY') %}Programme unavailable
{% elif expiry > as_timestamp(now()) %}**22°C** · Boost until {{ expiry | timestamp_custom('%a %H:%M') }}
{% else %}**{{ target }}°C** · Schedule{% endif %}

{% set next = state_attr('SCHEDULE','next_event') %}
{% if next %}Next switch {{ as_timestamp(next) | timestamp_custom('%a %H:%M') }}{% endif %}
""".strip().replace("EXPIRY", expiry).replace("SCHEDULE", schedule)
        sections.append({"type": "grid", "cards": [
            {"type": "heading", "heading": label},
            {"type": "markdown", "content": status},
            {"type": "horizontal-stack", "cards": button_cards},
            {"type": "tile", "entity": schedule, "name": "Weekly timetable"},
        ]})
    sections.insert(0, {"type": "grid", "cards": [{"type": "markdown",
        "content": "**Test programme** · Example timetable, daily 07:00–22:00 at 20°C; 16°C outside active blocks. Each boost lasts until that zone’s next switch."}]})
    return {"schedules": schedules, "expiries": expiries, "scripts": scripts,
            "view": {"type": "sections", "title": "Programmer", "path": "programmer",
                     "icon": "mdi:calendar-clock", "max_columns": 2, "sections": sections}}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
