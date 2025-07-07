"""
CLI commands for Microsoft Dynamics & Power Platform Architecture Builder.

This module defines the command-line interface using click.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    import click
    from rich.console import Console

    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    logging.warning("Click library not available. CLI will be disabled.")

from models.architecture import DiagramConfig, DiagramFormat
from services.architecture_generator import ArchitectureGenerator
from services.diagram_exporter import DiagramExporter
from services.selection_service import SelectionService
from services.technology_catalog import get_catalog
from cli.prompts import InteractivePrompts

logger = logging.getLogger(__name__)
console = Console()


if not CLICK_AVAILABLE:
    # Provide dummy decorators if click is not available
    def click_command(*args, **kwargs):
        def decorator(f):
            return f

        return decorator

    def click_option(*args, **kwargs):
        def decorator(f):
            return f

        return decorator

    def click_argument(*args, **kwargs):
        def decorator(f):
            return f

        return decorator

    click_command = click_option = click_argument = lambda *a, **k: lambda f: f


class CLICommands:
    """
    Main CLI commands class for the architecture builder.

    This class organizes all the command-line interface functionality.
    """

    def __init__(self):
        """Initialize CLI commands."""
        self.catalog = get_catalog()
        self.selection_service = SelectionService(self.catalog)
        self.architecture_generator = ArchitectureGenerator(self.catalog)
        self.diagram_exporter = DiagramExporter()

    def run_interactive_mode(self) -> None:
        """
        Run the interactive mode for architecture building.

        This is the main interactive workflow that guides users through
        the process of selecting components and generating diagrams.
        """
        try:
            prompts = InteractivePrompts(self.catalog, self.selection_service)

            # Welcome screen
            prompts.welcome_screen()

            # Get architecture details
            name, description = prompts.prompt_architecture_name()

            # Create new technology stack
            self.selection_service.create_new_stack(name, description)

            # Main selection loop
            while True:
                # Select technology categories
                selected_categories = prompts.prompt_technology_categories()
                if not selected_categories:
                    console.print("[yellow]No categories selected. Exiting.[/yellow]")
                    return

                # Select components within each category
                all_selected_components = []
                for category in selected_categories:
                    component_ids = prompts.prompt_components_by_category(category)
                    all_selected_components.extend(component_ids)

                if not all_selected_components:
                    console.print("[yellow]No components selected.[/yellow]")
                    continue

                # Add selected components
                successful, failed = self.selection_service.add_multiple_components(
                    all_selected_components
                )

                if failed:
                    console.print(
                        f"[yellow]Some components could not be added: {len(failed)}[/yellow]"
                    )
                    for failure in failed:
                        console.print(f"  • {failure}")

                # Handle dependencies
                missing_deps = self.selection_service.get_missing_dependencies()
                if missing_deps:
                    dep_ids = prompts.prompt_resolve_dependencies(missing_deps)
                    if dep_ids:
                        self.selection_service.add_multiple_components(dep_ids)

                # Handle conflicts
                is_valid, errors = self.selection_service.validate_current_stack()
                if not is_valid:
                    conflict_errors = [e for e in errors if "conflicts" in e.lower()]
                    if conflict_errors:
                        continue_anyway = prompts.prompt_handle_conflicts(
                            conflict_errors
                        )
                        if not continue_anyway:
                            continue

                # Add integration flows
                suggested_flows = self.selection_service.generate_integration_flows()
                if suggested_flows:
                    selected_flow_ids = prompts.prompt_integration_flows(
                        suggested_flows
                    )
                    for flow in suggested_flows:
                        if flow.id in selected_flow_ids:
                            self.selection_service.add_integration_flow(flow)

                # Show summary and get next action
                prompts.display_selection_summary(self.selection_service)

                next_action = prompts.prompt_continue_or_modify()

                if next_action == "generate":
                    break
                elif next_action == "modify":
                    self._handle_modifications(prompts)
                elif next_action == "restart":
                    self.selection_service.clear_current_stack()
                    self.selection_service.create_new_stack(name, description)
                    continue
                elif next_action == "exit":
                    return

            # Generate diagram
            self._generate_diagram_interactive(prompts)

        except KeyboardInterrupt:
            console.print("\\n[yellow]Operation cancelled by user.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error in interactive mode: {e}[/red]")
            logger.exception("Error in interactive mode")

    def _handle_modifications(self, prompts: InteractivePrompts) -> None:
        """
        Handle modification operations in interactive mode.

        Args:
            prompts: Interactive prompts instance
        """
        while True:
            action = prompts.prompt_modification_options()

            if action == "add":
                # Add more components
                categories = prompts.prompt_technology_categories()
                for category in categories:
                    component_ids = prompts.prompt_components_by_category(category)
                    self.selection_service.add_multiple_components(component_ids)

            elif action == "remove":
                # Remove components
                current_components = self.selection_service.current_stack.components
                component_ids = prompts.prompt_components_to_remove(current_components)
                for comp_id in component_ids:
                    self.selection_service.remove_component(comp_id)

            elif action == "flows":
                # Add integration flows
                suggested_flows = self.selection_service.generate_integration_flows()
                selected_flow_ids = prompts.prompt_integration_flows(suggested_flows)
                for flow in suggested_flows:
                    if flow.id in selected_flow_ids:
                        self.selection_service.add_integration_flow(flow)

            elif action == "back":
                break

            # Show updated summary
            prompts.display_selection_summary(self.selection_service)

    def _generate_diagram_interactive(self, prompts: InteractivePrompts) -> None:
        """
        Generate diagram in interactive mode.

        Args:
            prompts: Interactive prompts instance
        """
        try:
            # Get diagram configuration
            config_dict = prompts.prompt_diagram_configuration()

            config = DiagramConfig(
                format=DiagramFormat(config_dict["format"]),
                filename=config_dict["filename"],
                output_directory=config_dict["output_directory"],
                width=config_dict["width"],
                height=config_dict["height"],
                show_descriptions=config_dict["show_descriptions"],
                color_by_category=config_dict["color_by_category"],
            )

            # Generate architecture
            prompts.display_generation_progress("Generating architecture model...")
            architecture = self.architecture_generator.generate_architecture(
                self.selection_service.current_stack
            )

            # Export diagram
            prompts.display_generation_progress("Creating diagram...")
            output_path, metadata = self.diagram_exporter.export_diagram(
                architecture, config
            )

            # Show success
            prompts.display_success_message(output_path, metadata)

        except Exception as e:
            prompts.display_error_message(str(e))
            logger.exception("Error generating diagram")

    def generate_from_components(
        self,
        component_ids: list[str],
        output_file: str,
        format: str = "png",
        name: str = "Generated Architecture",
        description: str = "",
    ) -> None:
        """
        Generate diagram from a list of component IDs (non-interactive).

        Args:
            component_ids: List of component IDs to include
            output_file: Output file path
            format: Output format
            name: Architecture name
            description: Architecture description
        """
        try:
            # Create technology stack
            self.selection_service.create_new_stack(name, description)

            # Add components
            successful, failed = self.selection_service.add_multiple_components(
                component_ids
            )

            if failed:
                console.print(
                    f"[yellow]Warning: {len(failed)} components could not be added[/yellow]"
                )
                for failure in failed:
                    console.print(f"  • {failure}")

            if not successful:
                console.print(
                    "[red]No valid components were added. Cannot generate diagram.[/red]"
                )
                return

            # Auto-resolve dependencies
            added_deps, dep_errors = self.selection_service.auto_resolve_dependencies()
            if added_deps > 0:
                console.print(
                    f"[green]Auto-added {added_deps} dependency components[/green]"
                )

            # Generate integration flows
            suggested_flows = self.selection_service.generate_integration_flows()
            for flow in suggested_flows:
                self.selection_service.add_integration_flow(flow)

            # Create diagram config
            output_path = Path(output_file)
            config = DiagramConfig(
                format=DiagramFormat(format),
                filename=output_path.stem,
                output_directory=str(output_path.parent),
            )

            # Generate architecture and diagram
            console.print("[blue]Generating architecture...[/blue]")
            architecture = self.architecture_generator.generate_architecture(
                self.selection_service.current_stack
            )

            console.print("[blue]Creating diagram...[/blue]")
            final_output_path, metadata = self.diagram_exporter.export_diagram(
                architecture, config
            )

            console.print(f"[green]✅ Diagram saved to: {final_output_path}[/green]")
            console.print(
                f"[dim]Components: {metadata.component_count}, "
                f"Integrations: {metadata.integration_count}, "
                f"Complexity: {metadata.complexity_score}/10[/dim]"
            )

        except Exception as e:
            console.print(f"[red]Error generating diagram: {e}[/red]")
            logger.exception("Error in non-interactive generation")

    def list_components(
        self, category: Optional[str] = None, search: Optional[str] = None
    ) -> None:
        """
        List available technology components.

        Args:
            category: Filter by category
            search: Search term
        """
        try:
            if search:
                components = self.catalog.search_components(search)
                console.print(f"[bold]Search results for '{search}':[/bold]")
            elif category:
                from models.technology import TechnologyCategory

                try:
                    cat_enum = TechnologyCategory(category.lower())
                    components = self.catalog.get_components_by_category(cat_enum)
                    console.print(f"[bold]Components in category '{category}':[/bold]")
                except ValueError:
                    console.print(f"[red]Invalid category: {category}[/red]")
                    console.print(
                        f"Valid categories: {[c.value for c in TechnologyCategory]}"
                    )
                    return
            else:
                components = self.catalog.get_all_components()
                console.print("[bold]All available components:[/bold]")

            if not components:
                console.print("[yellow]No components found.[/yellow]")
                return

            # Group by category for display
            by_category = {}
            for comp in components:
                cat = comp.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(comp)

            for category_name, comps in by_category.items():
                console.print(
                    f"\\n[cyan]{category_name.replace('_', ' ').title()}:[/cyan]"
                )
                for comp in sorted(comps, key=lambda x: x.name):
                    core_marker = " [yellow]*[/yellow]" if comp.is_core else ""
                    console.print(f"  • {comp.name}{core_marker}")
                    console.print(f"    ID: {comp.id}")
                    console.print(f"    Layer: {comp.layer.value}")
                    if comp.description:
                        desc = (
                            comp.description[:80] + "..."
                            if len(comp.description) > 80
                            else comp.description
                        )
                        console.print(f"    {desc}")

        except Exception as e:
            console.print(f"[red]Error listing components: {e}[/red]")
            logger.exception("Error listing components")

    def show_catalog_stats(self) -> None:
        """Display statistics about the technology catalog."""
        try:
            stats = self.catalog.get_catalog_statistics()

            console.print("[bold]Technology Catalog Statistics:[/bold]")
            console.print(f"  Total Components: {stats['total_components']}")
            console.print(f"  Core Components: {stats['core_components']}")

            console.print("\\n[bold]By Category:[/bold]")
            for key, value in stats.items():
                if (
                    key.endswith("_components")
                    and not key.startswith("total")
                    and not key.startswith("core")
                ):
                    category = key.replace("_components", "").replace("_", " ").title()
                    console.print(f"  {category}: {value}")

            console.print("\\n[bold]By Layer:[/bold]")
            for key, value in stats.items():
                if key.endswith("_layer_components"):
                    layer = (
                        key.replace("_layer_components", "").replace("_", " ").title()
                    )
                    console.print(f"  {layer}: {value}")

        except Exception as e:
            console.print(f"[red]Error showing stats: {e}[/red]")
            logger.exception("Error showing catalog stats")
