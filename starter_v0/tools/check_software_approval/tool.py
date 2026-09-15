from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, fold_text


CATALOG_FILE = ROOT / "helpdesk_data" / "approved_software.json"


def check_software_approval(
    software_name: str = "",
    version: str = "",
    operating_system: str = "",
) -> dict[str, Any]:
    tool = "check_software_approval"
    if not all(isinstance(value, str) for value in (software_name, version, operating_system)):
        return {"tool": tool, "error": "invalid_input_type"}

    wanted_name = software_name.strip()
    wanted_version = version.strip()
    wanted_os = operating_system.strip()
    if not wanted_name:
        return {"tool": tool, "error": "missing_software_name"}
    if not wanted_version:
        return {"tool": tool, "error": "missing_version"}
    if not wanted_os:
        return {"tool": tool, "error": "missing_operating_system"}

    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        folded_name = fold_text(wanted_name)
        product = next(
            (
                item
                for item in data["products"]
                if folded_name in {fold_text(item["name"]), *(fold_text(alias) for alias in item.get("aliases", []))}
            ),
            None,
        )
        if product is None:
            return {
                "tool": tool,
                "status": "not_found",
                "error": "software_not_found",
                "software_name": wanted_name,
                "source": "mock_approved_software_catalog",
            }

        folded_os = fold_text(wanted_os)
        variant = next(
            (item for item in product["variants"] if fold_text(item["operating_system"]) == folded_os),
            None,
        )
        if variant is None:
            return {
                "tool": tool,
                "status": "not_approved",
                "error": "operating_system_not_supported",
                "matched_product": product["name"],
                "operating_system": wanted_os,
                "source": "mock_approved_software_catalog",
            }

        approved_versions = variant.get("approved_versions", [])
        upgrade_from = variant.get("upgrade_from", [])
        if wanted_version in approved_versions:
            status = "approved"
            recommendation = "No version change is required."
        elif wanted_version in upgrade_from:
            status = "upgrade_required"
            recommendation = variant["recommendation"]
        else:
            status = "not_approved"
            recommendation = "Use an approved version from the managed software catalog."

        return {
            "tool": tool,
            "status": status,
            "matched_product": product["name"],
            "requested_version": wanted_version,
            "approved_versions": approved_versions,
            "operating_system": variant["operating_system"],
            "recommendation": recommendation,
            "catalog_version": data["catalog_version"],
            "snapshot_at": data["snapshot_at"],
            "source": "mock_approved_software_catalog",
        }
    except Exception as exc:
        return err(tool, exc)
