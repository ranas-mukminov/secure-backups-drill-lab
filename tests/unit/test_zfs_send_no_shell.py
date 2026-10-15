"""ZFS send-to-file must not use shell=True (command injection via paths)."""

from __future__ import annotations

from unittest.mock import MagicMock, mock_open, patch

from backup_orchestrator_observability.backends.zfs_backend import ZFSBackend


def test_backup_to_file_uses_popen_without_shell(tmp_path):
    backend = ZFSBackend()
    out = tmp_path / "stream.zfs"

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"", b"")

    with (
        patch.object(backend, "_run_zfs") as run_zfs,
        patch("backup_orchestrator_observability.backends.zfs_backend.subprocess.Popen") as popen,
        patch("builtins.open", mock_open()),
    ):
        run_zfs.return_value = MagicMock()
        popen.return_value = mock_proc

        result = backend.backup(
            sources=["tank/data"],
            repository=str(out),
            snapshot_name="backup-test",
        )

    assert result.success is True
    popen.assert_called_once()
    args, kwargs = popen.call_args
    assert args[0][0] == "zfs"
    assert kwargs.get("shell") in (None, False)
    assert ">" not in " ".join(args[0])
