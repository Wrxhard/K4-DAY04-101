"""Streamlit UI for the real IT Helpdesk agent runtime."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = Path(os.getenv("DAY04_UI_TRANSCRIPTS_DIR", ROOT / "transcripts"))
PROVIDERS = ("openrouter", "openai", "anthropic", "gemini")
load_lab_env(ROOT)
PROVIDER_KEYS = {
    "openrouter": "OPENROUTER_API_KEY", "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY",
}
configured_provider = next((name for name in PROVIDERS if os.getenv(PROVIDER_KEYS[name])), "openrouter")
DEFAULT_PROVIDER = os.getenv("DAY04_UI_PROVIDER", configured_provider).lower()
DEFAULT_VERSION = os.getenv("DAY04_UI_VERSION", "v3")
HISTORY_WINDOW = int(os.getenv("DAY04_UI_HISTORY_WINDOW", "5"))
MAX_TOOL_ROUNDS = int(os.getenv("DAY04_UI_MAX_TOOL_ROUNDS", "4"))

st.set_page_config(page_title="Northstar IT Helpdesk", page_icon="N", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root {--blue:#2563eb;--ink:#172033;--muted:#64748b;--line:#e3e8ef;--soft:#f6f8fb}
.stApp {background:#f6f8fb;color:var(--ink)}
.block-container {max-width:1080px;padding-top:1.4rem;padding-bottom:6rem}
[data-testid="stSidebar"] {background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"] .block-container {padding-top:1.25rem}
[data-testid="stChatMessage"] {background:#fff;border:1px solid var(--line);border-radius:8px;padding:.8rem 1rem;margin:.65rem 0;box-shadow:0 3px 12px #17203308}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {background:#eef4ff;border-color:#dbe7ff}
[data-testid="stChatInput"] {border-color:#cbd5e1;box-shadow:0 8px 24px #17203312}
.brand {display:flex;align-items:center;gap:.7rem;margin-bottom:1rem}
.brand-mark {display:grid;place-items:center;width:38px;height:38px;border-radius:8px;background:var(--blue);color:white;font-weight:800}
.brand-title {font-weight:750;color:var(--ink);line-height:1.1}.brand-sub {font-size:.75rem;color:var(--muted)}
.hero {border-bottom:1px solid var(--line);padding:.35rem 0 1rem;margin-bottom:1rem}
.hero h1 {font-size:1.65rem;margin:0 0 .3rem;color:var(--ink);letter-spacing:0}.hero p {margin:0;color:var(--muted)}
.eyebrow {font-size:.7rem;font-weight:750;letter-spacing:0;color:#64748b;margin:.9rem 0 .35rem}
.meta {font-size:.78rem;color:var(--muted);overflow-wrap:anywhere;background:var(--soft);padding:.55rem;border-radius:8px}
.session-pill {display:inline-block;background:#ecfdf5;color:#047857;border:1px solid #bbf7d0;border-radius:999px;padding:.2rem .55rem;font-size:.72rem;font-weight:700}
.welcome {text-align:center;padding:2rem 1rem;color:var(--muted)}.welcome strong {display:block;color:var(--ink);font-size:1.05rem;margin-bottom:.3rem}
pre {white-space:pre-wrap!important;overflow-wrap:anywhere}
@media(max-width:760px){.block-container{padding-left:.8rem;padding-right:.8rem}.hero h1{font-size:1.45rem}}
</style>
""", unsafe_allow_html=True)


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "session"


def model_for(provider_name: str) -> str | None:
    configured = os.getenv("DAY04_UI_MODEL")
    if configured:
        return configured
    try:
        return getattr(make_provider(provider_name), "default_model", None)
    except Exception:
        # Let message processing report provider configuration errors as a turn
        # instead of crashing the whole app during session initialization.
        return None


