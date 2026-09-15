from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import streamlit as st

from app_service import HelpdeskAppService
from chat import json_text, now_iso, safe_slug
from providers import make_provider


PROVIDERS = ["openai", "openrouter", "gemini", "anthropic"]
QUICK_PROMPTS = {
    "Status": "Dịch vụ VPN production hiện có đang gặp sự cố không?",
    "Missing Info": "Kiểm tra Wi-Fi trên laptop của mình giúp nhé.",
    "Multi-Turn": "Mã máy là LT-240. Chỉ kiểm tra network trên đúng máy đó.",
    "Ticket": "Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.",
}

STATUS_LABELS = {
    "answered": ("Answered", "status-ok"),
    "waiting_for_user": ("Waiting", "status-wait"),
    "input_rejected": ("Rejected", "status-error"),
    "provider_error": ("Provider Error", "status-error"),
    "max_tool_rounds": ("Max Rounds", "status-wait"),
    "started": ("Started", "status-wait"),
}


def init_session() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "transcript_id" not in st.session_state:
        st.session_state.transcript_id = new_transcript_id("v3_bonus", "openai")
    if "transcript_created_at" not in st.session_state:
        st.session_state.transcript_created_at = now_iso()
    if "last_config" not in st.session_state:
        st.session_state.last_config = None


