"""
Main entry point for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides the command-line interface for the architecture builder tool.
"""

import logging
import sys
from typing import Optional

try:
    import click
    from rich.console import Console
    from rich.logging import RichHandler

    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    print(
        "Error: Required libraries not available. Please install with: pip install -r requirements.txt"
    )
    sys.exit(1)

from cli.commands import CLICommands
from services.technology_catalog import get_catalog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool) -> None:
    """
    Microsoft Dynamics & Power Platform Architecture Builder.

    Generate professional architectural diagrams for your Microsoft technology stack.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")


@cli.command()
def interactive() -> None:
    """
    Run the interactive architecture builder.

    This launches an interactive wizard that guides you through selecting
    technology components and generating architectural diagrams.
    """
    try:
        cli_commands = CLICommands()
        cli_commands.run_interactive_mode()
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Error in interactive mode")
        sys.exit(1)


@cli.command()
@click.option(
    "--components",
    "-c",
    required=True,
    help="Comma-separated list of component IDs to include",
)
@click.option("--output", "-o", required=True, help="Output file path for the diagram")
@click.option(
    "--format",
    "-f",
    default="png",
    type=click.Choice(["png", "svg", "pdf", "jpg", "vsdx"]),
    help="Output format (default: png)",
)
@click.option(
    "--name",
    "-n",
    default="Generated Architecture",
    help="Architecture name (default: Generated Architecture)",
)
@click.option("--description", "-d", default="", help="Architecture description")
def generate(
    components: str, output: str, format: str, name: str, description: str
) -> None:
    """
    Generate architecture diagram from component list.

    Example:
        dynamics-arch-builder generate -c "power_apps_canvas,dataverse,power_bi" -o "my_arch.png"
    """
    try:
        component_ids = [comp.strip() for comp in components.split(",")]

        cli_commands = CLICommands()
        cli_commands.generate_from_components(
            component_ids=component_ids,
            output_file=output,
            format=format,
            name=name,
            description=description,
        )
    except Exception as e:
        console.print(f"[red]Error generating diagram: {e}[/red]")
        logger.exception("Error in generate command")
        sys.exit(1)


@cli.command()
@click.option(
    "--category",
    "-c",
    help="Filter by category (power_platform, dynamics_365, azure_services, security_ops)",
)
@click.option("--search", "-s", help="Search for components by name or description")
def list_components(category: Optional[str], search: Optional[str]) -> None:
    """
    List available technology components.

    Examples:
        dynamics-arch-builder list-components
        dynamics-arch-builder list-components --category power_platform
        dynamics-arch-builder list-components --search "power apps"
    """
    try:
        cli_commands = CLICommands()
        cli_commands.list_components(category=category, search=search)
    except Exception as e:
        console.print(f"[red]Error listing components: {e}[/red]")
        logger.exception("Error in list-components command")
        sys.exit(1)


@cli.command()
def stats() -> None:
    """
    Show technology catalog statistics.

    Displays information about the number of components by category and layer.
    """
    try:
        cli_commands = CLICommands()
        cli_commands.show_catalog_stats()
    except Exception as e:
        console.print(f"[red]Error showing statistics: {e}[/red]")
        logger.exception("Error in stats command")
        sys.exit(1)


@cli.command()
def validate() -> None:
    """
    Validate the technology catalog and system requirements.

    Checks that all required dependencies are installed and the catalog is valid.
    """
    try:
        console.print("[blue]Validating system requirements...[/blue]")

        # Check graphviz
        import subprocess

        try:
            result = subprocess.run(["dot", "-V"], capture_output=True, text=True)
            if result.returncode == 0:
                console.print("[green]✓[/green] Graphviz is installed")
            else:
                console.print("[red]✗[/red] Graphviz not working properly")
        except FileNotFoundError:
            console.print(
                "[red]✗[/red] Graphviz not found. Install with: sudo apt-get install graphviz"
            )

        # Check diagrams library
        try:
            import diagrams

            console.print("[green]✓[/green] Diagrams library available")
        except ImportError:
            console.print("[red]✗[/red] Diagrams library not available")

        # Check interactive libraries
        try:
            import questionary
            import rich

            console.print("[green]✓[/green] Interactive libraries available")
        except ImportError:
            console.print("[red]✗[/red] Interactive libraries not available")

        # Validate catalog
        console.print("[blue]Validating technology catalog...[/blue]")
        catalog = get_catalog()
        stats = catalog.get_catalog_statistics()

        if stats["total_components"] > 0:
            console.print(
                f"[green]✓[/green] Catalog loaded with {stats['total_components']} components"
            )
        else:
            console.print("[red]✗[/red] No components found in catalog")

        console.print("[green]Validation complete![/green]")

    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        logger.exception("Error in validate command")
        sys.exit(1)


@cli.command()
def download_icons() -> None:
    """
    Download official Microsoft icons for use in diagrams.
    
    This downloads the official Power Platform and Azure icons from Microsoft
    for use in architectural diagrams.
    """
    try:
        console.print("[blue]Downloading Microsoft icons...[/blue]")
        
        cli_commands = CLICommands()
        success = cli_commands.diagram_exporter.download_microsoft_icons()
        
        if success:
            console.print("[green]✓[/green] Microsoft icons downloaded successfully")
            
            # Show available icons
            available = cli_commands.diagram_exporter.list_available_icons()
            if available:
                console.print("\n[bold]Available icon categories:[/bold]")
                for category, icons in available.items():
                    console.print(f"  {category}: {len(icons)} icons")
        else:
            console.print("[red]✗[/red] Failed to download Microsoft icons")
            console.print("[yellow]Note: Some icons may require manual download from Microsoft[/yellow]")

    except Exception as e:
        console.print(f"[red]Error downloading icons: {e}[/red]")
        logger.exception("Error in download-icons command")
        sys.exit(1)


@cli.command()
def cache_stats() -> None:
    """
    Show cache statistics and memory usage information.
    
    Displays information about diagram cache, icon cache, and current memory usage.
    """
    try:
        console.print("[blue]Cache and Memory Statistics[/blue]")
        
        from services.cache_manager import get_cache_manager
        from utils.memory_optimizer import get_memory_monitor
        
        # Get cache statistics
        cache_manager = get_cache_manager()
        cache_stats = cache_manager.get_cache_stats()
        
        console.print("\n[bold]Cache Statistics:[/bold]")
        console.print(f"  Memory cache entries: {cache_stats.get('memory_cache_size', 0)}")
        console.print(f"  Diagram cache files: {cache_stats.get('diagram_cache_files', 0)}")
        console.print(f"  Icon cache files: {cache_stats.get('icon_cache_files', 0)}")
        console.print(f"  Metadata cache files: {cache_stats.get('metadata_cache_files', 0)}")
        
        # Cache sizes
        cache_sizes = cache_stats.get('cache_size_bytes', {})
        total_size_mb = cache_stats.get('total_cache_size_bytes', 0) / 1024 / 1024
        console.print(f"\n[bold]Cache Sizes:[/bold]")
        console.print(f"  Diagrams: {cache_sizes.get('diagrams', 0) / 1024 / 1024:.1f} MB")
        console.print(f"  Icons: {cache_sizes.get('icons', 0) / 1024 / 1024:.1f} MB")
        console.print(f"  Metadata: {cache_sizes.get('metadata', 0) / 1024 / 1024:.1f} MB")
        console.print(f"  Total: {total_size_mb:.1f} MB")
        
        # Memory usage
        memory_monitor = get_memory_monitor()
        memory_info = memory_monitor.get_memory_info()
        
        if memory_info:
            console.print(f"\n[bold]Memory Usage:[/bold]")
            console.print(f"  Current: {memory_info.get('rss_mb', 0):.1f} MB ({memory_info.get('percent', 0):.1f}%)")
            console.print(f"  Available: {memory_info.get('available_mb', 0):.1f} MB")
            console.print(f"  Total: {memory_info.get('total_mb', 0):.1f} MB")

    except Exception as e:
        console.print(f"[red]Error getting cache/memory statistics: {e}[/red]")
        logger.exception("Error in cache-stats command")
        sys.exit(1)


@cli.command()
def clear_cache() -> None:
    """
    Clear all caches to free up disk space.
    
    This will remove all cached diagrams, icons, and metadata.
    """
    try:
        console.print("[blue]Clearing caches...[/blue]")
        
        from services.cache_manager import get_cache_manager
        
        cache_manager = get_cache_manager()
        success = cache_manager.clear_cache("all")
        
        if success:
            console.print("[green]✓[/green] All caches cleared successfully")
        else:
            console.print("[red]✗[/red] Failed to clear caches")

    except Exception as e:
        console.print(f"[red]Error clearing caches: {e}[/red]")
        logger.exception("Error in clear-cache command")
        sys.exit(1)


@cli.command()
def create_template() -> None:
    """
    Create a Visio template with Microsoft branding and styling.
    
    This creates a .vsdx template file that can be used as a starting point
    for creating Microsoft architecture diagrams in Visio.
    """
    try:
        console.print("[blue]Creating Visio template...[/blue]")
        
        cli_commands = CLICommands()
        template_path = cli_commands.diagram_exporter.create_visio_template()
        
        console.print(f"[green]✓[/green] Visio template created: {template_path}")
        console.print("[dim]You can open this template in Microsoft Visio to create custom diagrams[/dim]")

    except Exception as e:
        console.print(f"[red]Error creating template: {e}[/red]")
        logger.exception("Error in create-template command")
        sys.exit(1)


@cli.command()
@click.option("--all", "show_all", is_flag=True, help="Show all available examples")
def examples(show_all: bool) -> None:
    """
    Show usage examples and sample component combinations.
    """
    console.print(
        "[bold blue]Microsoft Dynamics & Power Platform Architecture Builder Examples[/bold blue]\\n"
    )

    examples_list = [
        {
            "name": "Simple Power Platform Stack",
            "description": "Basic Power Platform components with Dataverse",
            "components": "power_apps_canvas,dataverse,power_automate,power_bi",
            "command": 'dynamics-arch-builder generate -c "power_apps_canvas,dataverse,power_automate,power_bi" -o "power_platform.png"',
        },
        {
            "name": "Dynamics 365 Customer Service",
            "description": "Customer service solution with omnichannel support",
            "components": "dynamics_365_customer_service,dataverse,power_automate,teams_channel,azure_ad",
            "command": 'dynamics-arch-builder generate -c "dynamics_365_customer_service,dataverse,power_automate,teams_channel,azure_ad" -o "customer_service.png"',
        },
        {
            "name": "Enterprise Integration",
            "description": "Large-scale integration with Azure services",
            "components": "power_automate,azure_logic_apps,azure_service_bus,azure_functions,dataverse,azure_ad,azure_key_vault",
            "command": 'dynamics-arch-builder generate -c "power_automate,azure_logic_apps,azure_service_bus,azure_functions,dataverse,azure_ad,azure_key_vault" -o "enterprise.png"',
        },
    ]

    if not show_all:
        examples_list = examples_list[:2]  # Show only first 2 examples by default

    for i, example in enumerate(examples_list, 1):
        console.print(f"[bold cyan]{i}. {example['name']}[/bold cyan]")
        console.print(f"   {example['description']}")
        console.print(f"   Components: {example['components']}")
        console.print("   [dim]Command:[/dim]")
        console.print(f"   {example['command']}")
        console.print()

    if not show_all and len(examples_list) > 2:
        console.print("[dim]Use --all to see more examples[/dim]")

    console.print("[bold]Interactive Mode:[/bold]")
    console.print("dynamics-arch-builder interactive")
    console.print("   Launch the interactive wizard for guided component selection\\n")

    console.print("[bold]List Components:[/bold]")
    console.print("dynamics-arch-builder list-components --category power_platform")
    console.print("dynamics-arch-builder list-components --search 'dynamics 365'\\n")


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        logger.exception("Unexpected error in main")
        sys.exit(1)


if __name__ == "__main__":
    main()