def new_session(provider_name: str, version: str) -> None:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    metadata = artifact_version_dict(build_artifact_version(version, PROMPT_PATH, TOOLS_PATH))
    st.session_state.update(
        session_id=uuid4().hex, history=[], turns=[], created_at=now_iso(),
        provider_name=provider_name, model_name=model_for(provider_name), version=version,
        artifact_metadata=metadata, is_processing=False, save_error=None,
        transcript_path=TRANSCRIPTS_DIR / f"{safe_slug(version)}_{safe_slug(provider_name)}_{stamp}.transcript.json",
    )


required = {"session_id", "history", "turns", "transcript_path", "created_at", "provider_name", "model_name", "version", "artifact_metadata", "is_processing"}
if not required.issubset(st.session_state):
    new_session(DEFAULT_PROVIDER if DEFAULT_PROVIDER in PROVIDERS else "openrouter", DEFAULT_VERSION)


def transcript() -> dict[str, Any]:
    return {
        "transcript_id": st.session_state.session_id,
        **st.session_state.artifact_metadata,
        "provider": st.session_state.provider_name, "model": st.session_state.model_name,
        "system_prompt": str(PROMPT_PATH), "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW, "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": st.session_state.created_at, "updated_at": now_iso(),
        "turns": st.session_state.turns,
    }


def save_transcript() -> None:
    try:
        write_transcript(st.session_state.transcript_path, transcript())
        st.session_state.save_error = None
    except Exception as exc:
        st.session_state.save_error = f"{type(exc).__name__}: {exc}"


def parsed_reply(raw: str) -> tuple[str, dict[str, Any] | None]:
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw, None
    if not isinstance(value, dict):
        return raw, None
    return value.get("reply") if isinstance(value.get("reply"), str) else raw, value


def render_trace(turn: dict[str, Any]) -> None:
    events = turn.get("tool_events") or []
    round_numbers = []
    for item in turn.get("rounds", []):
        round_numbers.extend([item.get("round")] * len(item.get("tool_results", [])))
    with st.expander(f"Xem quá trình xử lý — {len(events)} tool calls"):
        if not events:
            st.caption("Không gọi công cụ.")
        for index, event in enumerate(events):
            result = event.get("result")
            error = isinstance(result, dict) and bool(result.get("error"))
            empty = result in ({}, [], None)
            status = "Lỗi" if error else ("Kết quả rỗng" if empty else "Hoàn tất")
            round_no = round_numbers[index] if index < len(round_numbers) else "—"
            with st.container(border=True):
                st.markdown(f"**{event.get('tool', 'unknown')}** · Vòng {round_no} · {status}")
                args_col, result_col = st.columns(2)
                with args_col:
                    st.caption("Arguments")
                    st.json(event.get("args", {}), expanded=False)
                with result_col:
                    st.caption("Result / error")
                    st.json(result, expanded=False)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        reply, parsed = parsed_reply(turn.get("assistant_text") or "")
        status = turn.get("status")
        if status == "provider_error":
            st.error(turn.get("error", "Provider error"))
        elif status == "max_tool_rounds":
            st.warning("Agent đã dừng vì đạt giới hạn số vòng gọi tool. Đây chưa phải kết quả hoàn tất.")
            st.markdown(reply)
        elif status == "waiting_for_user":
            st.warning(reply)
        else:
            st.markdown(reply)
        labels = {
            "answered": "Đã trả lời", "waiting_for_user": "Chờ bổ sung",
            "provider_error": "Lỗi provider", "max_tool_rounds": "Đạt giới hạn tool",
        }
        st.caption(labels.get(status, f"Trạng thái: {status}"))
        if parsed:
            with st.expander("Chi tiết phản hồi agent"):
                st.json({key: parsed.get(key) for key in ("intent", "action", "evidence_ids")})
        render_trace(turn)


