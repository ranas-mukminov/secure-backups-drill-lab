"""Job state management and tracking."""

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    """Backup job execution status."""

    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    VERIFYING = "verifying"


@dataclass
class JobState:
    """State information for a backup job."""

    job_name: str
    status: JobStatus = JobStatus.IDLE
    last_run: datetime | None = None
    last_success: datetime | None = None
    last_verification: datetime | None = None
    duration_seconds: float = 0.0
    bytes_transferred: int = 0
    repository_size_bytes: int = 0
    error_message: str | None = None
    error_count: int = 0
    verification_success: bool = True
    metadata: dict[str, str] = field(default_factory=dict)

    def update_success(
        self, duration: float, bytes_transferred: int, repository_size: int = 0
    ) -> None:
        """Update state after successful backup.

        Args:
            duration: Backup duration in seconds
            bytes_transferred: Bytes transferred during backup
            repository_size: Total repository size in bytes
        """
        now = datetime.now(UTC)
        self.status = JobStatus.SUCCESS
        self.last_run = now
        self.last_success = now
        self.duration_seconds = duration
        self.bytes_transferred = bytes_transferred
        if repository_size > 0:
            self.repository_size_bytes = repository_size
        self.error_message = None

    def update_failure(self, error: str) -> None:
        """Update state after failed backup.

        Args:
            error: Error message describing the failure
        """
        self.status = JobStatus.FAILED
        self.last_run = datetime.now(UTC)
        self.error_message = error
        self.error_count += 1

    def update_verification(self, success: bool, error: str | None = None) -> None:
        """Update state after verification.

        Args:
            success: Whether verification succeeded
            error: Optional error message if verification failed
        """
        self.last_verification = datetime.now(UTC)
        self.verification_success = success
        if not success and error:
            self.error_message = error


class JobRegistry:
    """Thread-safe registry for tracking job states."""

    def __init__(self) -> None:
        """Initialize job registry."""
        self._states: dict[str, JobState] = {}
        self._lock = threading.RLock()

    def register_job(self, job_name: str) -> None:
        """Register a new job.

        Args:
            job_name: Unique job name
        """
        with self._lock:
            if job_name not in self._states:
                self._states[job_name] = JobState(job_name=job_name)

    def get_state(self, job_name: str) -> JobState | None:
        """Get current state for a job.

        Args:
            job_name: Job name

        Returns:
            JobState if job is registered, None otherwise
        """
        with self._lock:
            return self._states.get(job_name)

    def update_state(self, job_name: str, **kwargs: Any) -> None:
        """Update job state with specified fields.

        Args:
            job_name: Job name
            **kwargs: Fields to update on JobState
        """
        with self._lock:
            if job_name not in self._states:
                self.register_job(job_name)
            state = self._states[job_name]
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)

    def set_status(self, job_name: str, status: JobStatus) -> None:
        """Set job execution status.

        Args:
            job_name: Job name
            status: New status
        """
        self.update_state(job_name, status=status)

    def get_all_states(self) -> dict[str, JobState]:
        """Get all job states.

        Returns:
            Dictionary mapping job names to states
        """
        with self._lock:
            return dict(self._states)

    def clear(self) -> None:
        """Clear all job states (primarily for testing)."""
        with self._lock:
            self._states.clear()
