"""Restic backend implementation."""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backup_orchestrator_observability.backends.base import (
    BackupBackend,
    BackupResult,
    CheckResult,
    RestoreResult,
    Snapshot,
)

logger = logging.getLogger(__name__)


class ResticBackend(BackupBackend):
    """Restic CLI wrapper for backup operations."""

    def __init__(self, password_env: str = "RESTIC_PASSWORD") -> None:
        """Initialize Restic backend.

        Args:
            password_env: Environment variable containing repository password
        """
        self.password_env = password_env

    def _run_restic(
        self,
        args: List[str],
        repository: str,
        extra_env: Optional[Dict[str, str]] = None,
        capture_json: bool = False,
    ) -> subprocess.CompletedProcess:
        """Run restic command.

        Args:
            args: Restic command arguments
            repository: Repository URL
            extra_env: Additional environment variables
            capture_json: Whether to expect JSON output

        Returns:
            CompletedProcess with command result

        Raises:
            subprocess.CalledProcessError: If restic command fails
        """
        import os

        env = os.environ.copy()
        env["RESTIC_REPOSITORY"] = repository

        if extra_env:
            env.update(extra_env)

        cmd = ["restic"] + args
        if capture_json and "--json" not in args:
            cmd.append("--json")

        logger.debug(f"Running restic command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        return result

    def backup(
        self,
        sources: List[str],
        repository: str,
        **options: Any,
    ) -> BackupResult:
        """Perform restic backup.

        Args:
            sources: Paths to backup
            repository: Restic repository URL
            **options: Additional options (tags, exclude patterns, etc.)

        Returns:
            BackupResult with backup statistics
        """
        import time

        start_time = time.time()

        args = ["backup"] + sources
        
        # Add optional parameters
        if "tags" in options:
            for tag in options["tags"]:
                args.extend(["--tag", tag])
        
        if "exclude" in options:
            for pattern in options["exclude"]:
                args.extend(["--exclude", pattern])
        
        if "exclude_file" in options:
            args.extend(["--exclude-file", options["exclude_file"]])

        try:
            result = self._run_restic(args, repository, capture_json=True)
            duration = time.time() - start_time

            # Parse JSON output
            output_lines = result.stdout.strip().split("\n")
            summary = None
            for line in output_lines:
                try:
                    data = json.loads(line)
                    if data.get("message_type") == "summary":
                        summary = data
                        break
                except json.JSONDecodeError:
                    continue

            if summary:
                return BackupResult(
                    success=True,
                    duration_seconds=duration,
                    bytes_added=summary.get("data_added", 0),
                    bytes_processed=summary.get("total_bytes_processed", 0),
                    files_new=summary.get("files_new", 0),
                    files_changed=summary.get("files_changed", 0),
                    files_unmodified=summary.get("files_unmodified", 0),
                    snapshot_id=summary.get("snapshot_id"),
                    metadata=summary,
                )
            else:
                # Fallback if JSON parsing fails
                return BackupResult(
                    success=True,
                    duration_seconds=duration,
                    metadata={"stdout": result.stdout},
                )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"Restic backup failed: {e.stderr}")
            return BackupResult(
                success=False,
                duration_seconds=duration,
                error_message=e.stderr,
            )

    def check(self, repository: str, **options: Any) -> CheckResult:
        """Check restic repository integrity.

        Args:
            repository: Restic repository URL
            **options: Check options (read_data, etc.)

        Returns:
            CheckResult with check status
        """
        import time

        start_time = time.time()
        args = ["check"]

        if options.get("read_data"):
            args.append("--read-data")

        errors = []
        warnings = []

        try:
            result = self._run_restic(args, repository)
            duration = time.time() - start_time

            # Parse output for errors/warnings
            for line in result.stdout.split("\n"):
                if "error" in line.lower():
                    errors.append(line.strip())
                elif "warning" in line.lower():
                    warnings.append(line.strip())

            return CheckResult(
                success=True,
                errors=errors,
                warnings=warnings,
                duration_seconds=duration,
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            return CheckResult(
                success=False,
                errors=[e.stderr],
                warnings=[],
                duration_seconds=duration,
                error_message=e.stderr,
            )

    def restore(
        self,
        repository: str,
        snapshot_id: str,
        target: str,
        **options: Any,
    ) -> RestoreResult:
        """Restore from restic snapshot.

        Args:
            repository: Restic repository URL
            snapshot_id: Snapshot ID to restore
            target: Target directory for restoration
            **options: Restore options (include, exclude, etc.)

        Returns:
            RestoreResult with restore statistics
        """
        import time

        start_time = time.time()
        args = ["restore", snapshot_id, "--target", target]

        if "include" in options:
            for pattern in options["include"]:
                args.extend(["--include", pattern])

        try:
            result = self._run_restic(args, repository)
            duration = time.time() - start_time

            # Restic doesn't provide detailed restore stats in stdout
            # Parse what we can from the output
            files_restored = 0
            bytes_restored = 0

            return RestoreResult(
                success=True,
                duration_seconds=duration,
                bytes_restored=bytes_restored,
                files_restored=files_restored,
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            return RestoreResult(
                success=False,
                duration_seconds=duration,
                error_message=e.stderr,
            )

    def list_snapshots(self, repository: str, **options: Any) -> List[Snapshot]:
        """List restic snapshots.

        Args:
            repository: Restic repository URL
            **options: List options (tags, host, etc.)

        Returns:
            List of Snapshot objects
        """
        args = ["snapshots"]

        if "tags" in options:
            for tag in options["tags"]:
                args.extend(["--tag", tag])

        if "host" in options:
            args.extend(["--host", options["host"]])

        try:
            result = self._run_restic(args, repository, capture_json=True)
            snapshots_data = json.loads(result.stdout)

            snapshots = []
            for snap in snapshots_data:
                snapshots.append(
                    Snapshot(
                        id=snap["short_id"],
                        timestamp=datetime.fromisoformat(
                            snap["time"].replace("Z", "+00:00")
                        ),
                        hostname=snap.get("hostname", ""),
                        paths=snap.get("paths", []),
                        tags=snap.get("tags", []),
                    )
                )

            return snapshots

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []

    def forget(
        self,
        repository: str,
        snapshot_ids: List[str],
        **options: Any,
    ) -> None:
        """Forget restic snapshots.

        Args:
            repository: Restic repository URL
            snapshot_ids: Snapshot IDs to forget
            **options: Forget options
        """
        args = ["forget"] + snapshot_ids

        if options.get("prune", False):
            args.append("--prune")

        self._run_restic(args, repository)

    def prune(self, repository: str, **options: Any) -> None:
        """Prune restic repository.

        Args:
            repository: Restic repository URL
            **options: Prune options
        """
        args = ["prune"]
        self._run_restic(args, repository)

    def get_repository_size(self, repository: str) -> int:
        """Get restic repository size.

        Args:
            repository: Restic repository URL

        Returns:
            Repository size in bytes
        """
        try:
            result = self._run_restic(["stats"], repository, capture_json=True)
            stats = json.loads(result.stdout)
            return stats.get("total_size", 0)
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
            logger.warning("Failed to get repository size, returning 0")
            return 0

    def apply_retention_policy(
        self,
        repository: str,
        keep_last: Optional[int] = None,
        keep_hourly: Optional[int] = None,
        keep_daily: Optional[int] = None,
        keep_weekly: Optional[int] = None,
        keep_monthly: Optional[int] = None,
        keep_yearly: Optional[int] = None,
        prune: bool = True,
    ) -> None:
        """Apply retention policy using restic forget.

        Args:
            repository: Restic repository URL
            keep_last: Keep last N snapshots
            keep_hourly: Keep N hourly snapshots
            keep_daily: Keep N daily snapshots
            keep_weekly: Keep N weekly snapshots
            keep_monthly: Keep N monthly snapshots
            keep_yearly: Keep N yearly snapshots
            prune: Whether to prune after forgetting
        """
        args = ["forget"]

        if keep_last:
            args.extend(["--keep-last", str(keep_last)])
        if keep_hourly:
            args.extend(["--keep-hourly", str(keep_hourly)])
        if keep_daily:
            args.extend(["--keep-daily", str(keep_daily)])
        if keep_weekly:
            args.extend(["--keep-weekly", str(keep_weekly)])
        if keep_monthly:
            args.extend(["--keep-monthly", str(keep_monthly)])
        if keep_yearly:
            args.extend(["--keep-yearly", str(keep_yearly)])

        if prune:
            args.append("--prune")

        self._run_restic(args, repository)
