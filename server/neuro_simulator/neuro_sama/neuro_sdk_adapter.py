"""Compatibility WebSocket adapter for the VedalAI Neuro SDK protocol.

The official API is a plaintext JSON WebSocket protocol where integrations send
commands such as ``startup``, ``context``, ``actions/register`` and
``actions/force``. This adapter lets those clients connect to this simulator as
if it were a Neuro API server.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect
from openai import AsyncOpenAI

from .config import Config


@dataclass
class NeuroSdkSession:
    """Per-connection state for a Neuro SDK client."""

    game: str = "Unknown Game"
    actions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    context_messages: List[str] = field(default_factory=list)
    pending_actions: Dict[str, str] = field(default_factory=dict)

    def register_actions(self, actions: List[Dict[str, Any]]) -> None:
        for action in actions:
            name = action.get("name")
            if isinstance(name, str) and name:
                self.actions[name] = action

    def unregister_actions(self, action_names: List[str]) -> None:
        for action_name in action_names:
            self.actions.pop(action_name, None)


def _safe_json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Extract the first JSON object from an LLM response."""
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or start >= end:
            return {}
        try:
            parsed = json.loads(text[start : end + 1])
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}


def _normalize_action_data(data: Any) -> Optional[str]:
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return _safe_json_dumps(data)


def _fallback_action(session: NeuroSdkSession, allowed_names: List[str]) -> Dict[str, Any]:
    available_names = [name for name in allowed_names if name in session.actions]
    if not available_names:
        available_names = list(session.actions.keys())
    if not available_names:
        return {"name": "", "data": None}
    return {"name": available_names[0], "data": None}


async def choose_action(
    client: AsyncOpenAI,
    config: Config,
    session: NeuroSdkSession,
    force_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Ask the configured LLM to choose an SDK action, with deterministic fallback."""
    allowed_names = force_data.get("action_names") or list(session.actions.keys())
    allowed_actions = [session.actions[name] for name in allowed_names if name in session.actions]
    if not allowed_actions:
        return _fallback_action(session, allowed_names)

    system_prompt = (
        "You are Neuro-sama controlling an external integration through the Neuro SDK. "
        "Choose exactly one available action. Return only a JSON object with keys "
        "name and data. The data value must be an object matching the action schema, "
        "or null when no parameters are needed."
    )
    user_prompt = {
        "game": session.game,
        "recent_context": session.context_messages[-12:],
        "state": force_data.get("state", ""),
        "query": force_data.get("query", "Choose an action."),
        "allowed_actions": allowed_actions,
    }

    try:
        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _safe_json_dumps(user_prompt)},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        selected = _extract_json_object(content)
        selected_name = selected.get("name")
        if selected_name in {action["name"] for action in allowed_actions}:
            return {"name": selected_name, "data": selected.get("data")}
    except Exception as exc:
        print(f"Neuro SDK action choice failed, using fallback: {exc}")

    return _fallback_action(session, allowed_names)


async def handle_neuro_sdk_websocket(websocket: WebSocket, client: AsyncOpenAI, config: Config) -> None:
    """Handle a VedalAI Neuro SDK compatible websocket connection."""
    session = NeuroSdkSession()
    await websocket.accept()

    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json({"command": "error", "data": {"message": "Invalid JSON message"}})
                continue

            command = message.get("command")
            game = message.get("game")
            data = message.get("data") or {}
            if isinstance(game, str) and game:
                session.game = game

            if command == "startup":
                session.actions.clear()
                session.context_messages.clear()
                session.pending_actions.clear()
                await websocket.send_json({
                    "command": "startup",
                    "data": {
                        "session": {
                            "sessionId": str(uuid.uuid4()),
                            "characterId": "neuro",
                            "displayName": "Neuro-sama",
                        }
                    },
                })
            elif command == "context":
                context_message = data.get("message")
                if isinstance(context_message, str) and context_message:
                    session.context_messages.append(context_message)
                    session.context_messages = session.context_messages[-50:]
            elif command == "actions/register":
                actions = data.get("actions", [])
                if isinstance(actions, list):
                    session.register_actions(actions)
            elif command == "actions/unregister":
                action_names = data.get("action_names", [])
                if isinstance(action_names, list):
                    session.unregister_actions(action_names)
            elif command == "actions/force":
                selected = await choose_action(client, config, session, data)
                selected_name = selected.get("name")
                if not selected_name:
                    await websocket.send_json({
                        "command": "error",
                        "data": {"message": "No registered actions are available for actions/force"},
                    })
                    continue

                action_id = str(uuid.uuid4())
                session.pending_actions[action_id] = selected_name
                action_payload: Dict[str, Any] = {"id": action_id, "name": selected_name}
                selected_data = _normalize_action_data(selected.get("data"))
                if selected_data is not None:
                    action_payload["data"] = selected_data
                await websocket.send_json({"command": "action", "data": action_payload})
            elif command == "action/result":
                action_id = data.get("id")
                if isinstance(action_id, str):
                    session.pending_actions.pop(action_id, None)
                result_message = data.get("message")
                if isinstance(result_message, str) and result_message:
                    session.context_messages.append(f"Action result: {result_message}")
                    session.context_messages = session.context_messages[-50:]
            else:
                await websocket.send_json({
                    "command": "error",
                    "data": {"message": f"Unsupported command: {command}"},
                })
    except WebSocketDisconnect:
        print("Neuro SDK websocket disconnected")
