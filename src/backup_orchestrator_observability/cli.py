"""Command-line interface for backup orchestrator."""

import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from backup_orchestrator_observability.config import load_config

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level",
)
def main(log_level: str) -> None:
    """Backup Orchestrator - Secure backup management with observability."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to configuration file",
)
def run(config: Path) -> None:
    """Start the backup orchestrator daemon."""
    console.print("[bold green]Starting backup orchestrator[/bold green]")
    console.print(f"Config: {config}")

    try:
        cfg = load_config(config)
        console.print(f"Loaded {len(cfg.jobs)} job(s)")

        # TODO: Implement scheduler initialization and main loop
        console.print("[yellow]Scheduler implementation pending - see scheduler.py[/yellow]")
        console.print("Press Ctrl+C to stop")

        # Placeholder - actual implementation would start APScheduler here
        import time

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down...[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument("job_name")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to configuration file",
)
def exec(job_name: str, config: Path) -> None:
    """Execute a backup job immediately."""
    console.print(f"[bold green]Executing job: {job_name}[/bold green]")

    try:
        cfg = load_config(config)

        job_config = next((j for j in cfg.jobs if j.name == job_name), None)
        if not job_config:
            console.print(f"[bold red]Job '{job_name}' not found[/bold red]")
            sys.exit(1)

        console.print(f"Backend: {job_config.backend}")
        console.print(f"Sources: {', '.join(job_config.sources)}")
        console.print(f"Repository: {job_config.repository}")

        # TODO: Implement actual job execution
        console.print("[yellow]Job execution implementation pending - see scheduler.py[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument("job_name")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to configuration file",
)
def verify(job_name: str, config: Path) -> None:
    """Verify a backup repository."""
    console.print(f"[bold green]Verifying job: {job_name}[/bold green]")

    try:
        cfg = load_config(config)

        job_config = next((j for j in cfg.jobs if j.name == job_name), None)
        if not job_config:
            console.print(f"[bold red]Job '{job_name}' not found[/bold red]")
            sys.exit(1)

        # TODO: Implement verification
        console.print("[yellow]Verification implementation pending - see verify.py[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@main.command("list-jobs")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to configuration file",
)
def list_jobs(config: Path) -> None:
    """List all configured backup jobs."""
    try:
        cfg = load_config(config)

        table = Table(title="Backup Jobs")
        table.add_column("Name", style="cyan")
        table.add_column("Backend", style="magenta")
        table.add_column("Schedule", style="green")
        table.add_column("RPO (hours)", style="yellow")
        table.add_column("Enabled", style="blue")

        for job in cfg.jobs:
            table.add_row(
                job.name,
                job.backend.value,
                job.schedule,
                str(job.rpo_hours),
                "✓" if job.enabled else "✗",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@main.command("config")
@click.argument("action", type=click.Choice(["validate", "show"]))
@click.argument("config_path", type=click.Path(exists=True, path_type=Path))
def config_cmd(action: str, config_path: Path) -> None:
    """Validate or show configuration."""
    try:
        cfg = load_config(config_path)

        if action == "validate":
            console.print("[bold green]✓ Configuration is valid[/bold green]")
            console.print(f"Jobs: {len(cfg.jobs)}")
            console.print(f"Metrics port: {cfg.metrics.port}")

        elif action == "show":
            import yaml

            console.print(yaml.safe_dump(cfg.model_dump(exclude_none=True)))

    except Exception as e:
        console.print(f"[bold red]✗ Invalid configuration:[/bold red] {e}")
        sys.exit(1)


@main.command()
def version() -> None:
    """Show version information."""
    from backup_orchestrator_observability import __version__

    console.print(f"Backup Orchestrator v{__version__}")
    console.print("Author: Ranas Mukminov (https://run-as-daemon.ru)")
    console.print("License: Apache-2.0")


if __name__ == "__main__":
    main()
