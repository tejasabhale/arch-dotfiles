#!/usr/bin/env python3
"""
June AI Command-Line Interface.
Fish abbreviation: `june` -> `python3 -m assistant.core.cli`
Enables quick terminal questions, status inspection, and JSON outputs for Quickshell.
"""

import argparse
import json
import sys

# Configure UTF-8 stdout if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from assistant.core.client import JuneClient


def main():
    parser = argparse.ArgumentParser(
        description="June Personal AI Desktop Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  june "What is the keybinding for the application launcher?"
  june --chat "Explain system memory usage" --json
  june --history
  june --providers
  june --set-name "Krupa"
  june --clear
  june --ping
""",
    )

    parser.add_argument("prompt", nargs="?", help="Direct question or prompt to send to June")
    parser.add_argument("-c", "--chat", type=str, help="Chat message to send")
    parser.add_argument("-j", "--json", action="store_true", help="Output raw JSON for scripts and UI")
    parser.add_argument("--session", type=str, help="Target conversation session ID")
    parser.add_argument("--history", action="store_true", help="Print conversation history")
    parser.add_argument("--sessions", action="store_true", help="List all chat sessions")
    parser.add_argument("--providers", action="store_true", help="List AI providers and status")
    parser.add_argument("--identity", action="store_true", help="Show current assistant identity settings")
    parser.add_argument("--set-name", type=str, help="Change assistant display name")
    parser.add_argument("--clear", action="store_true", help="Clear chat session messages")
    parser.add_argument("--stop", action="store_true", help="Emergency stop active generation")
    parser.add_argument("--ping", action="store_true", help="Ping June daemon / service")
    parser.add_argument("--plan", type=str, help="Construct an ActionPlan AST from intent")
    parser.add_argument("--screen", action="store_true", help="Diagnose active screen content")
    parser.add_argument("--research", type=str, help="Autonomous web research and citations")
    parser.add_argument("--remember", type=str, help="Store memory key:value")
    parser.add_argument("--recall", type=str, help="Recall value for memory key")
    parser.add_argument("--memories", action="store_true", help="List all stored personal memories")
    parser.add_argument("--detect-lang", type=str, help="Context-aware language & code-switching detection")
    parser.add_argument("--languages", action="store_true", help="Show active multilingual engine configuration")

    args = parser.parse_args()
    client = JuneClient()

    # 1. Ping
    if args.ping:
        res = client.ping()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Status: {res.get('status')} | Name: {res.get('name')} | Provider: {res.get('active_provider')} ({res.get('active_model')})")
        return

    # 2. Set Name
    if args.set_name:
        res = client.set_name(args.set_name)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Assistant display name updated to '{args.set_name}'.")
        return

    # 3. Identity
    if args.identity:
        res = client.get_identity()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Name: {res.get('name')} {res.get('avatar')}")
            print(f"Personality: {res.get('personality')}")
            print(f"Provider: {res.get('provider')} ({res.get('model')})")
        return

    # 4. Providers
    if args.providers:
        res = client.list_providers()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Active Provider: {res.get('active_provider')} ({res.get('active_model')})\n")
            print("Available Providers:")
            for p in res.get("providers", []):
                cfg_str = "[Ready]" if p.get("configured") else "[Unconfigured]"
                loc_str = "(Local)" if p.get("is_local") else "(Cloud)"
                print(f"  • {p.get('id'):<12} {cfg_str:<15} {loc_str:<8} Models: {', '.join(p.get('models', [])[:3])}")
        return

    # 5. Clear
    if args.clear:
        success = client.clear(session_id=args.session)
        if args.json:
            print(json.dumps({"success": success}))
        else:
            print("Chat history cleared.")
        return

    # 6. Stop
    if args.stop:
        res = client.emergency_stop()
        if args.json:
            print(json.dumps(res))
        else:
            print("Emergency stop signal dispatched.")
        return

    # 7. Sessions
    if args.sessions:
        sessions = client.list_sessions()
        if args.json:
            print(json.dumps(sessions, indent=2))
        else:
            print("Conversation Sessions:")
            for s in sessions:
                print(f"  [{s.get('id')}] {s.get('title')} ({s.get('updated_at')[:10]})")
        return

    # 8. History
    if args.history:
        messages = client.get_messages(session_id=args.session)
        if args.json:
            print(json.dumps(messages, indent=2))
        else:
            name = client.ping().get("name", "June")
            for m in messages:
                speaker = "User" if m["role"] == "user" else name
                print(f"\n[{speaker} - {m['timestamp'][:16]}]:\n{m['content']}")
        return

    # 9. Action Plan
    if args.plan:
        plan = client.plan_action(args.plan)
        if args.json:
            print(json.dumps(plan, indent=2))
        else:
            print(f"Goal: {plan.get('goal')}")
            print(f"Requires Confirmation: {plan.get('requires_confirmation')}")
            print("Steps:")
            for s in plan.get("steps", []):
                print(f"  [{s.get('risk_level').upper()}] {s.get('primitive')}: {s.get('description')}")
        return

    # 10. Screen Diagnostics
    if args.screen:
        diag = client.screen_analyze()
        if args.json:
            print(json.dumps(diag, indent=2))
        else:
            print(f"Screen Analysis ({diag.get('window_title')} - {diag.get('window_class')}):")
            print(diag.get("findings"))
            print("Suggestions:")
            for s in diag.get("suggestions", []):
                print(f"  • {s}")
        return

    # 11. Web Research
    if args.research:
        res = client.web_research(args.research)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res.get("synthesis_markdown", ""))
        return

    # 12. Remember & Recall
    if args.remember:
        if ":" in args.remember:
            k, v = args.remember.split(":", 1)
        else:
            k, v = args.remember, "true"
        ret = client.remember(k.strip(), v.strip())
        if args.json:
            print(json.dumps(ret, indent=2))
        else:
            if ret.get("success"):
                print(f"Remembered: '{k.strip()}' -> '{v.strip()}'")
            else:
                print(f"Error: {ret.get('error')}")
        return

    if args.recall:
        val = client.recall(args.recall)
        if args.json:
            print(json.dumps({"key": args.recall, "value": val}))
        else:
            print(f"Recall: '{args.recall}' -> {val}")
        return

    if args.memories:
        mems = client.list_memories()
        if args.json:
            print(json.dumps(mems, indent=2))
        else:
            print("Stored Personal Memories:")
            for m in mems:
                print(f"  • [{m.get('category')}] {m.get('key')}: {m.get('value')} ({m.get('updated_at')[:10]})")
        return

    # 13. Multilingual Diagnostics
    if args.detect_lang:
        res = client.detect_language(args.detect_lang)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Primary: {res.get('primary_language')} | Combination: {res.get('combination')} | Script: {res.get('script')}")
            print(f"Code-Switched: {res.get('is_code_switched')} | Languages Present: {res.get('languages_present')}")
        return

    if args.languages:
        cfg = client.get_language_config()
        if args.json:
            print(json.dumps(cfg, indent=2))
        else:
            print("Multilingual Configuration:")
            print(f"  • Preferred Combination: {cfg.get('preferred_combination')}")
            print(f"  • Script Mode: {cfg.get('script_mode')}")
            print(f"  • Code-Switching Enabled: {cfg.get('code_switching_enabled')}")
        return

    # 14. Prompt or Chat Message
    prompt_text = args.chat or args.prompt
    if prompt_text:
        res = client.chat(prompt_text, session_id=args.session)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res.get("content", ""))
        return

    # If no arguments provided, show brief status
    status = client.ping()
    print(f"June AI ({status.get('name')}) is ready.")
    print("Run 'june --help' or 'june \"<question>\"' to interact.")


if __name__ == "__main__":
    main()