def new_transcript_id(version: str, provider: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return "_".join([safe_slug(version), safe_slug(provider), timestamp])


def reset_chat(version: str, provider: str) -> None:
    st.session_state.chat_history = []
    st.session_state.turns = []
    st.session_state.transcript_id = new_transcript_id(version, provider)
    st.session_state.transcript_created_at = now_iso()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 1.6rem;
            max-width: 1280px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.55rem;
        }
        .app-header {
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 1rem;
            padding-bottom: 0.85rem;
        }
        .app-kicker {
            color: #64748b;
            font-size: 0.88rem;
            margin-bottom: 0.15rem;
        }
        .app-title {
            color: #111827;
            font-size: 1.9rem;
            font-weight: 750;
            line-height: 1.15;
        }
        .app-subtitle {
            color: #475569;
            max-width: 760px;
            margin-top: 0.25rem;
        }
        .status-pill {
            border-radius: 999px;
            display: inline-flex;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.55rem;
            padding: 0.35rem 0.55rem;
        }
        .status-ok {
            background: #dcfce7;
            color: #166534;
        }
        .status-wait {
            background: #fef3c7;
            color: #92400e;
        }
        .status-error {
            background: #fee2e2;
            color: #991b1b;
        }
        .metric-strip {
            display: grid;
            gap: 0.5rem;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            margin: 0.75rem 0 0.85rem;
        }
        .metric-box {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.65rem 0.7rem;
            background: #ffffff;
        }
        .metric-label {
            color: #64748b;
            font-size: 0.74rem;
        }
        .metric-value {
            color: #111827;
            font-size: 1.08rem;
            font-weight: 750;
            margin-top: 0.1rem;
        }
        .tool-call {
            border: 1px solid #dbe4ef;
            border-radius: 8px;
            margin: 0.6rem 0;
            padding: 0.7rem;
            background: #f8fafc;
        }
        .tool-call-title {
            color: #0f172a;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }
        .muted-small {
            color: #64748b;
            font-size: 0.82rem;
        }
        .quick-prompt-row {
            margin-bottom: 0.65rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    label, css_class = STATUS_LABELS.get(status, (status.replace("_", " ").title(), "status-wait"))
    return f'<span class="status-pill {css_class}">{label}</span>'


def count_tool_calls(turns: list[dict[str, Any]]) -> int:
    return sum(len(round_item.get("tool_calls", [])) for turn in turns for round_item in turn.get("rounds", []))


def transcript_bytes(transcript: dict[str, Any]) -> str:
    return json.dumps(transcript, ensure_ascii=False, indent=2, default=str)


def render_tool_rounds(rounds: list[dict[str, Any]]) -> None:
    if not rounds:
        return

    st.markdown("**Tool trace**")
    for round_item in rounds:
        round_number = round_item.get("round", "?")
        calls = round_item.get("tool_calls", [])
        results = round_item.get("tool_results", [])
        with st.expander(f"Round {round_number} · {len(calls)} call(s)", expanded=bool(calls)):
            assistant_text = round_item.get("assistant_text")
            if assistant_text:
                st.caption("Assistant before tools")
                st.write(assistant_text)

            if not calls:
                st.info("No tool call in this round.")

            for index, call in enumerate(calls, start=1):
                matching_result = results[index - 1] if index - 1 < len(results) else None
                result = matching_result.get("result", matching_result) if matching_result else None
                has_error = isinstance(result, dict) and bool(result.get("error"))
                result_label = "Error" if has_error else "Result"

                st.markdown(
                    f"""
                    <div class="tool-call">
                        <div class="tool-call-title">{index}. {call.get('name', '<unknown>')}</div>
                        <div class="muted-small">Round order: {round_number}.{index} · {result_label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                args_col, result_col = st.columns(2)
                with args_col:
                    st.caption("Input / arguments")
                    st.json(call.get("args", {}))
                with result_col:
                    st.caption("Result / error")
                    if matching_result is None:
                        st.warning("No local result was recorded for this call.")
                    elif has_error:
                        st.error(json_text(result))
                    else:
                        st.json(result)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.write(turn["user"])

    with st.chat_message("assistant"):
        status = turn.get("status", "unknown")
        st.markdown(status_badge(status), unsafe_allow_html=True)
        if status == "provider_error":
            st.error(turn.get("error", "Provider error"))
        elif status == "waiting_for_user":
            st.write(turn.get("assistant_text") or "")
        elif status == "input_rejected":
            st.error(turn.get("assistant_text") or "Sensitive input was rejected.")
        elif status == "max_tool_rounds":
            st.warning(turn.get("assistant_text") or "Stopped after max tool rounds.")
        else:
            st.write(turn.get("assistant_text") or "")
        render_tool_rounds(turn.get("rounds", []))


def main() -> None:
    st.set_page_config(page_title="IT Helpdesk Agent", page_icon=":material/support_agent:", layout="wide")
    init_session()
    inject_styles()

    st.markdown(
        """
        <div class="app-header">
            <div class="app-kicker">Northstar Labs · Internal service desk</div>
            <div class="app-title">IT Helpdesk Agent</div>
            <div class="app-subtitle">Demo chat with visible tool calls, arguments, results, errors, and transcript export.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Run Config")
        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        provider_preview = make_provider(provider_name)
        default_model = getattr(provider_preview, "default_model", None)
        model_input = st.text_input("Model", value=default_model or "")
        model = model_input.strip() or None
        version = st.text_input("Version label", value="v3_bonus")
        history_window = st.number_input("History window", min_value=0, max_value=20, value=5)
        max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)

        service = HelpdeskAppService(
            provider_name=provider_name,
            version=version,
            model=model,
            history_window=int(history_window),
            max_tool_rounds=int(max_tool_rounds),
        )
        artifact_version = service.artifact_version
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

    transcript = service.build_transcript(
        transcript_id=st.session_state.transcript_id,
        created_at=st.session_state.transcript_created_at,
        updated_at=now_iso(),
        turns=st.session_state.turns,
    )
    transcript_path = service.transcript_path(st.session_state.transcript_id)

    left, right = st.columns([2.25, 1], gap="large")
    with right:
        st.subheader("Session")
        st.markdown(
            f"""
            <div class="metric-strip">
                <div class="metric-box"><div class="metric-label">Turns</div><div class="metric-value">{len(st.session_state.turns)}</div></div>
                <div class="metric-box"><div class="metric-label">Tool Calls</div><div class="metric-value">{count_tool_calls(st.session_state.turns)}</div></div>
                <div class="metric-box"><div class="metric-label">Version</div><div class="metric-value">{version}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Provider / model")
        st.code(f"{provider_name} · {model or default_model or 'default'}")
        st.caption("Transcript file")
        st.code(transcript_path.name)
        st.caption("Không nhập password, API key, token, MFA/OTP hoặc recovery code.")
        st.download_button(
            "Download transcript JSON",
            data=transcript_bytes(transcript),
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
        st.markdown('<div class="quick-prompt-row">', unsafe_allow_html=True)
        prompt_cols = st.columns(len(QUICK_PROMPTS))
        selected_prompt = None
        for column, (label, prompt) in zip(prompt_cols, QUICK_PROMPTS.items()):
            with column:
                if st.button(label, use_container_width=True):
                    selected_prompt = prompt
        st.markdown("</div>", unsafe_allow_html=True)

        for turn in st.session_state.turns:
            render_turn(turn)

        user_text = st.chat_input("Type an IT helpdesk request...")
        active_text = selected_prompt or user_text
        if active_text:
            turn_index = len(st.session_state.turns) + 1
            turn_record: dict[str, Any] = {
                "turn_index": turn_index,
                "started_at": now_iso(),
                "user": active_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }

            with st.spinner("Calling model and tools..."):
                try:
                    result = service.send_message(
                        user_text=active_text,
                        history=st.session_state.chat_history,
                    )
                    history_messages = result.pop("history_messages", [])
                    turn_record["user"] = result.pop("display_user_text", active_text)
                    turn_record.update(result)
                    st.session_state.chat_history.extend(history_messages)
                except Exception as exc:
                    turn_record.update({
                        "status": "provider_error",
                        "error": f"{type(exc).__name__}: {str(exc)}",
                    })

            turn_record["ended_at"] = now_iso()
            st.session_state.turns.append(turn_record)
            transcript = service.build_transcript(
                transcript_id=st.session_state.transcript_id,
                created_at=st.session_state.transcript_created_at,
                updated_at=now_iso(),
                turns=st.session_state.turns,
            )
            service.save_transcript(transcript)
            st.rerun()


if __name__ == "__main__":
    main()
