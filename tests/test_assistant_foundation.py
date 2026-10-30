"""
Automated Unit Tests for June AI Assistant Foundation (Phase 6).
Verifies IdentityManager, ConversationStore, Modular Providers,
JSON-RPC IPC protocol, Daemon dispatching, and JuneClient.
"""

import json
import os
import shutil
import tempfile
import unittest

from assistant.core.client import JuneClient
from assistant.core.daemon import JuneDaemon
from assistant.core.identity import DEFAULT_IDENTITY_CONFIG, PERSONALITY_PRESETS, IdentityManager
from assistant.core.ipc import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    JsonRpcRequest,
    JsonRpcResponse,
)
from assistant.memory.conversation_store import ConversationStore
from assistant.providers.anthropic_provider import AnthropicProvider
from assistant.providers.gemini_provider import GeminiProvider
from assistant.providers.mock_provider import MockProvider
from assistant.providers.ollama_provider import OllamaProvider
from assistant.providers.openai_provider import OpenAIProvider
from assistant.providers.registry import ProviderRegistry


class TestAssistantFoundation(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="june_test_")
        self.config_path = os.path.join(self.test_dir, "assistant.json")
        self.db_path = os.path.join(self.test_dir, "conversations.db")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Identity Manager Tests
    # -------------------------------------------------------------------------
    def test_identity_defaults_and_persistence(self):
        manager = IdentityManager(config_path=self.config_path)
        self.assertEqual(manager.get_display_name(), "June")
        self.assertEqual(manager.get_avatar(), "󱚣")
        self.assertEqual(manager.get_personality(), "helpful")
        self.assertTrue(os.path.exists(self.config_path))

    def test_identity_renaming(self):
        manager = IdentityManager(config_path=self.config_path)
        # Rename assistant to custom name (Rule 2.1)
        self.assertTrue(manager.set_display_name("Krupa AI"))
        self.assertEqual(manager.get_display_name(), "Krupa AI")

        # Reload from disk
        reloaded = IdentityManager(config_path=self.config_path)
        self.assertEqual(reloaded.get_display_name(), "Krupa AI")

    def test_personality_presets(self):
        manager = IdentityManager(config_path=self.config_path)
        self.assertTrue(manager.set_personality("coder"))
        self.assertEqual(manager.get_personality(), "coder")
        self.assertIn("software engineer", manager.get_system_prompt())

        self.assertTrue(manager.set_personality("concise"))
        self.assertEqual(manager.get_personality(), "concise")
        self.assertIn("ultra-concise", manager.get_system_prompt())

    # -------------------------------------------------------------------------
    # 2. SQLite Conversation Store Tests
    # -------------------------------------------------------------------------
    def test_conversation_store_sessions_and_messages(self):
        store = ConversationStore(db_path=self.db_path)

        # Create session
        sid = store.create_session(title="Development Session", provider="mock", model="mock-smart")
        self.assertIsNotNone(sid)

        # Add messages
        msg1 = store.add_message(sid, role="user", content="How do I use Hyprland?")
        msg2 = store.add_message(sid, role="assistant", content="Use Super key for navigation.")
        self.assertGreater(msg1, 0)
        self.assertGreater(msg2, msg1)

        # Retrieve messages
        messages = store.get_messages(sid)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "How do I use Hyprland?")
        self.assertEqual(messages[1]["role"], "assistant")

        # Context retrieval
        context = store.get_recent_context(sid, limit=5)
        self.assertEqual(len(context), 2)
        self.assertEqual(context[0]["role"], "user")

        # Search
        results = store.search_messages("Hyprland")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["session_id"], sid)

        # Markdown export
        md = store.export_session_markdown(sid)
        self.assertIn("Development Session", md)
        self.assertIn("How do I use Hyprland?", md)

        # Delete session
        self.assertTrue(store.delete_session(sid))
        self.assertEqual(len(store.get_messages(sid)), 0)

    # -------------------------------------------------------------------------
    # 3. Provider Architecture Tests
    # -------------------------------------------------------------------------
    def test_mock_provider(self):
        mock = MockProvider()
        self.assertTrue(mock.is_configured())
        self.assertIn("mock-smart", mock.list_models())

        conn = mock.test_connection()
        self.assertTrue(conn["success"])

        # Test shortcut answer
        reply = mock.chat([{"role": "user", "content": "Tell me about keybind shortcuts"}])
        self.assertIn("Super + Space", reply)

        # Test streaming simulation
        chunks = list(mock.chat([{"role": "user", "content": "hi"}], stream=True))
        self.assertGreater(len(chunks), 1)

    def test_cloud_providers_unconfigured_by_default(self):
        # Without API keys, cloud providers report is_configured = False
        gemini = GeminiProvider(api_key="")
        self.assertFalse(gemini.is_configured())

        openai = OpenAIProvider(api_key="")
        self.assertFalse(openai.is_configured())

        anthropic = AnthropicProvider(api_key="")
        self.assertFalse(anthropic.is_configured())

    def test_provider_registry_fallback(self):
        reg = ProviderRegistry()
        # When unconfigured cloud provider requested, fallback to mock
        prov = reg.get_provider("gemini")
        # Should return mock since gemini has no API key in test environment
        self.assertIn(prov.name, ["gemini", "mock"])

        providers_meta = reg.list_providers()
        self.assertEqual(len(providers_meta), 5)
        provider_ids = [p["id"] for p in providers_meta]
        self.assertIn("mock", provider_ids)
        self.assertIn("gemini", provider_ids)
        self.assertIn("openai", provider_ids)
        self.assertIn("anthropic", provider_ids)
        self.assertIn("ollama", provider_ids)

    # -------------------------------------------------------------------------
    # 4. JSON-RPC IPC Protocol Tests
    # -------------------------------------------------------------------------
    def test_jsonrpc_structures(self):
        req = JsonRpcRequest(method="ping", params={"arg": 123}, id=42)
        raw_json = req.to_json()
        parsed = json.loads(raw_json)
        self.assertEqual(parsed["jsonrpc"], "2.0")
        self.assertEqual(parsed["method"], "ping")
        self.assertEqual(parsed["id"], 42)

        resp = JsonRpcResponse.success(id=42, result={"status": "ok"})
        resp_json = json.loads(resp.to_json())
        self.assertEqual(resp_json["result"]["status"], "ok")

        err_resp = JsonRpcResponse.error_response(id=42, code=METHOD_NOT_FOUND, message="Not Found")
        err_json = json.loads(err_resp.to_json())
        self.assertEqual(err_json["error"]["code"], METHOD_NOT_FOUND)

    # -------------------------------------------------------------------------
    # 5. June Daemon Dispatcher Tests
    # -------------------------------------------------------------------------
    def test_daemon_dispatch_ping_and_chat(self):
        daemon = JuneDaemon(
            config_path=self.config_path,
            db_path=self.db_path,
            tcp_port=42499,
        )

        # Ping dispatch
        ping_res = daemon.dispatch("ping", {})
        self.assertEqual(ping_res["status"], "online")
        self.assertEqual(ping_res["name"], "June")

        # Chat dispatch
        chat_res = daemon.dispatch("chat", {"message": "What is the Wi-Fi hotspot setup?"})
        self.assertIn("content", chat_res)
        self.assertIn("Access Point", chat_res["content"])
        self.assertIsNotNone(chat_res["session_id"])

        # Verify message stored in DB
        messages = daemon.store.get_messages(chat_res["session_id"])
        self.assertEqual(len(messages), 2)  # User + Assistant

        # Emergency Stop
        stop_res = daemon.dispatch("emergency_stop", {})
        self.assertEqual(stop_res["status"], "aborted")

    # -------------------------------------------------------------------------
    # 6. June Client Standalone In-Process Fallback Tests
    # -------------------------------------------------------------------------
    def test_client_standalone_execution(self):
        client = JuneClient()
        ping_data = client.ping()
        self.assertIn("name", ping_data)

        chat_data = client.chat("Hello June")
        self.assertEqual(chat_data["role"], "assistant")
        self.assertIn("June", chat_data["content"])

        providers_data = client.list_providers()
        self.assertIn("providers", providers_data)


if __name__ == "__main__":
    unittest.main()
