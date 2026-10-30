#!/usr/bin/env python3
"""
June AI Client Library.
Provides both IPC socket client connectivity and in-process standalone fallback
for interacting with June.
"""

import json
from typing import Any, Dict, List, Optional

from assistant.core.identity import IdentityManager
from assistant.core.ipc import send_ipc_message
from assistant.memory.conversation_store import ConversationStore
from assistant.providers.registry import ProviderRegistry


class JuneClient:
    """Client for June AI Assistant with IPC and direct-execution fallback."""

    def __init__(self, socket_path: Optional[str] = None):
        self.socket_path = socket_path

    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Attempts IPC call; if daemon is offline, falls back to in-process execution."""
        res = send_ipc_message(method=method, params=params or {}, socket_path=self.socket_path, timeout=5.0)
        if "result" in res:
            return res["result"]

        # In-process standalone fallback if daemon is not running
        return self._direct_dispatch(method, params or {})

    def _direct_dispatch(self, method: str, params: Dict[str, Any]) -> Any:
        identity = IdentityManager()
        store = ConversationStore()
        providers = ProviderRegistry()

        if method == "ping":
            p = providers.get_provider(identity.get_provider())
            return {
                "status": "in-process",
                "name": identity.get_display_name(),
                "avatar": identity.get_avatar(),
                "uptime_seconds": 0.0,
                "active_provider": p.name,
                "active_model": identity.get_model(),
                "provider_configured": p.is_configured(),
                "version": "1.0.0",
            }

        elif method == "chat":
            msg = params.get("message", "").strip()
            session_id = params.get("session_id") or store.get_or_create_default_session()
            provider_name = params.get("provider") or identity.get_provider()
            p = providers.get_provider(provider_name)
            model_name = params.get("model") or identity.get_model()

            store.add_message(session_id, role="user", content=msg)
            context = store.get_recent_context(session_id, limit=8)
            sys_prompt = identity.get_system_prompt()

            try:
                reply = p.chat(context, model=model_name, system_prompt=sys_prompt, stream=False)
            except Exception as e:
                reply = f"Error in {p.display_name}: {e}"

            store.add_message(session_id, role="assistant", content=str(reply))
            return {
                "session_id": session_id,
                "role": "assistant",
                "content": str(reply),
                "provider": p.name,
                "model": model_name,
            }

        elif method == "get_identity":
            return identity.get_config()

        elif method == "update_identity":
            identity.update_config(params)
            return {"success": True, "config": identity.get_config()}

        elif method == "list_providers":
            return {
                "active_provider": identity.get_provider(),
                "active_model": identity.get_model(),
                "providers": providers.list_providers(),
            }

        elif method == "list_sessions":
            return {"sessions": store.list_sessions(limit=params.get("limit", 20))}

        elif method == "get_messages":
            sid = params.get("session_id") or store.get_or_create_default_session()
            return {"session_id": sid, "messages": store.get_messages(sid)}

        elif method == "clear_messages":
            sid = params.get("session_id")
            if sid:
                store.delete_session(sid)
                new_sid = store.create_session(session_id=sid)
            else:
                store.clear_all_sessions()
                new_sid = store.get_or_create_default_session()
            return {"success": True, "session_id": new_sid}

        elif method == "emergency_stop":
            return {"status": "aborted"}

        elif method == "plan_action":
            from assistant.action_planner import ActionPlanner
            planner = ActionPlanner()
            goal = params.get("goal") or params.get("text", "")
            return planner.parse_natural_intent(goal).to_dict()

        elif method == "execute_plan":
            from assistant.action_planner import ActionPlanner
            from assistant.executor import ControlledExecutor
            planner = ActionPlanner()
            executor = ControlledExecutor()
            plan_data = params.get("plan", {})
            user_approved = bool(params.get("user_approved", False))
            valid, plan, err = planner.create_plan_from_json(plan_data)
            if not valid:
                return {"success": False, "error": err, "plan": plan.to_dict()}
            executed = executor.execute_plan(plan, user_approved=user_approved)
            return {"success": executed.status == "completed", "plan": executed.to_dict()}

        elif method == "screen_analyze":
            from assistant.screen_intelligence import ScreenIntelligence
            screen = ScreenIntelligence()
            return screen.analyze_screen(user_prompt=params.get("prompt"))

        elif method == "file_search":
            from assistant.file_intelligence import FileIntelligence
            files = FileIntelligence()
            return {"results": files.search_files(params.get("query", ""), search_dir=params.get("dir"))}

        elif method == "remember":
            from assistant.memory import MemoryManager
            mem = MemoryManager()
            ok, err = mem.remember(params.get("key", ""), params.get("value", ""), category=params.get("category", "general"))
            return {"success": ok, "error": err}

        elif method == "recall":
            from assistant.memory import MemoryManager
            mem = MemoryManager()
            return {"key": params.get("key", ""), "value": mem.recall(params.get("key", ""))}

        elif method == "list_memories":
            from assistant.memory import MemoryManager
            mem = MemoryManager()
            return {"memories": mem.list_memories(category=params.get("category"))}

        elif method == "forget":
            from assistant.memory import MemoryManager
            mem = MemoryManager()
            return {"success": mem.forget(params.get("key", ""))}

        elif method == "web_research":
            from assistant.research import ResearchEngine
            res = ResearchEngine()
            return res.search_and_synthesize(params.get("query", ""))

        elif method == "detect_language":
            from assistant.languages.detector import MultilingualDetector
            d = MultilingualDetector()
            profile = d.analyze(params.get("text", ""))
            return {
                "primary_language": profile.primary_language,
                "combination": profile.combination,
                "script": profile.script,
                "is_code_switched": profile.is_code_switched,
                "languages_present": profile.languages_present,
                "details": profile.details,
            }

        elif method == "get_language_config":
            from assistant.languages.router import LanguageRouter
            return LanguageRouter().get_config()

        elif method == "update_language_config":
            from assistant.languages.router import LanguageRouter
            r = LanguageRouter()
            ok = r.update_config(params)
            return {"success": ok, "config": r.get_config()}

        return {"error": f"Method {method} not handled in fallback"}

    def ping(self) -> Dict[str, Any]:
        return self._call("ping")

    def chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        return self._call("chat", {"message": message, "session_id": session_id})

    def get_identity(self) -> Dict[str, Any]:
        return self._call("get_identity")

    def set_name(self, name: str) -> Dict[str, Any]:
        return self._call("update_identity", {"name": name})

    def list_providers(self) -> Dict[str, Any]:
        return self._call("list_providers")

    def list_sessions(self) -> List[Dict[str, Any]]:
        res = self._call("list_sessions")
        return res.get("sessions", [])

    def get_messages(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        res = self._call("get_messages", {"session_id": session_id})
        return res.get("messages", [])

    def clear(self, session_id: Optional[str] = None) -> bool:
        res = self._call("clear_messages", {"session_id": session_id})
        return res.get("success", False)

    def emergency_stop(self) -> Dict[str, Any]:
        return self._call("emergency_stop")

    def plan_action(self, goal: str) -> Dict[str, Any]:
        return self._call("plan_action", {"goal": goal})

    def execute_plan(self, plan: Dict[str, Any], user_approved: bool = False) -> Dict[str, Any]:
        return self._call("execute_plan", {"plan": plan, "user_approved": user_approved})

    def screen_analyze(self, prompt: Optional[str] = None) -> Dict[str, Any]:
        return self._call("screen_analyze", {"prompt": prompt})

    def search_files(self, query: str, search_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        res = self._call("file_search", {"query": query, "dir": search_dir})
        return res.get("results", [])

    def remember(self, key: str, value: str, category: str = "general") -> Dict[str, Any]:
        return self._call("remember", {"key": key, "value": value, "category": category})

    def recall(self, key: str) -> Optional[str]:
        res = self._call("recall", {"key": key})
        return res.get("value")

    def list_memories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        res = self._call("list_memories", {"category": category})
        return res.get("memories", [])

    def forget(self, key: str) -> bool:
        res = self._call("forget", {"key": key})
        return res.get("success", False)

    def web_research(self, query: str) -> Dict[str, Any]:
        return self._call("web_research", {"query": query})

    def detect_language(self, text: str) -> Dict[str, Any]:
        return self._call("detect_language", {"text": text})

    def get_language_config(self) -> Dict[str, Any]:
        return self._call("get_language_config")

    def set_language_combination(self, combination: str) -> Dict[str, Any]:
        return self._call("update_language_config", {"preferred_combination": combination})
