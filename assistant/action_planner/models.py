#!/usr/bin/env python3
"""
Data models for June AI Action Planner and Controlled Executor.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import uuid


class RiskLevel(str, Enum):
    LOW = "low"          # Safe, read-only or standard UX (e.g., switch workspace, open browser)
    MEDIUM = "medium"    # State-modifying (e.g., toggle hotspot, switch power profile)
    HIGH = "high"        # Disruptive or destructive (e.g., kill process, delete files)
    BLOCKED = "blocked"  # Forbidden actions (e.g., disk format, EFI touch, Windows partition touch)


@dataclass
class ActionStep:
    primitive: str
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: str = "pending"  # pending, executing, success, failed, aborted
    result: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["risk_level"] = self.risk_level.value
        return d


@dataclass
class ActionPlan:
    goal: str
    steps: List[ActionStep] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    requires_confirmation: bool = False
    status: str = "pending"  # pending, approved, executing, completed, aborted, failed
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "requires_confirmation": self.requires_confirmation,
            "status": self.status,
            "created_at": self.created_at,
            "steps": [s.to_dict() for s in self.steps],
        }
