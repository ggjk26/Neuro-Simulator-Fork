from neuro_simulator.neuro_sama.neuro_sdk_adapter import (
    NeuroSdkSession,
    _extract_json_object,
    _fallback_action,
    _normalize_action_data,
)


def test_extract_json_object_from_wrapped_text():
    assert _extract_json_object('choice: {"name":"jump","data":{"height":2}}') == {
        "name": "jump",
        "data": {"height": 2},
    }


def test_normalize_action_data_serializes_objects():
    assert _normalize_action_data({"direction": "left"}) == '{"direction":"left"}'
    assert _normalize_action_data('{"already":"json"}') == '{"already":"json"}'
    assert _normalize_action_data(None) is None


def test_fallback_action_prefers_allowed_registered_action():
    session = NeuroSdkSession()
    session.register_actions([
        {"name": "first", "description": "First action"},
        {"name": "second", "description": "Second action"},
    ])

    assert _fallback_action(session, ["second"])["name"] == "second"
