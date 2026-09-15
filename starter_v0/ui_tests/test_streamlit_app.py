from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from providers.base import ModelResponse, ToolCall


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "ui_tests" / "_ui_transcripts"


class ScriptedProvider:
    default_model = "test-model"

    def __init__(self, responses):
        self.responses = list(responses)
        self.messages = []

    def complete(self, messages, tools=None, **kwargs):
        self.messages.append(list(messages))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def final(reply="Hoan tat"):
    return ModelResponse(text=json.dumps({
        "intent": "test",
        "action": "answer",
        "reply": reply,
        "evidence_ids": [],
    }))


class StreamlitAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        os.environ["DAY04_UI_PROVIDER"] = "openai"
        os.environ["DAY04_UI_MODEL"] = "test-model"
        os.environ["DAY04_UI_TRANSCRIPTS_DIR"] = str(OUTPUT_DIR)

    @classmethod
    def tearDownClass(cls):
        for path in OUTPUT_DIR.glob("*.json"):
            path.unlink()
        OUTPUT_DIR.rmdir()

    def run_app(self, provider):
        patcher = patch("providers.make_provider", return_value=provider)
        patcher.start()
        self.addCleanup(patcher.stop)
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def submit(self, app, text):
        app.chat_input[0].set_value(text).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        return app.session_state["turns"][-1]

    def test_answered_tool_trace_and_transcript(self):
        provider = ScriptedProvider([
            ModelResponse(tool_calls=[ToolCall("check_service_status", {
                "service": "vpn", "environment": "production",
            })]),
            final("VPN da duoc kiem tra"),
        ])
        app = self.run_app(provider)
        turn = self.submit(app, "Kiem tra VPN production")

        self.assertEqual(turn["status"], "answered")
        self.assertEqual(turn["tool_events"][0]["tool"], "check_service_status")
        self.assertEqual(turn["tool_events"][0]["args"]["environment"], "production")
        self.assertEqual(len(provider.messages), 2)
        path = Path(app.session_state["transcript_path"])
        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["turns"][0]["status"], "answered")
        self.assertTrue(saved["prompt_hash"])
        self.assertTrue(saved["tools_hash"])
        self.assertNotIn("API_KEY", path.read_text(encoding="utf-8"))

        calls_before_rerun = len(provider.messages)
        app.run()
        self.assertEqual(len(app.session_state["turns"]), 1)
        self.assertEqual(len(provider.messages), calls_before_rerun)
        self.assertTrue(any("VPN da duoc kiem tra" in item.value for item in app.markdown))
        self.assertTrue(app.selectbox[0].disabled)

    def test_clarification_then_contextual_answer(self):
        provider = ScriptedProvider([
            ModelResponse(tool_calls=[ToolCall("clarify", {
                "question": "Ma may la gi?", "response_type": "text",
            })]),
            ModelResponse(tool_calls=[ToolCall("inspect_device", {
                "asset_id": "LT-240", "check": "network",
            })]),
            final("Da kiem tra LT-240"),
        ])
        app = self.run_app(provider)
        first = self.submit(app, "Kiem tra network tren laptop cua toi")
        self.assertEqual(first["status"], "waiting_for_user")
        self.assertEqual(first["tool_events"][0]["tool"], "clarify")

        second = self.submit(app, "Ma may la LT-240")
        self.assertEqual(second["status"], "answered")
        self.assertEqual(second["tool_events"][0]["tool"], "inspect_device")
        contents = [item["content"] for item in provider.messages[1]]
        self.assertTrue(any("Kiem tra network" in value for value in contents))
        self.assertEqual(len(app.session_state["history"]), 4)

    def test_provider_error_is_recorded_and_saved(self):
        app = self.run_app(ScriptedProvider([RuntimeError("provider unavailable")]))
        turn = self.submit(app, "Kiem tra VPN production")
        self.assertEqual(turn["status"], "provider_error")
        self.assertIn("RuntimeError", turn["error"])
        saved = json.loads(Path(app.session_state["transcript_path"]).read_text(encoding="utf-8"))
        self.assertEqual(saved["turns"][0]["status"], "provider_error")

    def test_max_tool_rounds_preserves_all_events(self):
        call = ModelResponse(tool_calls=[ToolCall("check_service_status", {
            "service": "vpn", "environment": "production",
        })])
        app = self.run_app(ScriptedProvider([call, call, call, call]))
        turn = self.submit(app, "Kiem tra VPN")
        self.assertEqual(turn["status"], "max_tool_rounds")
        self.assertEqual(len(turn["rounds"]), 4)
        self.assertEqual(len(turn["tool_events"]), 4)

    def test_tool_error_and_empty_result_are_preserved(self):
        provider = ScriptedProvider([
            ModelResponse(tool_calls=[ToolCall("missing_tool", {})]),
            final(),
        ])
        app = self.run_app(provider)
        error_turn = self.submit(app, "Trigger tool error")
        result = error_turn["tool_events"][0]["result"]
        self.assertEqual(result["error"], "unknown_tool")

        empty_provider = ScriptedProvider([
            ModelResponse(tool_calls=[ToolCall("empty_test_tool", {})]),
            final(),
        ])
        with patch.dict("chat.TOOL_FUNCTIONS", {"empty_test_tool": lambda: []}):
            app = self.run_app(empty_provider)
            empty_turn = self.submit(app, "Trigger empty result")
        self.assertEqual(empty_turn["tool_events"][0]["result"], [])
        self.assertEqual(len(app.exception), 0)

    def test_new_conversation_resets_state_and_keeps_old_file(self):
        app = self.run_app(ScriptedProvider([final()]))
        self.submit(app, "Xin chao")
        old_session = app.session_state["session_id"]
        old_path = Path(app.session_state["transcript_path"])
        self.assertTrue(old_path.exists())

        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertNotEqual(app.session_state["session_id"], old_session)
        self.assertEqual(app.session_state["turns"], [])
        self.assertEqual(app.session_state["history"], [])
        self.assertNotEqual(Path(app.session_state["transcript_path"]), old_path)
        self.assertTrue(old_path.exists())


if __name__ == "__main__":
    unittest.main()
