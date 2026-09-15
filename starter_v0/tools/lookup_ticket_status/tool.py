from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


TICKET_STATUS_FILE = ROOT / "helpdesk_data" / "ticket_status.json"


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    tool = "lookup_ticket_status"
    if not isinstance(ticket_id, str):
        return {"tool": tool, "error": "invalid_ticket_id_type"}
    wanted_id = ticket_id.strip().upper()
    if not wanted_id:
        return {"tool": tool, "error": "missing_ticket_id"}

    try:
        data = json.loads(TICKET_STATUS_FILE.read_text(encoding="utf-8"))
        ticket = next((item for item in data["tickets"] if item["ticket_id"] == wanted_id), None)
        if ticket is None:
            return {"tool": tool, "ticket_id": wanted_id, "error": "ticket_not_found"}
        return {
            "tool": tool,
            "ticket": ticket,
            "snapshot_at": data["snapshot_at"],
            "source": "mock_ticket_status_store",
        }
    except Exception as exc:
        return err(tool, exc)
