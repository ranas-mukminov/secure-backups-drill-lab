"""Disaster Recovery Drill Lab - Automated backup recovery testing."""

__version__ = "0.1.0"
__author__ = "Ranas Mukminov"
__license__ = "Apache-2.0"
__url__ = "https://run-as-daemon.ru"

from backup_disaster_drill_lab.metrics import DrillMetrics, calculate_rpo, calculate_rto
from backup_disaster_drill_lab.report.model import DrillReport, TimelineEvent, VerificationResult

__all__ = [
    "__version__",
    "DrillMetrics",
    "calculate_rpo",
    "calculate_rto",
    "DrillReport",
    "TimelineEvent",
    "VerificationResult",
]
