from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app_service import (
    HelpdeskAppService,
    contains_sensitive_data,
    redact_sensitive_text,
)
from providers.base import ModelResponse


class FakeProvider:
    default_model = "fake-model"

    def complete(self, messages, tools=None, **kwargs):
        return ModelResponse(text="Đã xử lý bằng backend service.")


class AppServiceTests(unittest.TestCase):
    def test_sensitive_input_is_rejected_before_provider_call(self) -> None:
        service = HelpdeskAppService(
            provider_name="openai",
            version="v3",
            provider=FakeProvider(),
        )
        result = service.send_message(user_text="Bearer definitely_fake_token", history=[])

        self.assertEqual(result["status"], "input_rejected")
        self.assertEqual(result["tool_events"], [])
        self.assertEqual(result["display_user_text"], "[REDACTED]")
        self.assertNotIn("definitely_fake_token", str(result))

    def test_backend_contract_and_history_messages(self) -> None:
        service = HelpdeskAppService(
            provider_name="openai",
            version="v3",
            provider=FakeProvider(),
        )
        result = service.send_message(user_text="Kiểm tra VPN production.", history=[])

        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["assistant_text"], "Đã xử lý bằng backend service.")
        self.assertEqual(len(result["history_messages"]), 2)

    def test_transcript_is_sanitized_before_write(self) -> None:
        self.assertTrue(contains_sensitive_data("password: secret123"))
        self.assertEqual(redact_sensitive_text("password: secret123"), "[REDACTED]")

        with tempfile.TemporaryDirectory() as temp_dir:
            service = HelpdeskAppService(
                provider_name="openai",
                version="v3",
                provider=FakeProvider(),
                transcripts_dir=Path(temp_dir),
            )
            transcript = service.build_transcript(
                transcript_id="test-session",
                created_at="2026-09-15T19:00:00+07:00",
                updated_at="2026-09-15T19:01:00+07:00",
                turns=[{"user": "token=abcdefghijklmno"}],
            )
            path = service.save_transcript(transcript)
            saved = path.read_text(encoding="utf-8")

            self.assertIn("[REDACTED]", saved)
            self.assertNotIn("abcdefghijklmno", saved)


if __name__ == "__main__":
    unittest.main()
