"""Borg Backup backend implementation."""

import contextlib
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Any

from backup_orchestrator_observability.backends.base import (
    BackupBackend,
    BackupResult,
    CheckResult,
    RestoreResult,
    Snapshot,
)

logger = logging.getLogger(__name__)


class BorgBackend(BackupBackend):
    """Borg Backup CLI wrapper for backup operations."""

    def __init__(self, passphrase_env: str = "BORG_PASSPHRASE") -> None:
        """Initialize Borg backend.

        Args:
            passphrase_env: Environment variable containing repository passphrase
        """
        self.passphrase_env = passphrase_env

    def _run_borg(
        self,
        args: list[str],
        repository: str | None = None,
        extra_env: dict[str, str] | None = None,
        capture_json: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Run borg command.

        Args:
            args: Borg command arguments
            repository: Repository path (prepended to first arg if provided)
            extra_env: Additional environment variables
            capture_json: Whether to expect JSON output

        Returns:
            CompletedProcess with command result

        Raises:
            subprocess.CalledProcessError: If borg command fails
        """
        import os

        env = os.environ.copy()

        if extra_env:
            env.update(extra_env)

        cmd = ["borg"] + args

        # Add repository to command if provided (borg requires it per-command)
        if repository and len(args) > 0:
            # Insert repository after the borg subcommand
            cmd = ["borg", args[0]]
            if capture_json:
                cmd.append("--json")
            cmd.append(repository)
            cmd.extend(args[1:])
        elif capture_json and "--json" not in args:
            cmd.insert(1, "--json") if len(cmd) > 1 else cmd.append("--json")

        logger.debug(f"Running borg command: {' '.join(cmd)}")

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
        sources: list[str],
        repository: str,
        **options: Any,
    ) -> BackupResult:
        """Perform borg backup (create archive).

        Args:
            sources: Paths to backup
            repository: Borg repository path
            **options: Additional options (compression, exclude, etc.)

        Returns:
            BackupResult with backup statistics
        """
        start_time = time.time()

        # Generate archive name with timestamp
        archive_name = options.get(
            "archive_name",
            f"{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}",
        )
        archive = f"{repository}::{archive_name}"

        args = ["create", "--stats"]

        # Add compression
        compression = options.get("compression", "lz4")
        args.extend(["--compression", compression])

        # Add exclude patterns
        if "exclude" in options:
            for pattern in options["exclude"]:
                args.extend(["--exclude", pattern])

        # Add the archive and sources
        args.append(archive)
        args.extend(sources)

        try:
            result = self._run_borg(args)
            duration = time.time() - start_time

            # Parse stats from output
            stdout = result.stdout + result.stderr  # Borg prints stats to stderr
            stats = self._parse_create_stats(stdout)

            return BackupResult(
                success=True,
                duration_seconds=duration,
                bytes_added=stats.get("deduplicated_size", 0),
                bytes_processed=stats.get("original_size", 0),
                files_new=stats.get("number_files", 0),
                snapshot_id=archive_name,
                metadata=stats,
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"Borg create failed: {e.stderr}")
            return BackupResult(
                success=False,
                duration_seconds=duration,
                error_message=e.stderr,
            )

    def _parse_create_stats(self, output: str) -> dict[str, Any]:
        """Parse borg create statistics from output.

        Args:
            output: Borg create stdout/stderr

        Returns:
            Dictionary of statistics
        """
        stats = {}
        for line in output.split("\n"):
            if "Original size:" in line:
                # Extract size value
                parts = line.split(":")
                if len(parts) > 1:
                    try:
                        size_str = parts[1].strip().split()[0]
                        stats["original_size"] = self._parse_size(size_str)
                    except (IndexError, ValueError):
                        pass
            elif "Deduplicated size:" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    try:
                        size_str = parts[1].strip().split()[0]
                        stats["deduplicated_size"] = self._parse_size(size_str)
                    except (IndexError, ValueError):
                        pass
            elif "Number of files:" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    with contextlib.suppress(ValueError):
                        stats["number_files"] = int(parts[1].strip())

        return stats

    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '1.5 GB') to bytes.

        Args:
            size_str: Size string with unit

        Returns:
            Size in bytes
        """
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        parts = size_str.split()
        if len(parts) == 2:
            try:
                value = float(parts[0])
                unit = parts[1]
                return int(value * units.get(unit, 1))
            except ValueError:
                return 0
        return 0

    def check(self, repository: str, **_options: Any) -> CheckResult:
        """Check borg repository integrity.

        Args:
            repository: Borg repository path
            **_options: Check options (reserved for future use)

        Returns:
            CheckResult with check status
        """
        start_time = time.time()
        args = ["check"]

        errors = []
        warnings = []

        try:
            result = self._run_borg(args, repository)
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
        **_options: Any,
    ) -> RestoreResult:
        """Restore from borg archive (extract).

        Args:
            repository: Borg repository path
            snapshot_id: Archive name to restore
            target: Target directory for restoration
            **options: Restore options

        Returns:
            RestoreResult with restore statistics
        """
        start_time = time.time()
        archive = f"{repository}::{snapshot_id}"

        args = ["extract", archive]

        # Change to target directory for extraction
        import os

        original_cwd = os.getcwd()

        try:
            os.makedirs(target, exist_ok=True)
            os.chdir(target)

            self._run_borg(args)
            duration = time.time() - start_time

            return RestoreResult(
                success=True,
                duration_seconds=duration,
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            return RestoreResult(
                success=False,
                duration_seconds=duration,
                error_message=e.stderr,
            )
        finally:
            os.chdir(original_cwd)

    def list_snapshots(self, repository: str, **_options: Any) -> list[Snapshot]:
        """List borg archives.

        Args:
            repository: Borg repository path
            **_options: List options (reserved for future use)

        Returns:
            List of Snapshot objects
        """
        args = ["list"]

        try:
            result = self._run_borg(args, repository, capture_json=True)
            archives_data = json.loads(result.stdout)

            snapshots = []
            for archive in archives_data.get("archives", []):
                # Borg timestamp format: '2023-11-19T12:34:56.123456'
                timestamp_str = archive.get("time", "")
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    timestamp = datetime.utcnow()

                snapshots.append(
                    Snapshot(
                        id=archive.get("name", ""),
                        timestamp=timestamp,
                        hostname=archive.get("hostname", ""),
                        paths=[],  # Borg list doesn't provide paths easily
                        tags=[],  # Borg doesn't have tags by default
                    )
                )

            return snapshots

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to list archives: {e}")
            return []

    def forget(
        self,
        repository: str,
        snapshot_ids: list[str],
        **_options: Any,
    ) -> None:
        """Delete borg archives.

        Args:
            repository: Borg repository path
            snapshot_ids: Archive names to delete
            **_options: Delete options (reserved for future use)
        """
        for archive_name in snapshot_ids:
            args = ["delete", f"{repository}::{archive_name}"]
            self._run_borg(args)

    def prune(self, repository: str, **options: Any) -> None:
        """Prune borg repository to free space.

        Args:
            repository: Borg repository path
            **options: Prune options (keep policies)
        """
        args = ["prune"]

        # Add retention options
        for key, value in options.items():
            if key.startswith("keep_") and value is not None:
                args.append(f"--{key.replace('_', '-')}")
                args.append(str(value))

        self._run_borg(args, repository)

    def get_repository_size(self, repository: str) -> int:
        """Get borg repository size.

        Args:
            repository: Borg repository path

        Returns:
            Repository size in bytes
        """
        try:
            result = self._run_borg(["info"], repository, capture_json=True)
            info = json.loads(result.stdout)
            # Borg info provides repository stats
            cache = info.get("cache", {})
            stats = cache.get("stats", {})
            unique_size = stats.get("unique_csize", 0)
            return int(unique_size) if unique_size is not None else 0
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
            logger.warning("Failed to get repository size, returning 0")
            return 0
