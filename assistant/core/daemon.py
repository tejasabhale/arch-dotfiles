#!/usr/bin/env python3
"""
June AI Core Daemon Service.
Runs as a decoupled background service, maintaining local conversation SQLite storage,
identity configuration, modular AI providers, and JSON-RPC 2.0 socket server.

Complies with AGENTS.md Rule 2.1:
Decoupled & Independent Operation — The desktop shell remains 100% operational
even if June is offline or stopped.
"""

import argparse
from datetime import datetime
import json
import os
import signal
import socket
import sys
import threading
import time
from typing import Any, Dict, Optional

from assistant.action_planner import ActionPlan, ActionPlanner, ActionStep, RiskLevel
from assistant.core.identity import IdentityManager
from assistant.core.ipc import (
    DEFAULT_TCP_PORT,
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    JsonRpcResponse,
    get_default_socket_path,
)
from assistant.executor import ControlledExecutor
from assistant.file_intelligence import FileIntelligence
from assistant.languages import LanguageRouter
from assistant.memory import ConversationStore, MemoryManager
from assistant.permissions import PermissionEngine
from assistant.providers.registry import ProviderRegistry
from assistant.research import ResearchEngine
from assistant.screen_intelligence import ScreenIntelligence
from assistant.voice import VoicePipeline


