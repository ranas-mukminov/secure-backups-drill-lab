"""Unit tests for job state management."""


from backup_orchestrator_observability.jobs import JobRegistry, JobState, JobStatus


def test_job_registration():
    """Test registering jobs in the registry."""
    registry = JobRegistry()

    registry.register_job("test-job")
    state = registry.get_state("test-job")

    assert state is not None
    assert state.job_name == "test-job"
    assert state.status == JobStatus.IDLE


def test_job_state_update_success():
    """Test updating job state after successful backup."""
    state = JobState(job_name="test")

    duration = 120.5
    bytes_transferred = 1024 * 1024 * 500  # 500 MB
    repo_size = 1024 * 1024 * 1024 * 10  # 10 GB

    state.update_success(duration, bytes_transferred, repo_size)

    assert state.status == JobStatus.SUCCESS
    assert state.duration_seconds == duration
    assert state.bytes_transferred == bytes_transferred
    assert state.repository_size_bytes == repo_size
    assert state.last_success is not None
    assert state.error_message is None


def test_job_state_update_failure():
    """Test updating job state after failed backup."""
    state = JobState(job_name="test")

    error_msg = "Backup failed: connection timeout"
    state.update_failure(error_msg)

    assert state.status == JobStatus.FAILED
    assert state.error_message == error_msg
    assert state.error_count == 1
    assert state.last_run is not None


def test_job_state_update_verification():
    """Test updating job state after verification."""
    state = JobState(job_name="test")

    # Successful verification
    state.update_verification(success=True)
    assert state.verification_success is True
    assert state.last_verification is not None

    # Failed verification
    state.update_verification(success=False, error="Checksum mismatch")
    assert state.verification_success is False
    assert state.error_message == "Checksum mismatch"


def test_registry_thread_safety():
    """Test that registry operations are thread-safe."""
    import threading

    registry = JobRegistry()
    registry.register_job("concurrent-job")

    def update_state():
        for _i in range(100):
            registry.update_state("concurrent-job", status=JobStatus.RUNNING)
            registry.update_state("concurrent-job", status=JobStatus.SUCCESS)

    threads = [threading.Thread(target=update_state) for _ in range(5)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Should not crash and state should be consistent
    state = registry.get_state("concurrent-job")
    assert state is not None


def test_registry_get_all_states():
    """Test retrieving all job states."""
    registry = JobRegistry()

    registry.register_job("job1")
    registry.register_job("job2")
    registry.register_job("job3")

    all_states = registry.get_all_states()

    assert len(all_states) == 3
    assert "job1" in all_states
    assert "job2" in all_states
    assert "job3" in all_states
