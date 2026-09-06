import sys
import click
import asyncio
from datetime import datetime

from src.config.manager import ConfigManager
from src.agent.orchestrator import create_agent
from src.observability.logger import get_logger
from src.utils.date_utils import get_last_complete_week, get_date_range

logger = get_logger(__name__)

@click.group()
def cli():
    """GROW Agent CLI"""
    pass

@cli.command()
@click.option('--start', type=click.DateTime(formats=["%Y-%m-%d"]), help="Start date (YYYY-MM-DD)")
@click.option('--end', type=click.DateTime(formats=["%Y-%m-%d"]), help="End date (YYYY-MM-DD)")
@click.option('--dry-run', is_flag=True, help="Run without persisting or delivering")
@click.option('--config', type=click.Path(exists=True), help="Path to config file")
def run(start, end, dry_run, config):
    """Execute the full weekly pipeline."""
    # Load config
    if config:
        config_obj = ConfigManager.load(config)
    else:
        config_obj = ConfigManager.load()
    
    # Setup dates
    if start and end:
        start_date, end_date = get_date_range(start, end)
    else:
        start_date, end_date = get_last_complete_week()

    click.echo(f"Running pipeline for {start_date.date()} to {end_date.date()} (dry-run: {dry_run})")
    
    # Initialize agent
    try:
        agent = create_agent(config_obj)
        # run the agent async
        report = asyncio.run(agent.run(start_date=start_date, end_date=end_date, dry_run=dry_run))
        
        click.echo("\n--- Execution Report ---")
        click.echo(f"Status: {report.status}")
        click.echo(f"Run ID: {report.run_id}")
        click.echo(f"Duration: {report.duration_seconds:.2f}s")
        if report.warnings:
            click.echo("Warnings:")
            for w in report.warnings:
                click.echo(f"  - {w}")
        if report.errors:
            click.echo("Errors:")
            for e in report.errors:
                click.echo(f"  - {e}")
                
        if report.status == "failed":
            sys.exit(1)
            
    except Exception as e:
        logger.exception("Pipeline failed unexpectedly", error=str(e))
        click.echo(f"Critical error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
def status():
    """Show last run status."""
    click.echo("Status command not fully implemented. Check logs or storage.")
    # Could load storage backend and get last run

@cli.command()
@click.option('--limit', default=5, help="Number of runs to show")
def history(limit):
    """Show recent run history."""
    click.echo(f"History command not fully implemented (limit: {limit}).")
    # Could list execution reports from storage if they were persisted

if __name__ == "__main__":
    cli()
