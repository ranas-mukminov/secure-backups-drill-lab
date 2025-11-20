"""Drill report data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class EventType(str, Enum):
    """Types of events in a drill timeline."""

    SETUP = "setup"
    FAILURE_INJECTED = "failure_injected"
    DETECTION = "detection"
    RESTORE_STARTED = "restore_started"
    RESTORE_COMPLETED = "restore_completed"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    CLEANUP = "cleanup"


@dataclass
class TimelineEvent:
    """A single event in the drill timeline."""

    timestamp: datetime
    event_type: EventType
    description: str
    metadata: dict = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Results of post-restore verification."""

    data_integrity_ok: bool
    service_restored: bool
    checksums_matched: bool
    issues: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class DrillReport:
    """Complete drill execution report."""

    scenario_name: str
    drill_id: str
    timestamp: datetime
    rto_seconds: float
    rpo_seconds: float
    target_rto_seconds: float
    target_rpo_seconds: float
    timeline: List[TimelineEvent]
    verification: VerificationResult
    success: bool
    metadata: dict = field(default_factory=dict)
    ai_summary: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert report to dictionary.

        Returns:
            Dictionary representation of the report
        """
        return {
            "scenario_name": self.scenario_name,
            "drill_id": self.drill_id,
            "timestamp": self.timestamp.isoformat(),
            "rto_seconds": self.rto_seconds,
            "rpo_seconds": self.rpo_seconds,
            "target_rto_seconds": self.target_rto_seconds,
            "target_rpo_seconds": self.target_rpo_seconds,
            "success": self.success,
            "timeline": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type.value,
                    "description": event.description,
                    "metadata": event.metadata,
                }
                for event in self.timeline
            ],
            "verification": {
                "data_integrity_ok": self.verification.data_integrity_ok,
                "service_restored": self.verification.service_restored,
                "checksums_matched": self.verification.checksums_matched,
                "issues": self.verification.issues,
                "metadata": self.verification.metadata,
            },
            "metadata": self.metadata,
            "ai_summary": self.ai_summary,
        }