def process_prompt(user_text: str) -> None:
    turn: dict[str, Any] = {"turn_index": len(st.session_state.turns) + 1, "user": user_text, "assistant_text": "", "status": "started", "rounds": [], "tool_events": [], "started_at": now_iso(), "ended_at": None}
    st.session_state.is_processing = True
    try:
        messages = [{"role": "system", "content": PROMPT_PATH.read_text(encoding="utf-8")}, *trim_history(st.session_state.history, HISTORY_WINDOW), {"role": "user", "content": user_text}]
        result = run_model_tool_loop(provider=make_provider(st.session_state.provider_name), messages=messages, tools=to_openai_tools(load_tool_declarations(TOOLS_PATH)), model=st.session_state.model_name, max_tool_rounds=MAX_TOOL_ROUNDS)
        turn.update(result)
        st.session_state.history.extend([{"role": "user", "content": user_text}, {"role": "assistant", "content": result.get("assistant_text", "")}])
    except Exception as exc:
        turn.update(status="provider_error", error=f"{type(exc).__name__}: {exc}")
    finally:
        turn["ended_at"] = now_iso()
        st.session_state.turns.append(turn)
        st.session_state.is_processing = False
        save_transcript()


with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">N</div><div><div class="brand-title">Northstar IT</div><div class="brand-sub">Helpdesk Agent</div></div></div>', unsafe_allow_html=True)
    st.markdown('<span class="session-pill">Phiên đang hoạt động</span>', unsafe_allow_html=True)
    if st.button("＋ Hội thoại mới", use_container_width=True):
        new_session(st.session_state.provider_name, st.session_state.version)
        st.rerun()
    st.markdown('<div class="eyebrow">CẤU HÌNH PHIÊN</div>', unsafe_allow_html=True)
    locked = bool(st.session_state.history)
    provider = st.selectbox("Provider", PROVIDERS, index=PROVIDERS.index(st.session_state.provider_name), disabled=locked)
    version = st.text_input("Version", st.session_state.version, disabled=locked)
    if not locked and (provider != st.session_state.provider_name or version != st.session_state.version):
        new_session(provider, version.strip() or DEFAULT_VERSION)
        st.rerun()
    if locked:
        st.caption("Bắt đầu hội thoại mới để đổi provider hoặc version.")
    meta = st.session_state.artifact_metadata
    st.markdown('<div class="eyebrow">RUNTIME & ARTIFACT</div>', unsafe_allow_html=True)
    st.markdown(f"**Model:** `{st.session_state.model_name or 'provider default'}`")
    st.markdown(f"**Artifact:** `{meta['artifact_version']}`")
    with st.expander("SHA-256 hashes"):
        st.code(meta["prompt_hash"], language="text")
        st.code(meta["tools_hash"], language="text")
    st.markdown('<div class="eyebrow">TRANSCRIPT</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="meta">{st.session_state.transcript_path}</div>', unsafe_allow_html=True)
    if st.session_state.save_error:
        st.error(f"Không thể lưu: {st.session_state.save_error}")
    elif st.session_state.turns:
        st.success("Đã lưu")
    data = json.dumps(transcript(), ensure_ascii=False, indent=2, default=str)
    st.download_button("⇩ Tải transcript", data, file_name=st.session_state.transcript_path.name, mime="application/json", use_container_width=True)

st.markdown("""<section class="hero"><h1>IT Helpdesk Agent</h1><p>Tra cứu dịch vụ, kiểm tra thiết bị và hỗ trợ sự cố IT với tool trace có thể kiểm chứng.</p></section>""", unsafe_allow_html=True)
if not st.session_state.turns:
    st.markdown("""<div class="welcome"><strong>Xin chào! Tôi có thể giúp gì cho bạn?</strong>Hỏi về VPN, Wi-Fi, thiết bị, tài khoản, knowledge base hoặc ticket.<br>API key được đọc an toàn từ <code>.env</code>.</div>""", unsafe_allow_html=True)
for existing_turn in st.session_state.turns:
    render_turn(existing_turn)
prompt = st.chat_input("Ví dụ: Kiểm tra trạng thái VPN production.", disabled=st.session_state.is_processing)
if prompt and prompt.strip():
    submitted_text = prompt.strip()
    # Render the submitted message before the blocking provider call. Without
    # this, it only appears on the rerun after the assistant has responded.
    with st.chat_message("user"):
        st.markdown(submitted_text)
    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý yêu cầu…"):
            process_prompt(submitted_text)
    st.rerun()
