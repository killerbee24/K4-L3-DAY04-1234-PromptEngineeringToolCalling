from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


MAINTENANCE_FILE = ROOT / "helpdesk_data" / "maintenance_windows.json"
VALID_SERVICES = {"vpn", "email", "sso", "wifi", "printing"}
VALID_ENVIRONMENTS = {"production", "staging"}


def check_maintenance_window(service: str = "", environment: str = "") -> dict[str, Any]:
    tool = "check_maintenance_window"
    if not isinstance(service, str) or not isinstance(environment, str):
        return {"tool": tool, "error": "invalid_input_type"}
    wanted_service = service.strip().lower()
    wanted_environment = environment.strip().lower()
    if wanted_service not in VALID_SERVICES:
        return {"tool": tool, "service": wanted_service, "error": "invalid_service"}
    if wanted_environment not in VALID_ENVIRONMENTS:
        return {"tool": tool, "environment": wanted_environment, "error": "invalid_environment"}

    try:
        data = json.loads(MAINTENANCE_FILE.read_text(encoding="utf-8"))
        windows = [
            item
            for item in data["windows"]
            if item["service"] == wanted_service and item["environment"] == wanted_environment
        ]
        return {
            "tool": tool,
            "service": wanted_service,
            "environment": wanted_environment,
            "status": "planned" if windows else "no_planned_window",
            "windows": windows,
            "snapshot_at": data["snapshot_at"],
            "timezone": data["timezone"],
            "source": "mock_maintenance_calendar",
        }
    except Exception as exc:
        return err(tool, exc)
