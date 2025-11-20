"""ZFS send/receive backend implementation."""

import logging
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from backup_orchestrator_observability.backends.base import (
    BackupBackend,
    BackupResult,
    CheckResult,
    RestoreResult,
    Snapshot,
)

logger = logging.getLogger(__name__)


class ZFSBackend(BackupBackend):
    """ZFS send/receive wrapper for backup operations."""

    def _run_zfs(
        self, args: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run zfs command.

        Args:
            args: ZFS command arguments
            capture_output: Whether to capture stdout/stderr

        Returns:
            Completed Process with command result

        Raises:
            subprocess.CalledProcessError: If zfs command fails
        """
        cmd = ["zfs"] + args
        logger.debug(f"Running zfs command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=capture_output,
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
        """Perform ZFS snapshot and send.

        Args:
            sources: ZFS datasets to snapshot (usually single dataset)
            repository: Target dataset or file for zfs send
            **options: Additional options (incremental base, compression, etc.)

        Returns:
            BackupResult with send statistics
        """
        start_time = time.time()

        if not sources:
            return BackupResult(
                success=False,
                duration_seconds=0,
                error_message="No source dataset specified",
            )

        dataset = sources[0]  # ZFS typically backs up one dataset at a time
        snapshot_name = options.get(
            "snapshot_name",
            f"backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        )
        snapshot = f"{dataset}@{snapshot_name}"

        try:
            # Create snapshot
            self._run_zfs(["snapshot", snapshot])

            # Determine if incremental
            incremental_base = options.get("incremental_base")

            send_args = ["send"]

            if incremental_base:
                # Incremental send
                send_args.extend(["-i", f"{dataset}@{incremental_base}"])
            
            send_args.append(snapshot)

            # Determine target
            if repository.startswith("/"):
                # Send to file
                send_args.extend([">", repository])
                # Use shell for redirection
                send_cmd = f"zfs {' '.join(send_args)}"
                result = subprocess.run(
                    send_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                # Send to remote dataset (via SSH or direct)
                # For now, we'll assume direct local receive
                recv_cmd = ["zfs", "receive", "-F", repository]
                
                send_proc = subprocess.Popen(
                    ["zfs"] + send_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                
                recv_proc = subprocess.Popen(
                    recv_cmd,
                    stdin=send_proc.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                send_proc.stdout.close()
                recv_stdout, recv_stderr = recv_proc.communicate()
                
                if recv_proc.returncode != 0:
                    raise subprocess.CalledProcessError(
                        recv_proc.returncode, recv_cmd, stderr=recv_stderr
                    )

            duration = time.time() - start_time

            # Get snapshot size
            bytes_sent = self._get_snapshot_size(snapshot)

            return BackupResult(
                success=True,
                duration_seconds=duration,
                bytes_added=bytes_sent,
                bytes_processed=bytes_sent,
                snapshot_id=snapshot_name,
                metadata={"dataset": dataset, "snapshot": snapshot},
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            logger.error(f"ZFS send failed: {e.stderr}")
            return BackupResult(
                success=False,
                duration_seconds=duration,
                error_message=str(e.stderr) if e.stderr else str(e),
            )

    def _get_snapshot_size(self, snapshot: str) -> int:
        """Get snapshot size in bytes.

        Args:
            snapshot: Snapshot name (dataset@snapshot)

        Returns:
            Snapshot size in bytes
        """
        try:
            result = self._run_zfs(["get", "-Hp", "-o", "value", "used", snapshot])
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 0

    def check(self, repository: str, **options: Any) -> CheckResult:
        """Check ZFS dataset integrity (scrub).

        Args:
            repository: ZFS pool or dataset to check
            **options: Check options

        Returns:
            CheckResult with check status
        """
        start_time = time.time()

        # Extract pool name from dataset
        pool = repository.split("/")[0]

        errors = []
        warnings = []

        try:
            # Check pool status
            result = subprocess.run(
                ["zpool", "status", pool],
                capture_output=True,
                text=True,
                check=True,
            )

            duration = time.time() - start_time

            # Parse status for errors
            for line in result.stdout.split("\n"):
                if "DEGRADED" in line or "FAULTED" in line:
                    errors.append(line.strip())
                elif "errors:" in line and "No known data errors" not in line:
                    warnings.append(line.strip())

            return CheckResult(
                success=len(errors) == 0,
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
        """Restore from ZFS snapshot (receive).

        Args:
            repository: Source dataset or file
            snapshot_id: Snapshot name to restore
            target: Target dataset for receive
            **options: Restore options

        Returns:
            RestoreResult with restore statistics
        """
        start_time = time.time()

        try:
            snapshot = f"{repository}@{snapshot_id}"

            # Send snapshot and receive to target
            send_proc = subprocess.Popen(
                ["zfs", "send", snapshot],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            recv_proc = subprocess.Popen(
                ["zfs", "receive", "-F", target],
                stdin=send_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            send_proc.stdout.close()
            recv_stdout, recv_stderr = recv_proc.communicate()

            duration = time.time() - start_time

            if recv_proc.returncode != 0:
                return RestoreResult(
                    success=False,
                    duration_seconds=duration,
                    error_message=recv_stderr,
                )

            bytes_restored = self._get_snapshot_size(snapshot)

            return RestoreResult(
                success=True,
                duration_seconds=duration,
                bytes_restored=bytes_restored,
            )

        except (subprocess.CalledProcessError, OSError) as e:
            duration = time.time() - start_time
            return RestoreResult(
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )

    def list_snapshots(self, repository: str, **options: Any) -> List[Snapshot]:
        """List ZFS snapshots.

        Args:
            repository: ZFS dataset
            **options: List options

        Returns:
            List of Snapshot objects
        """
        try:
            result = self._run_zfs(
                ["list", "-t", "snapshot", "-H", "-o", "name,creation", repository]
            )

            snapshots = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                full_name = parts[0]  # dataset@snapshot
                creation_ts = int(parts[1])

                # Extract snapshot name
                if "@" in full_name:
                    dataset, snap_name = full_name.split("@", 1)
                    snapshots.append(
                        Snapshot(
                            id=snap_name,
                            timestamp=datetime.fromtimestamp(creation_ts),
                            hostname="",
                            paths=[dataset],
                        )
                    )

            return snapshots

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []

    def forget(
        self,
        repository: str,
        snapshot_ids: List[str],
        **options: Any,
    ) -> None:
        """Delete ZFS snapshots.

        Args:
            repository: ZFS dataset
            snapshot_ids: Snapshot names to delete
            **options: Delete options
        """
        for snap_name in snapshot_ids:
            snapshot = f"{repository}@{snap_name}"
            self._run_zfs(["destroy", snapshot])

    def prune(self, repository: str, **options: Any) -> None:
        """Prune ZFS snapshots (no-op, handled by forget).

        ZFS doesn't have a separate prune operation.

        Args:
            repository: ZFS dataset
            **options: Prune options
        """
        pass  # ZFS prunes space automatically when snapshots are destroyed

    def get_repository_size(self, repository: str) -> int:
        """Get ZFS dataset size.

        Args:
            repository: ZFS dataset

        Returns:
            Dataset used size in bytes
        """
        try:
            result = self._run_zfs(["get", "-Hp", "-o", "value", "used", repository])
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            logger.warning("Failed to get dataset size, returning 0")
            return 0
