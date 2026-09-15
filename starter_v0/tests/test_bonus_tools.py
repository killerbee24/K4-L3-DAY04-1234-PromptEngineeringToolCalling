from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import TOOL_FUNCTIONS
from tools.check_maintenance_window.tool import check_maintenance_window
from tools.check_software_approval.tool import check_software_approval
from tools.lookup_ticket_status.tool import lookup_ticket_status


class BonusToolTests(unittest.TestCase):
    def test_bonus_tools_are_registered(self) -> None:
        self.assertIn("check_software_approval", TOOL_FUNCTIONS)
        self.assertIn("lookup_ticket_status", TOOL_FUNCTIONS)
        self.assertIn("check_maintenance_window", TOOL_FUNCTIONS)

    def test_approved_software_version(self) -> None:
        result = check_software_approval("Cisco Secure Client", "5.2.1", "Windows 11")
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["source"], "mock_approved_software_catalog")

    def test_outdated_software_requires_upgrade(self) -> None:
        result = check_software_approval("Cisco AnyConnect", "5.1.8", "macOS 15")
        self.assertEqual(result["status"], "upgrade_required")

    def test_unknown_software_returns_explicit_error(self) -> None:
        result = check_software_approval("Unknown Editor", "1.0", "Windows 11")
        self.assertEqual(result["error"], "software_not_found")

    def test_ticket_lookup_and_not_found(self) -> None:
        found = lookup_ticket_status("lab-1002")
        missing = lookup_ticket_status("LAB-9999")
        self.assertEqual(found["ticket"]["status"], "open")
        self.assertEqual(missing["error"], "ticket_not_found")

    def test_maintenance_lookup_and_empty_result(self) -> None:
        planned = check_maintenance_window("vpn", "production")
        empty = check_maintenance_window("sso", "staging")
        self.assertEqual(planned["status"], "planned")
        self.assertEqual(planned["windows"][0]["window_id"], "MW-201")
        self.assertEqual(empty["status"], "no_planned_window")


if __name__ == "__main__":
    unittest.main()
