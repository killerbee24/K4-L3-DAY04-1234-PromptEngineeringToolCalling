from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from chat import json_text, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

_SENSITIVE_PATTERNS = (
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{8,}"),
    re.compile(
        r"(?i)\b(?:password|passwd|api[_ -]?key|access[_ -]?token|token|mfa|otp|recovery[_ -]?code)\b"
        r"\s*(?:[:=]|\bis\b|\blà\b)\s*\S+"
    ),
)


def redact_sensitive_text(text: str) -> str:
    redacted = text
    for pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def contains_sensitive_data(text: str) -> bool:
    return redact_sensitive_text(text) != text


def sanitize_for_transcript(value: Any) -> Any:
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, list):
        return [sanitize_for_transcript(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_transcript(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_for_transcript(item) for key, item in value.items()}
    return value


class HelpdeskAppService:
    """Backend boundary shared by the Streamlit UI and its tests."""

    def __init__(
        self,
        *,
        provider_name: str,
        version: str,
        model: str | None = None,
        history_window: int = 5,
        max_tool_rounds: int = 4,
        provider: Any | None = None,
        system_prompt_path: Path = SYSTEM_PROMPT_PATH,
        tools_path: Path = TOOLS_PATH,
        transcripts_dir: Path = TRANSCRIPTS_DIR,
    ) -> None:
        load_lab_env(ROOT)
        self.provider_name = provider_name
        self.version = version
        self.model_override = model
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.system_prompt_path = system_prompt_path
        self.tools_path = tools_path
        self.transcripts_dir = transcripts_dir

        self.provider = provider or make_provider(provider_name)
        self.selected_model = model or getattr(self.provider, "default_model", None)
        self.system_prompt = system_prompt_path.read_text(encoding="utf-8")
        declarations = load_tool_declarations(tools_path)
        self.tools = to_openai_tools(declarations)
        self.artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    def send_message(
        self,
        *,
        user_text: str,
        history: list[dict[str, str]],
    ) -> dict[str, Any]:
        if contains_sensitive_data(user_text):
            assistant_text = (
                "Mình không thể xử lý hoặc lưu nội dung có vẻ chứa password, API key, token, "
                "MFA/OTP hay recovery code. Hãy gửi lại yêu cầu sau khi loại bỏ dữ liệu nhạy cảm."
            )
            return {
                "status": "input_rejected",
                "assistant_text": assistant_text,
                "rounds": [],
                "tool_events": [],
                "display_user_text": redact_sensitive_text(user_text),
                "history_messages": [
                    {"role": "user", "content": redact_sensitive_text(user_text)},
                    {"role": "assistant", "content": assistant_text},
                ],
            }

        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(history, self.history_window),
            {"role": "user", "content": user_text},
        ]
        result = run_model_tool_loop(
            provider=self.provider,
            messages=messages,
            tools=self.tools,
            model=self.model_override,
            max_tool_rounds=self.max_tool_rounds,
        )

        assistant_text = result.get("assistant_text", "")
        evidence = sanitize_for_transcript(
            {
                "status": result.get("status"),
                "tool_events": result.get("tool_events", []),
            }
        )
        assistant_history = assistant_text
        if evidence["tool_events"]:
            assistant_history += (
                "\n\nPRIOR_TOOL_EVIDENCE_JSON:\n"
                + json_text(evidence, max_chars=12000)
            )

        return {
            **result,
            "display_user_text": user_text,
            "history_messages": [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_history},
            ],
        }

    def build_transcript(
        self,
        *,
        transcript_id: str,
        created_at: str,
        updated_at: str,
        turns: list[dict[str, Any]],
    ) -> dict[str, Any]:
        transcript = {
            "transcript_id": transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": self.provider_name,
            "model": self.selected_model,
            "system_prompt": str(self.system_prompt_path),
            "tools": str(self.tools_path),
            "history_window": self.history_window,
            "max_tool_rounds": self.max_tool_rounds,
            "created_at": created_at,
            "updated_at": updated_at,
            "turns": turns,
        }
        return sanitize_for_transcript(transcript)

    def transcript_path(self, transcript_id: str) -> Path:
        return self.transcripts_dir / f"{transcript_id}.transcript.json"

    def save_transcript(self, transcript: dict[str, Any]) -> Path:
        path = self.transcript_path(transcript["transcript_id"])
        write_transcript(path, sanitize_for_transcript(transcript))
        return path
