#!/usr/bin/env python3
"""
June AI JSON-RPC 2.0 IPC Protocol & Socket Abstraction.
Facilitates decoupled communication between the visual shell (Quickshell),
command-line utilities, and the background daemon.
"""

from dataclasses import dataclass
import json
import os
import socket
import sys
from typing import Any, Dict, Optional, Union

# Standard JSON-RPC 2.0 Error Codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_ERROR = -32000


@dataclass
class JsonRpcRequest:
    method: str
    params: Dict[str, Any]
    id: Optional[Union[str, int]] = 1
    jsonrpc: str = "2.0"

    def to_json(self) -> str:
        data = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
        }
        if self.id is not None:
            data["id"] = self.id
        return json.dumps(data)


@dataclass
class JsonRpcResponse:
    id: Optional[Union[str, int]]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"

    def to_json(self) -> str:
        data: Dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            data["error"] = self.error
        else:
            data["result"] = self.result
        return json.dumps(data)

    @classmethod
    def success(cls, id: Optional[Union[str, int]], result: Any) -> "JsonRpcResponse":
        return cls(id=id, result=result)

    @classmethod
    def error_response(
        cls, id: Optional[Union[str, int]], code: int, message: str, data: Optional[Any] = None
    ) -> "JsonRpcResponse":
        err: Dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        return cls(id=id, error=err)


def get_default_socket_path() -> str:
    """Returns the platform-appropriate IPC socket location."""
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
    if xdg_runtime and sys.platform != "win32":
        sock_dir = os.path.join(xdg_runtime, "june")
    else:
        sock_dir = os.path.expanduser("~/.local/share/tejas-os/june")
    os.makedirs(sock_dir, exist_ok=True)
    return os.path.join(sock_dir, "june.sock")


DEFAULT_TCP_PORT = 42421


def send_ipc_message(
    method: str,
    params: Optional[Dict[str, Any]] = None,
    socket_path: Optional[str] = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """
    Sends a synchronous JSON-RPC request to the June daemon via UNIX domain socket
    or TCP fallback (on Windows/non-UNIX).
    """
    req = JsonRpcRequest(method=method, params=params or {}, id=1)
    payload = (req.to_json() + "\n").encode("utf-8")

    path = socket_path or get_default_socket_path()

    # Attempt UNIX domain socket if supported and exists
    if hasattr(socket, "AF_UNIX") and sys.platform != "win32" and os.path.exists(path):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(min(timeout, 1.0))
            s.connect(path)
            s.settimeout(timeout)
            s.sendall(payload)
            response_data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in chunk:
                    break
            s.close()
            return json.loads(response_data.decode("utf-8"))
        except Exception:
            # Fall back to TCP if UNIX socket fails
            pass

    # TCP Loopback fallback (Windows or headless environments)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)  # Fast connection timeout for offline check
        s.connect(("127.0.0.1", DEFAULT_TCP_PORT))
        s.settimeout(timeout)
        s.sendall(payload)
        response_data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b"\n" in chunk:
                break
        s.close()
        return json.loads(response_data.decode("utf-8"))
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": SERVER_ERROR,
                "message": f"Could not connect to June daemon: {e}",
            },
        }