class JuneDaemon:
    """Core daemon managing June AI assistant state and IPC dispatching."""

    def __init__(
        self,
        socket_path: Optional[str] = None,
        tcp_port: int = DEFAULT_TCP_PORT,
        config_path: Optional[str] = None,
        db_path: Optional[str] = None,
        memory_db_path: Optional[str] = None,
        lang_config_path: Optional[str] = None,
    ):
        self.socket_path = socket_path or get_default_socket_path()
        self.tcp_port = tcp_port
        self.identity = IdentityManager(config_path=config_path)
        self.store = ConversationStore(db_path=db_path)
        self.providers = ProviderRegistry()

        # Phase 7 & 8: Advanced Automation, Multilingual & Intelligence Engines
        self.permissions = PermissionEngine()
        self.planner = ActionPlanner(self.permissions)
        self.executor = ControlledExecutor(self.permissions)
        self._screen: Optional[ScreenIntelligence] = None
        self._files: Optional[FileIntelligence] = None
        self.memory = MemoryManager(db_path=memory_db_path)
        self._research: Optional[ResearchEngine] = None
        self._voice: Optional[VoicePipeline] = None
        self.lang_router = LanguageRouter(config_path=lang_config_path)

        self.start_time = time.time()
        self._running = False
        self._abort_flag = threading.Event()
        self._server_threads: list[threading.Thread] = []

    @property
    def screen(self) -> ScreenIntelligence:
        if self._screen is None:
            self._screen = ScreenIntelligence()
        return self._screen

    @screen.setter
    def screen(self, val: ScreenIntelligence):
        self._screen = val

    @property
    def files(self) -> FileIntelligence:
        if self._files is None:
            self._files = FileIntelligence()
        return self._files

    @files.setter
    def files(self, val: FileIntelligence):
        self._files = val

    @property
    def research(self) -> ResearchEngine:
        if self._research is None:
            self._research = ResearchEngine()
        return self._research

    @research.setter
    def research(self, val: ResearchEngine):
        self._research = val

    @property
    def voice(self) -> VoicePipeline:
        if self._voice is None:
            self._voice = VoicePipeline()
        return self._voice

    @voice.setter
    def voice(self, val: VoicePipeline):
        self._voice = val

    def dispatch(self, method: str, params: Dict[str, Any]) -> Any:
        """Dispatches a JSON-RPC method call to the appropriate internal handler."""
        handler_map = {
            "ping": self._handle_ping,
            "chat": self._handle_chat,
            "emergency_stop": self._handle_emergency_stop,
            "get_identity": self._handle_get_identity,
            "update_identity": self._handle_update_identity,
            "list_providers": self._handle_list_providers,
            "set_provider": self._handle_set_provider,
            "list_sessions": self._handle_list_sessions,
            "get_messages": self._handle_get_messages,
            "clear_messages": self._handle_clear_messages,
            "delete_session": self._handle_delete_session,
            # Phase 7 Action Planning & Execution
            "plan_action": self._handle_plan_action,
            "execute_plan": self._handle_execute_plan,
            "abort_plan": self._handle_abort_plan,
            # Phase 7 Intelligence & Diagnostics
            "screen_analyze": self._handle_screen_analyze,
            "file_search": self._handle_file_search,
            "file_summarize": self._handle_file_summarize,
            "log_parse": self._handle_log_parse,
            # Phase 7 Memory & Web Research
            "remember": self._handle_remember,
            "recall": self._handle_recall,
            "list_memories": self._handle_list_memories,
            "forget": self._handle_forget,
            "clear_memories": self._handle_clear_memories,
            "web_research": self._handle_web_research,
            "speak": self._handle_speak,
            # Phase 8: Multilingual Engine Handlers
            "detect_language": self._handle_detect_language,
            "get_language_config": self._handle_get_language_config,
            "update_language_config": self._handle_update_language_config,
        }

        if method not in handler_map:
            raise KeyError(f"Method '{method}' not found")

        return handler_map[method](params)

    # -------------------------------------------------------------------------
    # JSON-RPC Handlers
    # -------------------------------------------------------------------------
    def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        uptime_sec = round(time.time() - self.start_time, 1)
        active_provider_name = self.identity.get_provider()
        provider = self.providers.get_provider(active_provider_name)

        return {
            "status": "online",
            "name": self.identity.get_display_name(),
            "avatar": self.identity.get_avatar(),
            "uptime_seconds": uptime_sec,
            "active_provider": provider.name,
            "active_model": self.identity.get_model(),
            "provider_configured": provider.is_configured(),
            "version": "1.0.0",
        }

    def _handle_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_message = params.get("message", "").strip()
        if not user_message:
            raise ValueError("Message parameter cannot be empty")

        session_id = params.get("session_id") or self.store.get_or_create_default_session()
        provider_name = params.get("provider") or self.identity.get_provider()
        provider = self.providers.get_provider(provider_name)
        model_name = params.get("model") or self.identity.get_model()

        # 1. Store user message
        self.store.add_message(session_id, role="user", content=user_message)

        # 2. Retrieve recent conversation context
        context = self.store.get_recent_context(session_id, limit=8)

        # 3. Build system prompt & Multilingual Directives
        lang_directive = self.lang_router.build_system_prompt_instruction(user_message)
        system_prompt = self.identity.get_system_prompt() + lang_directive
        eff_comb, lang_prof = self.lang_router.resolve_effective_combination(user_message)

        # 4. Check for Action Planning & Autonomous Tools
        self._abort_flag.clear()
        lower_msg = user_message.lower()

        # Check for Web Research Request
        if lower_msg.startswith(("search web for ", "search the web for ", "google ")):
            res_data = self.research.search_and_synthesize(user_message)
            reply_text = res_data["synthesis_markdown"]

        # Check for Screen Intelligence Request
        elif any(phrase in lower_msg for phrase in ["analyze screen", "what is on my screen", "diagnose screen", "read my screen"]):
            screen_res = self.screen.analyze_screen()
            reply_text = f"### 󰹑 Screen Analysis\n\n{screen_res['findings']}\n\n**Suggestions:**\n" + "\n".join(f"- {s}" for s in screen_res["suggestions"])

        # Check for Memory Intent ("remember that X is Y" or "remember X: Y")
        elif lower_msg.startswith("remember ") and (" is " in lower_msg or ":" in lower_msg):
            clean = user_message[9:].strip()
            if " is " in clean:
                parts = clean.split(" is ", 1)
            else:
                parts = clean.split(":", 1)
            k, v = parts[0].strip(), parts[1].strip()
            ok, err = self.memory.remember(k, v)
            if ok:
                reply_text = f"󰚔 I have saved that to personal memory:\n> **{k}**: {v}"
            else:
                reply_text = f"⚠️ Could not save memory: {err}"

        # Check for Action Execution Intent (e.g. "switch to workspace 2", "open kitty", "set volume to 60%")
        else:
            plan = self.planner.parse_natural_intent(user_message)
            if plan.steps:
                if not plan.requires_confirmation:
                    # Low risk: execute immediately
                    self.executor.execute_plan(plan, user_approved=True)
                    reply_text = f"### 󰚣 Action Executed\n\n**Goal:** *\"{plan.goal}\"*\n\n"
                    for step in plan.steps:
                        status_icon = "󰄲" if step.status == "success" else "󰅖"
                        reply_text += f"- {status_icon} **{step.primitive}**: {step.description}\n"
                else:
                    # Medium/High risk: generate confirmation request
                    reply_text = f"### 󰀦 Action Plan Requires Confirmation\n\n**Goal:** *\"{plan.goal}\"*\n\n"
                    for step in plan.steps:
                        reply_text += f"- [ ] **{step.primitive}** *({step.risk_level.value.upper()})*: {step.description}\n"
                    reply_text += "\n*Please confirm in the assistant window or click 'Approve & Run'.*"
            else:
                # Standard Multi-turn LLM generation
                try:
                    raw_response = provider.chat(
                        messages=context,
                        model=model_name,
                        system_prompt=system_prompt,
                        stream=False,
                    )
                    reply_text = str(raw_response)
                except Exception as e:
                    reply_text = (
                        f"I encountered an issue generating a response with {provider.display_name}: {str(e)}\n\n"
                        "Please verify your connection and API configuration in Settings."
                    )

        # If user pressed emergency stop during generation
        if self._abort_flag.is_set():
            reply_text += "\n\n*[Generation aborted by user]*"

        # 5. Store assistant message
        msg_id = self.store.add_message(
            session_id,
            role="assistant",
            content=reply_text,
            metadata={"provider": provider.name, "model": model_name},
        )

        return {
            "session_id": session_id,
            "message_id": msg_id,
            "role": "assistant",
            "content": reply_text,
            "provider": provider.name,
            "model": model_name,
            "language": lang_prof.primary_language,
            "combination": eff_comb,
            "timestamp": datetime.now().isoformat(),
        }

    def _handle_emergency_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._abort_flag.set()
        return {"status": "aborted", "timestamp": datetime.now().isoformat()}

    def _handle_get_identity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.identity.get_config()

    def _handle_update_identity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        success = self.identity.update_config(params)
        return {"success": success, "config": self.identity.get_config()}

    def _handle_list_providers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "active_provider": self.identity.get_provider(),
            "active_model": self.identity.get_model(),
            "providers": self.providers.list_providers(),
        }

    def _handle_set_provider(self, params: Dict[str, Any]) -> Dict[str, Any]:
        provider_name = params.get("provider", "")
        model_name = params.get("model")
        success = self.identity.set_provider(provider_name, model_name)
        return {"success": success, "active_provider": provider_name, "active_model": model_name}

    def _handle_list_sessions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        limit = params.get("limit", 20)
        sessions = self.store.list_sessions(limit=limit)
        return {"sessions": sessions}

    def _handle_get_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = params.get("session_id") or self.store.get_or_create_default_session()
        messages = self.store.get_messages(session_id, limit=params.get("limit", 100))
        return {"session_id": session_id, "messages": messages}

    def _handle_clear_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = params.get("session_id")
        if session_id:
            self.store.delete_session(session_id)
            new_id = self.store.create_session(session_id=session_id)
        else:
            self.store.clear_all_sessions()
            new_id = self.store.get_or_create_default_session()
        return {"success": True, "session_id": new_id}

    def _handle_delete_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = params.get("session_id", "")
        success = self.store.delete_session(session_id)
        return {"success": success}

    # -------------------------------------------------------------------------
    # Phase 7: Automation & Advanced Intelligence Handlers
    # -------------------------------------------------------------------------
    def _handle_plan_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        goal = params.get("goal") or params.get("text", "")
        plan = self.planner.parse_natural_intent(goal)
        return plan.to_dict()

    def _handle_execute_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        plan_data = params.get("plan", {})
        user_approved = bool(params.get("user_approved", False))
        valid, plan, err = self.planner.create_plan_from_json(plan_data)
        if not valid:
            return {"success": False, "error": err, "plan": plan.to_dict()}
        executed = self.executor.execute_plan(plan, user_approved=user_approved)
        return {"success": executed.status == "completed", "plan": executed.to_dict()}

    def _handle_abort_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self.executor.abort()
        self._abort_flag.set()
        return {"status": "aborted"}

    def _handle_screen_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prompt = params.get("prompt")
        image_path = params.get("image_path")
        return self.screen.analyze_screen(image_path=image_path, user_prompt=prompt)

    def _handle_file_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        search_dir = params.get("dir")
        results = self.files.search_files(query=query, search_dir=search_dir)
        return {"results": results}

    def _handle_file_summarize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = params.get("path", "")
        return self.files.summarize_code(path)

    def _handle_log_parse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = params.get("path")
        return self.files.parse_recent_logs(log_path=path)

    def _handle_remember(self, params: Dict[str, Any]) -> Dict[str, Any]:
        key = params.get("key", "")
        value = params.get("value", "")
        cat = params.get("category", "general")
        success, err = self.memory.remember(key, value, category=cat)
        return {"success": success, "error": err}

    def _handle_recall(self, params: Dict[str, Any]) -> Dict[str, Any]:
        key = params.get("key", "")
        val = self.memory.recall(key)
        return {"key": key, "value": val}

    def _handle_list_memories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cat = params.get("category")
        return {"memories": self.memory.list_memories(category=cat)}

    def _handle_forget(self, params: Dict[str, Any]) -> Dict[str, Any]:
        key = params.get("key", "")
        return {"success": self.memory.forget(key)}

    def _handle_clear_memories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": self.memory.clear_memories()}

    def _handle_web_research(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        return self.research.search_and_synthesize(query)

    def _handle_speak(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get("text", "")
        voice = params.get("voice")
        return {"success": self.voice.speak(text, voice=voice)}

    def _handle_detect_language(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get("text", "")
        profile = self.lang_router.detector.analyze(text)
        return {
            "primary_language": profile.primary_language,
            "combination": profile.combination,
            "script": profile.script,
            "is_code_switched": profile.is_code_switched,
            "languages_present": profile.languages_present,
            "details": profile.details,
        }

    def _handle_get_language_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.lang_router.get_config()

    def _handle_update_language_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ok = self.lang_router.update_config(params)
        return {"success": ok, "config": self.lang_router.get_config()}

    # -------------------------------------------------------------------------
    # Connection & Request Processing
    # -------------------------------------------------------------------------
    def _process_client_connection(self, conn: socket.socket):
        try:
            conn.settimeout(30.0)
            data_buf = b""
            while self._running:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data_buf += chunk
                if b"\n" in data_buf:
                    lines = data_buf.split(b"\n")
                    data_buf = lines[-1]
                    for line in lines[:-1]:
                        if not line.strip():
                            continue
                        response = self._process_request_line(line.decode("utf-8"))
                        conn.sendall((response + "\n").encode("utf-8"))
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _process_request_line(self, line: str) -> str:
        req_id = None
        try:
            req_data = json.loads(line)
            req_id = req_data.get("id", 1)
            method = req_data.get("method")
            params = req_data.get("params", {})

            if not method:
                return JsonRpcResponse.error_response(
                    req_id, INVALID_REQUEST, "Missing 'method' field in JSON-RPC request"
                ).to_json()

            result = self.dispatch(method, params)
            return JsonRpcResponse.success(req_id, result).to_json()

        except json.JSONDecodeError as e:
            return JsonRpcResponse.error_response(req_id, -32700, f"Parse error: {e}").to_json()
        except KeyError as e:
            return JsonRpcResponse.error_response(req_id, METHOD_NOT_FOUND, str(e)).to_json()
        except ValueError as e:
            return JsonRpcResponse.error_response(req_id, INVALID_PARAMS, str(e)).to_json()
        except Exception as e:
            return JsonRpcResponse.error_response(req_id, INTERNAL_ERROR, f"Internal error: {e}").to_json()

    # -------------------------------------------------------------------------
    # Server Listeners
    # -------------------------------------------------------------------------
    def _run_unix_socket_server(self):
        if not hasattr(socket, "AF_UNIX") or sys.platform == "win32":
            return

        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except Exception:
                pass

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.socket_path)
        sock.listen(10)
        sock.settimeout(1.0)

        while self._running:
            try:
                conn, _ = sock.accept()
                t = threading.Thread(target=self._process_client_connection, args=(conn,), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception:
                break

        sock.close()
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except Exception:
                pass

    def _run_tcp_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", self.tcp_port))
            sock.listen(10)
            sock.settimeout(1.0)
        except Exception as e:
            print(f"[JuneDaemon] TCP server could not bind to port {self.tcp_port}: {e}", file=sys.stderr)
            return

        while self._running:
            try:
                conn, _ = sock.accept()
                t = threading.Thread(target=self._process_client_connection, args=(conn,), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception:
                break

        sock.close()

    def start(self, block: bool = True):
        """Starts the daemon servers."""
        self._running = True
        print(f"[JuneDaemon] Starting June AI core daemon (Name: {self.identity.get_display_name()})...")

        # Start UNIX socket listener if on UNIX
        if hasattr(socket, "AF_UNIX") and sys.platform != "win32":
            unix_t = threading.Thread(target=self._run_unix_socket_server, daemon=True)
            unix_t.start()
            self._server_threads.append(unix_t)
            print(f"[JuneDaemon] Listening on UNIX socket: {self.socket_path}")

        # Start TCP listener as cross-platform fallback
        tcp_t = threading.Thread(target=self._run_tcp_server, daemon=True)
        tcp_t.start()
        self._server_threads.append(tcp_t)
        print(f"[JuneDaemon] Listening on TCP fallback: 127.0.0.1:{self.tcp_port}")

        if block:
            try:
                while self._running:
                    time.sleep(1.0)
            except (KeyboardInterrupt, SystemExit):
                self.stop()

    def stop(self):
        """Stops the daemon."""
        print("[JuneDaemon] Stopping daemon...")
        self._running = False
        for t in self._server_threads:
            t.join(timeout=1.0)
        print("[JuneDaemon] Daemon stopped cleanly.")


def main():
    parser = argparse.ArgumentParser(description="June AI Assistant Core Daemon")
    parser.add_argument("--socket", type=str, help="Custom socket path")
    parser.add_argument("--port", type=int, default=DEFAULT_TCP_PORT, help="Custom TCP fallback port")
    parser.add_argument("--foreground", action="store_true", help="Run in foreground (default)")
    parser.add_argument("--status", action="store_true", help="Query status of running daemon")
    parser.add_argument("--stop", action="store_true", help="Stop running daemon")

    args = parser.parse_args()

    daemon = JuneDaemon(socket_path=args.socket, tcp_port=args.port)
    daemon.start(block=True)


if __name__ == "__main__":
    main()
