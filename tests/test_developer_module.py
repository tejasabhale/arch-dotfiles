#!/usr/bin/env python3
"""
Automated Test Suite for Developer Productivity Module (Phase 9).
Tests workspace project launcher, git manager, python environment manager,
node.js scripts inspector, listening ports monitor, and SSH shortcuts.
"""

import json
import os
import shutil
import sys
import tempfile
import pytest

from developer.project_launcher.project_manager import ProjectManager
from developer.git.git_manager import GitManager
from developer.python.python_manager import PythonManager
from developer.node.node_manager import NodeManager
from developer.ports.ports_manager import PortsManager
from developer.ssh.ssh_manager import SSHManager


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp(prefix="tejas_test_dev_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ============================================================================
# 1. Project Manager Tests
# ============================================================================

def test_project_manager_detect_types(temp_dir):
    mgr = ProjectManager(config_path=os.path.join(temp_dir, "projects.json"))

    # Test Rust project
    rust_dir = os.path.join(temp_dir, "rust_proj")
    os.makedirs(rust_dir)
    with open(os.path.join(rust_dir, "Cargo.toml"), "w") as f:
        f.write('[package]\nname = "rust_proj"\n')
    assert mgr.detect_project_type(rust_dir) == "Rust"

    # Test Python project
    py_dir = os.path.join(temp_dir, "py_proj")
    os.makedirs(py_dir)
    with open(os.path.join(py_dir, "pyproject.toml"), "w") as f:
        f.write('[tool.poetry]\nname = "py_proj"\n')
    assert mgr.detect_project_type(py_dir) == "Python"

    # Test Node/TS project
    node_dir = os.path.join(temp_dir, "node_proj")
    os.makedirs(node_dir)
    with open(os.path.join(node_dir, "package.json"), "w") as f:
        f.write('{"name": "node_proj"}')
    assert "Node" in mgr.detect_project_type(node_dir)


def test_project_manager_pinning(temp_dir):
    cfg = os.path.join(temp_dir, "projects.json")
    mgr = ProjectManager(config_path=cfg)

    # Initial pinned list contains at least default
    initial = mgr.list_pinned()
    assert isinstance(initial, list)

    # Pin new project
    proj_dir = os.path.join(temp_dir, "my_custom_project")
    os.makedirs(proj_dir)
    ok = mgr.pin_project(proj_dir, name="Custom Proj", p_type="Rust")
    assert ok is True

    # Check pinned
    pinned = mgr.list_pinned()
    matching = [p for p in pinned if p["path"] == os.path.abspath(proj_dir)]
    assert len(matching) == 1
    assert matching[0]["name"] == "Custom Proj"
    assert matching[0]["type"] == "Rust"

    # Unpin project
    ok_unpin = mgr.unpin_project(proj_dir)
    assert ok_unpin is True
    assert not any(p["path"] == os.path.abspath(proj_dir) for p in mgr.list_pinned())


def test_project_manager_scan_workspaces(temp_dir):
    workspace = os.path.join(temp_dir, "my_workspace")
    os.makedirs(workspace)

    proj_a = os.path.join(workspace, "proj_a")
    os.makedirs(proj_a)
    with open(os.path.join(proj_a, "package.json"), "w") as f:
        f.write('{"name": "proj_a"}')

    proj_b = os.path.join(workspace, "proj_b")
    os.makedirs(proj_b)
    with open(os.path.join(proj_b, "Cargo.toml"), "w") as f:
        f.write('[package]\nname = "proj_b"\n')

    mgr = ProjectManager(config_path=os.path.join(temp_dir, "projects.json"))
    scanned = mgr.scan_workspaces(custom_dirs=[workspace], max_depth=1)
    paths = [p["path"] for p in scanned]
    assert os.path.abspath(proj_a) in paths
    assert os.path.abspath(proj_b) in paths


# ============================================================================
# 2. Git Manager Tests
# ============================================================================

def test_git_manager_non_repo(temp_dir):
    non_repo = os.path.join(temp_dir, "empty")
    os.makedirs(non_repo)
    gm = GitManager(repo_path=non_repo)
    assert gm.is_git_repo() is False
    status = gm.get_status()
    assert status["is_repo"] is False
    assert "error" in status


def test_git_manager_current_repo():
    # Test on the current repository
    gm = GitManager(repo_path=".")
    assert gm.is_git_repo() is True
    status = gm.get_status()
    assert status["is_repo"] is True
    assert isinstance(status["branch"], str)
    assert len(status["branch"]) > 0
    assert isinstance(status["staged"], list)
    assert isinstance(status["unstaged"], list)
    assert isinstance(status["untracked"], list)


# ============================================================================
# 3. Python Manager Tests
# ============================================================================

def test_python_manager_system_python():
    pm = PythonManager()
    sys_py = pm.get_system_python()
    assert sys_py["is_system"] is True
    assert sys_py["executable"] is not None
    assert len(sys_py["version"]) > 0


def test_python_manager_local_venvs(temp_dir):
    pm = PythonManager(workspace_path=temp_dir)
    # Initially no venv
    assert len(pm.detect_local_venvs()) == 0

    # Create dummy venv structure
    fake_venv = os.path.join(temp_dir, ".venv")
    os.makedirs(fake_venv)
    with open(os.path.join(fake_venv, "pyvenv.cfg"), "w") as f:
        f.write("home = /usr/bin\nversion = 3.12.0\n")

    venvs = pm.detect_local_venvs()
    assert len(venvs) == 1
    assert venvs[0]["name"] == ".venv"


def test_python_manager_jupyter_commands():
    pm = PythonManager()
    cmd = pm.get_jupyter_launch_command(port=8899, workspace_dir="/home/user/code", use_lab=True)
    assert "--port=8899" in cmd
    assert "--notebook-dir=/home/user/code" in cmd
    assert "--no-browser" in cmd


# ============================================================================
# 4. Node Manager Tests
# ============================================================================

def test_node_manager_detection(temp_dir):
    nm = NodeManager(workspace_path=temp_dir)
    assert nm.is_node_project() is False

    # Create package.json
    pkg_data = {
        "name": "my-web-app",
        "version": "1.0.0",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "test": "vitest",
        },
        "dependencies": {
            "react": "^18.2.0",
        },
        "devDependencies": {
            "vite": "^5.0.0",
        },
    }
    with open(os.path.join(temp_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(pkg_data, f)

    assert nm.is_node_project() is True
    summary = nm.get_project_summary()
    assert summary["name"] == "my-web-app"
    assert summary["version"] == "1.0.0"
    assert summary["dependencies_count"] == 1
    assert summary["dev_dependencies_count"] == 1
    assert "dev" in summary["scripts"]
    assert "build" in summary["scripts"]


def test_node_manager_package_manager_resolution(temp_dir):
    nm = NodeManager(workspace_path=temp_dir)

    # pnpm lockfile
    pnpm_lock = os.path.join(temp_dir, "pnpm-lock.yaml")
    with open(pnpm_lock, "w") as f:
        f.write("")
    pm = nm.detect_package_manager()
    assert "pnpm" in pm
    os.remove(pnpm_lock)

    # yarn lockfile
    yarn_lock = os.path.join(temp_dir, "yarn.lock")
    with open(yarn_lock, "w") as f:
        f.write("")
    pm = nm.detect_package_manager()
    assert "yarn" in pm


def test_node_manager_run_command():
    nm = NodeManager()
    cmd = nm.get_run_command("dev")
    assert "dev" in cmd


# ============================================================================
# 5. Ports Manager Tests
# ============================================================================

def test_ports_manager_known_services():
    ports_mgr = PortsManager()
    assert "Vite" in ports_mgr.get_known_service_name(5173)
    assert "React" in ports_mgr.get_known_service_name(3000)
    assert "PostgreSQL" in ports_mgr.get_known_service_name(5432)
    assert "FastAPI" in ports_mgr.get_known_service_name(8000)
    assert "Ollama" in ports_mgr.get_known_service_name(11434)
    assert "June AI" in ports_mgr.get_known_service_name(42421)


def test_ports_manager_parse_ss_output():
    ports_mgr = PortsManager()
    raw_ss = """
Netid State  Recv-Q Send-Q   Local Address:Port   Peer Address:Port Process
tcp   LISTEN 0      128            0.0.0.0:22          0.0.0.0:*     users:(("sshd",pid=789,fd=3))
tcp   LISTEN 0      511          127.0.0.1:5173        0.0.0.0:*     users:(("vite",pid=12345,fd=18))
tcp   LISTEN 0      128          127.0.0.1:42421       0.0.0.0:*     users:(("python",pid=8888,fd=4))
"""
    parsed = ports_mgr.parse_ss_output(raw_ss)
    assert len(parsed) == 3

    p5173 = next((p for p in parsed if p["port"] == 5173), None)
    assert p5173 is not None
    assert p5173["process"] == "vite"
    assert p5173["pid"] == 12345
    assert "Vite" in p5173["service"]

    p42421 = next((p for p in parsed if p["port"] == 42421), None)
    assert p42421 is not None
    assert p42421["process"] == "python"
    assert p42421["pid"] == 8888
    assert "June AI" in p42421["service"]


def test_ports_manager_parse_windows_netstat():
    ports_mgr = PortsManager()
    raw_netstat = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       900
  TCP    0.0.0.0:5432           0.0.0.0:0              LISTENING       3200
  TCP    127.0.0.1:3000         0.0.0.0:0              LISTENING       4500
"""
    parsed = ports_mgr.parse_windows_netstat(raw_netstat)
    ports = [p["port"] for p in parsed]
    assert 135 in ports
    assert 5432 in ports
    assert 3000 in ports


def test_ports_manager_kill_safety_guards():
    ports_mgr = PortsManager()
    # Test refusal to kill PID 0-4 or systemd
    # Mock list_listening_ports returning system PID
    ports_mgr.list_listening_ports = lambda: [
        {"port": 135, "pid": 4, "process": "System", "service": "System"},
        {"port": 1, "pid": 1, "process": "systemd", "service": "init"},
    ]

    ok, msg = ports_mgr.kill_port(135)
    assert ok is False
    assert "Refusing to kill" in msg

    ok, msg = ports_mgr.kill_port(1)
    assert ok is False
    assert "Refusing to kill" in msg


# ============================================================================
# 6. SSH Manager Tests
# ============================================================================

def test_ssh_manager_config_parsing(temp_dir):
    cfg = os.path.join(temp_dir, "ssh_config")
    with open(cfg, "w", encoding="utf-8") as f:
        f.write("""
# Global default
Host *
    User devuser
    Port 22

# Bastion server
Host bastion
    HostName 192.168.1.100
    User jumpuser
    Port 2222
    IdentityFile ~/.ssh/id_rsa_jump

# Production web
Host prod-web
    HostName web.production.corp
    Port 22
""")

    sm = SSHManager(config_path=cfg)
    hosts = sm.list_hosts()
    assert len(hosts) == 2

    bastion = next((h for h in hosts if h["alias"] == "bastion"), None)
    assert bastion is not None
    assert bastion["hostname"] == "192.168.1.100"
    assert bastion["user"] == "jumpuser"
    assert bastion["port"] == 2222
    assert "ssh bastion" in bastion["connection_string"]
    assert "kitty --title 'SSH: bastion' ssh bastion" in bastion["terminal_command"]

    prod = next((h for h in hosts if h["alias"] == "prod-web"), None)
    assert prod is not None
    assert prod["hostname"] == "web.production.corp"
    assert prod["port"] == 22


def test_ssh_manager_add_host_entry(temp_dir):
    cfg = os.path.join(temp_dir, "ssh_config")
    sm = SSHManager(config_path=cfg)

    ok, msg = sm.add_host_entry(
        alias="staging-db",
        hostname="10.0.0.50",
        user="postgres",
        port=5432,
    )
    assert ok is True

    # Verify parsed back
    hosts = sm.list_hosts()
    assert len(hosts) == 1
    assert hosts[0]["alias"] == "staging-db"
    assert hosts[0]["hostname"] == "10.0.0.50"
    assert hosts[0]["user"] == "postgres"
    assert hosts[0]["port"] == 5432
