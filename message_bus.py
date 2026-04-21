"""
message_bus.py
Shared in-memory message bus for LaunchMind agents.
All agents communicate exclusively through this module.
"""

import uuid
from datetime import datetime, timezone

# Central message store: { "agent_name": [list of message dicts] }
_bus: dict[str, list[dict]] = {}

# Full log of every message ever sent (for demo / evaluator inspection)
_log: list[dict] = []


def send_message(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: dict,
    parent_message_id: str = None,
) -> dict:
    """
    Send a structured message from one agent to another.

    message_type must be one of: task | result | revision_request | confirmation
    """
    assert message_type in (
        "task", "result", "revision_request", "confirmation"
    ), f"Invalid message_type: {message_type}"

    msg = {
        "message_id": str(uuid.uuid4()),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "message_type": message_type,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_message_id": parent_message_id,
    }

    _bus.setdefault(to_agent, []).append(msg)
    _log.append(msg)

    print(
        f"  [BUS] {from_agent} → {to_agent} "
        f"({message_type}) | id={msg['message_id'][:8]}"
    )
    return msg


def get_messages(agent_name: str) -> list[dict]:
    """Return all messages addressed to agent_name (oldest first)."""
    return list(_bus.get(agent_name, []))


def get_latest(agent_name: str) -> dict | None:
    """Return the most recent message for agent_name, or None."""
    msgs = _bus.get(agent_name, [])
    return msgs[-1] if msgs else None


def clear_inbox(agent_name: str) -> None:
    """Clear an agent's inbox after it has processed messages."""
    _bus[agent_name] = []


def print_full_log() -> None:
    """Print every message ever sent — for demo / evaluator."""
    print("\n" + "=" * 60)
    print("FULL MESSAGE LOG")
    print("=" * 60)
    for i, msg in enumerate(_log, 1):
        print(f"\n[{i}] {msg['timestamp']}")
        print(f"     {msg['from_agent']} → {msg['to_agent']} ({msg['message_type']})")
        print(f"     id={msg['message_id'][:8]}  parent={str(msg['parent_message_id'])[:8]}")
        print(f"     payload keys: {list(msg['payload'].keys())}")
    print("\n" + "=" * 60)
