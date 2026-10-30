"""
Automated Unit Tests for June AI Advanced Intelligence & Automation (Phase 7).
Verifies PermissionEngine, ActionPlanner, ControlledExecutor, ScreenIntelligence,
FileIntelligence, MemoryManager, ResearchEngine, VoicePipeline, and Daemon Integration.
"""

import json
import os
import shutil
import tempfile
import unittest

from assistant.action_planner import ActionPlan, ActionPlanner, ActionStep, RiskLevel
from assistant.core.daemon import JuneDaemon
from assistant.executor import ControlledExecutor
from assistant.file_intelligence import FileIntelligence
from assistant.memory import MemoryManager
from assistant.permissions import PermissionEngine
from assistant.research import ResearchEngine
from assistant.screen_intelligence import ScreenIntelligence
from assistant.voice import VoicePipeline


class TestAssistantAutomation(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="june_automation_test_")
        self.memory_db = os.path.join(self.test_dir, "test_memory.db")
        self.conv_db = os.path.join(self.test_dir, "test_conv.db")
        self.config_path = os.path.join(self.test_dir, "assistant.json")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Permission Engine & Security Guardrails Tests (Rule 1.5 & Rule 2.2)
    # -------------------------------------------------------------------------
    def test_permission_engine_allowlist_and_risk(self):
        pe = PermissionEngine()

        # Low risk primitive
        step_low = ActionStep(primitive="workspace.switch", params={"workspace_id": 3})
        valid, risk, err = pe.validate_step(step_low)
        self.assertTrue(valid)
        self.assertEqual(risk, RiskLevel.LOW)

        # Medium risk primitive
        step_med = ActionStep(primitive="hotspot.toggle", params={"enable": True})
        valid, risk, err = pe.validate_step(step_med)
        self.assertTrue(valid)
        self.assertEqual(risk, RiskLevel.MEDIUM)

        # Blocked / unknown primitive
        step_unknown = ActionStep(primitive="system.hack", params={})
        valid, risk, err = pe.validate_step(step_unknown)
        self.assertFalse(valid)
        self.assertEqual(risk, RiskLevel.BLOCKED)

    def test_permission_engine_destructive_guardrails(self):
        pe = PermissionEngine()

        # Disk formatting attempt
        step_bad1 = ActionStep(primitive="app.launch", params={"app": "kitty", "extra": "mkfs.ext4 /dev/sda1"})
        valid, risk, err = pe.validate_step(step_bad1)
        self.assertFalse(valid)
        self.assertEqual(risk, RiskLevel.BLOCKED)
        self.assertIn("forbidden", str(err).lower())

        # Windows EFI partition attempt
        step_bad2 = ActionStep(primitive="file.read_scoped", params={"path": "/boot/efi/EFI/Microsoft/Boot/bootmgfw.efi"})
        valid, risk, err = pe.validate_step(step_bad2)
        self.assertFalse(valid)
        self.assertEqual(risk, RiskLevel.BLOCKED)

    # -------------------------------------------------------------------------
    # 2. Action Planner Tests
    # -------------------------------------------------------------------------
    def test_action_planner_natural_intent_parsing(self):
        planner = ActionPlanner()

        # Single action: workspace switch
        plan1 = planner.parse_natural_intent("switch to workspace 4")
        self.assertEqual(len(plan1.steps), 1)
        self.assertEqual(plan1.steps[0].primitive, "workspace.switch")
        self.assertEqual(plan1.steps[0].params["workspace_id"], 4)
        self.assertFalse(plan1.requires_confirmation)

        # Multi-step action: workspace + app launch
        plan2 = planner.parse_natural_intent("switch to workspace 2 and open kitty")
        self.assertEqual(len(plan2.steps), 2)
        self.assertEqual(plan2.steps[0].primitive, "workspace.switch")
        self.assertEqual(plan2.steps[1].primitive, "app.launch")
        self.assertFalse(plan2.requires_confirmation)

        # State modifying action requiring confirmation: hotspot
        plan3 = planner.parse_natural_intent("turn on wifi hotspot")
        self.assertEqual(len(plan3.steps), 1)
        self.assertEqual(plan3.steps[0].primitive, "hotspot.toggle")
        self.assertTrue(plan3.requires_confirmation)

    def test_action_planner_json_ast(self):
        planner = ActionPlanner()
        raw_json = json.dumps({
            "goal": "Prepare coding workspace",
            "steps": [
                {"primitive": "workspace.switch", "params": {"workspace_id": 1}},
                {"primitive": "app.launch", "params": {"app": "code"}},
                {"primitive": "audio.set_volume", "params": {"volume": 0.5}}
            ]
        })
        valid, plan, err = planner.create_plan_from_json(raw_json)
        self.assertTrue(valid)
        self.assertEqual(len(plan.steps), 3)
        self.assertEqual(plan.status, "approved")

    # -------------------------------------------------------------------------
    # 3. Controlled Executor & Emergency Stop Tests
    # -------------------------------------------------------------------------
    def test_controlled_executor_safe_execution(self):
        executor = ControlledExecutor()

        plan = ActionPlan(goal="Test Low Risk Execution")
        plan.steps = [
            ActionStep(primitive="workspace.switch", params={"workspace_id": 1}),
            ActionStep(primitive="clipboard.copy", params={"text": "Test snippet"}),
        ]

        executed = executor.execute_plan(plan, user_approved=False)
        self.assertEqual(executed.status, "completed")
        self.assertEqual(executed.steps[0].status, "success")
        self.assertEqual(executed.steps[1].status, "success")

    def test_controlled_executor_requires_approval(self):
        executor = ControlledExecutor()

        plan = ActionPlan(goal="Modify system power")
        plan.steps = [
            ActionStep(primitive="power.set_profile", params={"profile": "performance"}, risk_level=RiskLevel.MEDIUM)
        ]
        plan.requires_confirmation = True

        # Attempt to run without user approval
        executed = executor.execute_plan(plan, user_approved=False)
        self.assertEqual(executed.status, "pending_approval")
        self.assertEqual(executed.steps[0].status, "pending")

        # Now approve
        executed_approved = executor.execute_plan(plan, user_approved=True)
        self.assertEqual(executed_approved.status, "completed")

    def test_controlled_executor_emergency_stop(self):
        executor = ControlledExecutor()

        plan = ActionPlan(goal="Aborted plan")
        plan.steps = [
            ActionStep(primitive="clipboard.copy", params={"text": "First"}),
            ActionStep(primitive="clipboard.copy", params={"text": "Second"}),
        ]

        # Trigger emergency stop before running
        executor.abort()
        self.assertTrue(executor.is_aborted())

        executed = executor.execute_plan(plan, user_approved=True)
        self.assertEqual(executed.status, "aborted")

    # -------------------------------------------------------------------------
    # 4. Screen Intelligence Tests
    # -------------------------------------------------------------------------
    def test_screen_intelligence_analysis(self):
        si = ScreenIntelligence()
        # Diagnostic analysis with mock capture
        diag = si.analyze_screen(user_prompt="Inspect active windows")
        self.assertIn("timestamp", diag)
        self.assertIn("findings", diag)
        self.assertIsInstance(diag["suggestions"], list)
        self.assertGreater(len(diag["suggestions"]), 0)

    # -------------------------------------------------------------------------
    # 5. Scoped File Intelligence Tests
    # -------------------------------------------------------------------------
    def test_file_intelligence_boundary_and_summary(self):
        fi = FileIntelligence()

        # Path within current workspace is safe
        safe, err = fi.is_path_safe("tests/test_assistant_automation.py")
        self.assertTrue(safe)

        # Sensitive paths are blocked
        safe_ssh, err_ssh = fi.is_path_safe("~/.ssh/id_rsa")
        self.assertFalse(safe_ssh)

        safe_env, err_env = fi.is_path_safe(".env")
        self.assertFalse(safe_env)

        # Summarize this test file
        summary = fi.summarize_code("tests/test_assistant_automation.py")
        self.assertIn("total_lines", summary)
        self.assertGreater(summary["total_lines"], 10)
        self.assertGreater(summary["class_count"], 0)

    # -------------------------------------------------------------------------
    # 6. Personal Memory Tests & Credential Sanitization (Rule 2.2)
    # -------------------------------------------------------------------------
    def test_memory_manager_crud_and_security(self):
        mem = MemoryManager(db_path=self.memory_db)

        # Store safe preference
        ok, err = mem.remember("preferred_theme", "Midnight", category="ui")
        self.assertTrue(ok)
        self.assertIsNone(err)

        # Recall
        val = mem.recall("preferred_theme")
        self.assertEqual(val, "Midnight")

        # Security check: Password must be blocked
        ok_pwd, err_pwd = mem.remember("wifi_password", "SuperSecret123")
        self.assertFalse(ok_pwd)
        self.assertIn("Security Violation", str(err_pwd))

        # Security check: API key must be blocked
        ok_key, err_key = mem.remember("github_token", "ghp_123456789")
        self.assertFalse(ok_key)

        # List & Forget
        memories = mem.list_memories()
        self.assertEqual(len(memories), 1)

        self.assertTrue(mem.forget("preferred_theme"))
        self.assertIsNone(mem.recall("preferred_theme"))

    # -------------------------------------------------------------------------
    # 7. Research Engine & Voice Tests
    # -------------------------------------------------------------------------
    def test_research_engine_formulation_and_synthesis(self):
        re = ResearchEngine()
        q = re.formulate_query("Hey June, please search the web for PipeWire audio routing")
        self.assertIn("PipeWire audio routing", q)

        results = re.search_and_synthesize("Hyprland keybindings", max_results=2)
        self.assertGreater(results["results_count"], 0)
        self.assertIn("synthesis_markdown", results)
        self.assertIn("Hyprland", results["synthesis_markdown"])

    def test_voice_pipeline_push_to_talk(self):
        vp = VoicePipeline()
        start_res = vp.start_push_to_talk()
        self.assertEqual(start_res["status"], "listening")
        self.assertTrue(vp.is_listening)

        stop_res = vp.stop_push_to_talk()
        self.assertEqual(stop_res["status"], "idle")
        self.assertFalse(vp.is_listening)

    # -------------------------------------------------------------------------
    # 8. Daemon Integration Tests (Phase 7 RPC Handlers)
    # -------------------------------------------------------------------------
    def test_daemon_phase7_handlers(self):
        daemon = JuneDaemon(
            config_path=self.config_path,
            db_path=self.conv_db,
            memory_db_path=self.memory_db,
            tcp_port=42498,
        )

        # Plan action dispatch
        plan_res = daemon.dispatch("plan_action", {"goal": "switch to workspace 5"})
        self.assertEqual(len(plan_res["steps"]), 1)
        self.assertEqual(plan_res["steps"][0]["primitive"], "workspace.switch")

        # Memory remember dispatch
        rem_res = daemon.dispatch("remember", {"key": "shell", "value": "fish", "category": "tools"})
        self.assertTrue(rem_res["success"])

        # Memory recall dispatch
        rec_res = daemon.dispatch("recall", {"key": "shell"})
        self.assertEqual(rec_res["value"], "fish")

        # Screen analyze dispatch
        screen_res = daemon.dispatch("screen_analyze", {})
        self.assertIn("findings", screen_res)

        # Web research dispatch
        res_data = daemon.dispatch("web_research", {"query": "Linux memory management"})
        self.assertIn("synthesis_markdown", res_data)

        # Chat integration with automatic action execution
        chat_res = daemon.dispatch("chat", {"message": "switch to workspace 2"})
        self.assertIn("Action Executed", chat_res["content"])


if __name__ == "__main__":
    unittest.main()
