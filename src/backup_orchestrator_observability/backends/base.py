"""Base backend interface for backup tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class BackupResult:
    """Result of a backup operation."""

    success: bool
    duration_seconds: float
    bytes_added: int = 0
    bytes_processed: int = 0
    files_new: int = 0
    files_changed: int = 0
    files_unmodified: int = 0
    snapshot_id: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize metadata dict if None."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CheckResult:
    """Result of a repository check operation."""

    success: bool
    errors: list[str]
    warnings: list[str]
    duration_seconds: float
    error_message: str | None = None


@dataclass
class RestoreResult:
    """Result of a restore operation."""

    success: bool
    duration_seconds: float
    bytes_restored: int = 0
    files_restored: int = 0
    error_message: str | None = None


@dataclass
class Snapshot:
    """Backup snapshot information."""

    id: str
    timestamp: datetime
    hostname: str
    paths: list[str]
    tags: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize tags list if None."""
        if self.tags is None:
            self.tags = []


class BackupBackend(ABC):
    """Abstract base class for backup tool backends."""

    @abstractmethod
    def backup(
        self,
        sources: list[str],
        repository: str,
        **options: Any,
    ) -> BackupResult:
        """Perform a backup operation.

        Args:
            sources: List of source paths to backup
            repository: Repository location/URL
            **options: Backend-specific options

        Returns:
            BackupResult with operation details

        Raises:
            Exception: If backup fails
        """
        pass

    @abstractmethod
    def check(self, repository: str, **options: Any) -> CheckResult:
        """Check repository integrity.

        Args:
            repository: Repository location/URL
            **options: Backend-specific options

        Returns:
            CheckResult with check details

        Raises:
            Exception: If check fails
        """
        pass

    @abstractmethod
    def restore(
        self,
        repository: str,
        snapshot_id: str,
        target: str,
        **options: Any,
    ) -> RestoreResult:
        """Restore from a snapshot.

        Args:
            repository: Repository location/URL
            snapshot_id: Snapshot/archive ID to restore
            target: Target path for restoration
            **options: Backend-specific options

        Returns:
            RestoreResult with operation details

        Raises:
            Exception: If restore fails
        """
        pass

    @abstractmethod
    def list_snapshots(self, repository: str, **options: Any) -> list[Snapshot]:
        """List available snapshots.

        Args:
            repository: Repository location/URL
            **options: Backend-specific options

        Returns:
            List of Snapshot objects

        Raises:
            Exception: If listing fails
        """
        pass

    @abstractmethod
    def forget(
        self,
        repository: str,
        snapshot_ids: list[str],
        **options: Any,
    ) -> None:
        """Forget (delete) specific snapshots.

        Args:
            repository: Repository location/URL
            snapshot_ids: List of snapshot IDs to forget
            **options: Backend-specific options

        Raises:
            Exception: If forget operation fails
        """
        pass

    @abstractmethod
    def prune(self, repository: str, **options: Any) -> None:
        """Prune repository to free unused space.

        Args:
            repository: Repository location/URL
            **options: Backend-specific options

        Raises:
            Exception: If prune operation fails
        """
        pass

    @abstractmethod
    def get_repository_size(self, repository: str) -> int:
        """Get total repository size in bytes.

        Args:
            repository: Repository location/URL

        Returns:
            Repository size in bytes

        Raises:
            Exception: If size query fails
        """
        pass
