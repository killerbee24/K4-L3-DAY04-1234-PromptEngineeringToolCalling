from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

PROVIDERS = ["gemini", "openrouter", "openai", "anthropic"]


def init_session() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "transcript_id" not in st.session_state:
        st.session_state.transcript_id = new_transcript_id("v0", "gemini")
    if "last_config" not in st.session_state:
        st.session_state.last_config = None


def new_transcript_id(version: str, provider: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return "_".join([safe_slug(version), safe_slug(provider), timestamp])


def reset_chat(version: str, provider: str) -> None:
    st.session_state.chat_history = []
    st.session_state.turns = []
    st.session_state.transcript_id = new_transcript_id(version, provider)


def current_transcript(
    *,
    artifact_version: Any,
    provider: str,
    model: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    return {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": st.session_state.transcript_id.rsplit("_", 1)[-1],
        "updated_at": now_iso(),
        "turns": st.session_state.turns,
    }


def save_transcript(transcript: dict[str, Any]) -> Path:
    path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"
    write_transcript(path, transcript)
    return path


def render_tool_rounds(rounds: list[dict[str, Any]]) -> None:
    if not rounds:
        return

    st.markdown("**Tool Trace**")
    for round_item in rounds:
        round_number = round_item.get("round", "?")
        calls = round_item.get("tool_calls", [])
        results = round_item.get("tool_results", [])
        with st.expander(f"Round {round_number}: {len(calls)} tool call(s)", expanded=True):
            assistant_text = round_item.get("assistant_text")
            if assistant_text:
                st.caption("Assistant before tools")
                st.write(assistant_text)

            if not calls:
                st.info("No tool call in this round.")

            for index, call in enumerate(calls, start=1):
                st.markdown(f"**{index}. `{call.get('name', '<unknown>')}`**")
                st.caption("Input / arguments")
                st.json(call.get("args", {}))

                matching_result = results[index - 1] if index - 1 < len(results) else None
                st.caption("Result / error")
                if matching_result is None:
                    st.warning("No local result was recorded for this call.")
                else:
                    result = matching_result.get("result", matching_result)
                    if isinstance(result, dict) and result.get("error"):
                        st.error(json_text(result))
                    else:
                        st.json(result)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.write(turn["user"])

    with st.chat_message("assistant"):
        status = turn.get("status", "unknown")
        if status == "provider_error":
            st.error(turn.get("error", "Provider error"))
        elif status == "waiting_for_user":
            st.warning("Waiting for user input or confirmation.")
            st.write(turn.get("assistant_text") or "")
        elif status == "max_tool_rounds":
            st.warning(turn.get("assistant_text") or "Stopped after max tool rounds.")
        else:
            st.write(turn.get("assistant_text") or "")
        render_tool_rounds(turn.get("rounds", []))


def main() -> None:
    st.set_page_config(page_title="IT Helpdesk Agent", page_icon="IT", layout="wide")
    load_lab_env(ROOT)
    init_session()

    st.title("IT Helpdesk Agent")

    with st.sidebar:
        st.header("Runtime")
        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        provider = make_provider(provider_name)
        default_model = getattr(provider, "default_model", None)
        model_input = st.text_input("Model", value=default_model or "")
        model = model_input.strip() or None
        version = st.text_input("Version label", value="v0")
        history_window = st.number_input("History window", min_value=0, max_value=20, value=5)
        max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)

        artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
        st.divider()
        st.caption("Artifact version")
        st.code(artifact_version.artifact_version)
        st.caption("Prompt hash")
        st.code(artifact_version.prompt_hash[:12])
        st.caption("Tools hash")
        st.code(artifact_version.tools_hash[:12])

        config = (provider_name, model, version)
        if st.session_state.last_config is None:
            st.session_state.last_config = config
        elif st.session_state.last_config != config:
            st.session_state.last_config = config
            reset_chat(version, provider_name)

        if st.button("New session", use_container_width=True):
            reset_chat(version, provider_name)
            st.rerun()

    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    transcript = current_transcript(
        artifact_version=artifact_version,
        provider=provider_name,
        model=model,
        history_window=int(history_window),
        max_tool_rounds=int(max_tool_rounds),
    )
    transcript_path = save_transcript(transcript)

    left, right = st.columns([2, 1])
    with right:
        st.subheader("Session")
        st.write(f"Provider: `{provider_name}`")
        st.write(f"Model: `{model or default_model or 'default'}`")
        st.write(f"Transcript: `{transcript_path.name}`")
        st.download_button(
            "Download transcript JSON",
            data=json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
            file_name=transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )

        if st.session_state.turns:
            last_status = st.session_state.turns[-1].get("status")
            if last_status == "waiting_for_user":
                st.warning("Agent is waiting for missing information or confirmation.")
            elif last_status == "provider_error":
                st.error("Last turn had a provider error.")

    with left:
        st.subheader("Chat")
        for turn in st.session_state.turns:
            render_turn(turn)

        user_text = st.chat_input("Type an IT helpdesk request...")
        if user_text:
            turn_index = len(st.session_state.turns) + 1
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")},
                *trim_history(st.session_state.chat_history, int(history_window)),
                {"role": "user", "content": user_text},
            ]
            turn_record: dict[str, Any] = {
                "turn_index": turn_index,
                "started_at": now_iso(),
                "user": user_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }

            with st.spinner("Calling model and tools..."):
                try:
                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages,
                        tools=openai_tools,
                        model=model,
                        max_tool_rounds=int(max_tool_rounds),
                    )
                    turn_record.update(result)
                    assistant_text = result.get("assistant_text", "")
                    st.session_state.chat_history.append({"role": "user", "content": user_text})
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
                except Exception as exc:
                    turn_record.update({
                        "status": "provider_error",
                        "error": f"{type(exc).__name__}: {str(exc)}",
                    })

            turn_record["ended_at"] = now_iso()
            st.session_state.turns.append(turn_record)
            transcript = current_transcript(
                artifact_version=artifact_version,
                provider=provider_name,
                model=model,
                history_window=int(history_window),
                max_tool_rounds=int(max_tool_rounds),
            )
            save_transcript(transcript)
            st.rerun()


if __name__ == "__main__":
    main()
