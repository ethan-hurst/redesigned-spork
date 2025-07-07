"""
Interactive prompts for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides interactive CLI prompts for user input using questionary.
"""

import logging
from typing import Any

try:
    import questionary
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    INTERACTIVE_AVAILABLE = True
except ImportError:
    INTERACTIVE_AVAILABLE = False
    logging.warning("Interactive libraries not available. CLI will be limited.")

from models.technology import TechnologyCategory, TechnologyComponent
from services.selection_service import SelectionService
from services.technology_catalog import TechnologyCatalog

logger = logging.getLogger(__name__)


class InteractivePromptsError(Exception):
    """Custom exception for interactive prompt operations."""

    pass


class InteractivePrompts:
    """
    Class for handling interactive CLI prompts.

    This class provides a rich interactive experience for selecting
    technology components and configuring diagram generation.
    """

    def __init__(self, catalog: TechnologyCatalog, selection_service: SelectionService):
        """
        Initialize interactive prompts.

        Args:
            catalog: Technology catalog for component data
            selection_service: Service for managing selections
        """
        if not INTERACTIVE_AVAILABLE:
            raise InteractivePromptsError("Interactive libraries not available")

        self.catalog = catalog
        self.selection_service = selection_service
        self.console = Console()

    def welcome_screen(self) -> None:
        """Display welcome screen with information about the tool."""
        self.console.print(
            Panel.fit(
                "[bold blue]Microsoft Dynamics & Power Platform Architecture Builder[/bold blue]\\n\\n"
                "Generate professional architectural diagrams for your Microsoft technology stack.\\n\\n"
                "[dim]This tool helps you select from Microsoft technologies and creates "
                "comprehensive architectural diagrams following best practices.[/dim]",
                border_style="blue",
            )
        )

    def prompt_architecture_name(self) -> tuple[str, str]:
        """
        Prompt for architecture name and description.

        Returns:
            Tuple of (name, description)
        """
        name = questionary.text(
            "What would you like to name your architecture?",
            default="My Microsoft Architecture",
        ).ask()

        description = questionary.text(
            "Provide a brief description (optional):", default=""
        ).ask()

        return name or "My Microsoft Architecture", description or ""

    def prompt_technology_categories(self) -> list[TechnologyCategory]:
        """
        Prompt user to select technology categories.

        Returns:
            List of selected technology categories
        """
        category_choices = []
        for category in TechnologyCategory:
            count = len(self.catalog.get_components_by_category(category))
            choice_name = (
                f"{category.value.replace('_', ' ').title()} ({count} components)"
            )
            category_choices.append(
                questionary.Choice(title=choice_name, value=category)
            )

        selected = questionary.checkbox(
            "Select the technology categories you want to explore:",
            choices=category_choices,
        ).ask()

        return selected or []

    def prompt_components_by_category(self, category: TechnologyCategory) -> list[str]:
        """
        Prompt user to select components within a category.

        Args:
            category: The technology category to select from

        Returns:
            List of selected component IDs
        """
        components = self.catalog.get_components_by_category(category)
        if not components:
            return []

        # Group by subcategory for better organization
        subcategories = {}
        for component in components:
            if component.subcategory not in subcategories:
                subcategories[component.subcategory] = []
            subcategories[component.subcategory].append(component)

        selected_components = []

        for subcategory, subcat_components in subcategories.items():
            if len(subcategories) > 1:
                self.console.print(
                    f"\\n[bold]{subcategory.replace('_', ' ').title()}[/bold]"
                )

            choices = []
            for component in subcat_components:
                # Create choice with component info
                title = f"{component.name}"
                if component.is_core:
                    title += " [bold yellow]*[/bold yellow]"

                choices.append(
                    questionary.Choice(
                        title=title,
                        value=component.id,
                        checked=component.is_core,  # Pre-select core components
                    )
                )

            prompt_text = f"Select {category.value.replace('_', ' ')} components:"
            if len(subcategories) > 1:
                prompt_text = f"Select {subcategory.replace('_', ' ')} components:"

            selected = questionary.checkbox(prompt_text, choices=choices).ask()

            if selected:
                selected_components.extend(selected)

        return selected_components

    def prompt_resolve_dependencies(
        self, missing_deps: list[TechnologyComponent]
    ) -> list[str]:
        """
        Prompt user to resolve missing dependencies.

        Args:
            missing_deps: List of missing dependency components

        Returns:
            List of component IDs to add
        """
        if not missing_deps:
            return []

        self.console.print("\\n[yellow]Missing Dependencies Detected[/yellow]")

        choices = []
        for dep in missing_deps:
            title = f"{dep.name} - {dep.description[:60]}..."
            choices.append(questionary.Choice(title=title, value=dep.id, checked=True))

        selected = questionary.checkbox(
            "The following dependencies are recommended. Select which to add:",
            choices=choices,
        ).ask()

        return selected or []

    def prompt_handle_conflicts(self, conflicts: list[str]) -> bool:
        """
        Prompt user to handle component conflicts.

        Args:
            conflicts: List of conflict error messages

        Returns:
            True if user wants to continue despite conflicts
        """
        if not conflicts:
            return True

        self.console.print("\\n[red]Component Conflicts Detected[/red]")
        for conflict in conflicts:
            self.console.print(f"  • {conflict}")

        return questionary.confirm(
            "Do you want to continue with these conflicts? (You can resolve them later)",
            default=False,
        ).ask()

    def prompt_integration_flows(self, suggested_flows: list) -> list[str]:
        """
        Prompt user to select integration flows.

        Args:
            suggested_flows: List of suggested integration flow objects

        Returns:
            List of selected flow IDs
        """
        if not suggested_flows:
            return []

        self.console.print("\\n[green]Suggested Integration Flows[/green]")

        choices = []
        for flow in suggested_flows:
            title = f"{flow.name} ({flow.integration_pattern.value.replace('_', ' ').title()})"
            choices.append(questionary.Choice(title=title, value=flow.id, checked=True))

        selected = questionary.checkbox(
            "Select integration flows to include:", choices=choices
        ).ask()

        return selected or []

    def prompt_diagram_configuration(self) -> dict[str, Any]:
        """
        Prompt user for diagram configuration options.

        Returns:
            Dictionary with diagram configuration
        """
        config = {}

        # Output format
        format_choices = [
            questionary.Choice("PNG (Recommended)", "png"),
            questionary.Choice("SVG (Vector)", "svg"),
            questionary.Choice("PDF (Print)", "pdf"),
            questionary.Choice("JPG (Photo)", "jpg"),
        ]

        config["format"] = questionary.select(
            "Select output format:", choices=format_choices, default="png"
        ).ask()

        # Filename
        config["filename"] = questionary.text(
            "Enter filename (without extension):", default="microsoft_architecture"
        ).ask()

        # Output directory
        config["output_directory"] = questionary.text(
            "Enter output directory:", default="output"
        ).ask()

        # Advanced options
        show_advanced = questionary.confirm(
            "Configure advanced diagram options?", default=False
        ).ask()

        if show_advanced:
            config["show_descriptions"] = questionary.confirm(
                "Show component descriptions in diagram?", default=False
            ).ask()

            config["color_by_category"] = questionary.confirm(
                "Color components by category?", default=True
            ).ask()

            # Diagram size
            size_choices = [
                questionary.Choice("Standard (1200x800)", (1200, 800)),
                questionary.Choice("Large (1600x1200)", (1600, 1200)),
                questionary.Choice("Extra Large (2000x1500)", (2000, 1500)),
                questionary.Choice("Custom", "custom"),
            ]

            size_choice = questionary.select(
                "Select diagram size:", choices=size_choices, default=(1200, 800)
            ).ask()

            if size_choice == "custom":
                config["width"] = questionary.text(
                    "Enter width in pixels:",
                    default="1200",
                    validate=lambda x: x.isdigit() and int(x) > 0,
                ).ask()
                config["height"] = questionary.text(
                    "Enter height in pixels:",
                    default="800",
                    validate=lambda x: x.isdigit() and int(x) > 0,
                ).ask()
                config["width"] = int(config["width"])
                config["height"] = int(config["height"])
            else:
                config["width"], config["height"] = size_choice
        else:
            # Use defaults
            config["show_descriptions"] = False
            config["color_by_category"] = True
            config["width"] = 1200
            config["height"] = 800

        return config

    def display_selection_summary(self, selection_service: SelectionService) -> None:
        """
        Display a summary of the current selection.

        Args:
            selection_service: Service containing the current selection
        """
        if not selection_service.current_stack:
            self.console.print("[red]No active technology stack[/red]")
            return

        summary = selection_service.get_stack_summary()

        # Create summary table
        table = Table(
            title="Architecture Summary", show_header=True, header_style="bold blue"
        )
        table.add_column("Aspect", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Name", summary["name"])
        table.add_row("Components", str(summary["component_count"]))
        table.add_row("Integration Flows", str(summary["integration_flow_count"]))
        table.add_row("Valid", "✓" if summary["is_valid"] else "✗")

        if summary["missing_dependencies"] > 0:
            table.add_row("Missing Dependencies", str(summary["missing_dependencies"]))

        self.console.print(table)

        # Show components by category
        if summary["categories"]:
            self.console.print("\\n[bold]Components by Category:[/bold]")
            for category, count in summary["categories"].items():
                self.console.print(f"  • {category.replace('_', ' ').title()}: {count}")

        # Show layers
        if summary["layers"]:
            self.console.print("\\n[bold]Components by Layer:[/bold]")
            for layer, count in summary["layers"].items():
                self.console.print(f"  • {layer.replace('_', ' ').title()}: {count}")

    def prompt_continue_or_modify(self) -> str:
        """
        Prompt user to continue or modify the current selection.

        Returns:
            User choice: 'generate', 'modify', or 'exit'
        """
        choices = [
            questionary.Choice("Generate Diagram", "generate"),
            questionary.Choice("Modify Selection", "modify"),
            questionary.Choice("Start Over", "restart"),
            questionary.Choice("Exit", "exit"),
        ]

        return questionary.select(
            "What would you like to do next?", choices=choices
        ).ask()

    def prompt_modification_options(self) -> str:
        """
        Prompt user for modification options.

        Returns:
            Modification choice
        """
        choices = [
            questionary.Choice("Add Components", "add"),
            questionary.Choice("Remove Components", "remove"),
            questionary.Choice("Add Integration Flows", "flows"),
            questionary.Choice("Back to Main Menu", "back"),
        ]

        return questionary.select(
            "What would you like to modify?", choices=choices
        ).ask()

    def prompt_components_to_remove(
        self, current_components: list[TechnologyComponent]
    ) -> list[str]:
        """
        Prompt user to select components to remove.

        Args:
            current_components: List of currently selected components

        Returns:
            List of component IDs to remove
        """
        if not current_components:
            self.console.print("[yellow]No components to remove[/yellow]")
            return []

        choices = []
        for component in current_components:
            title = f"{component.name} ({component.category.value})"
            choices.append(questionary.Choice(title=title, value=component.id))

        selected = questionary.checkbox(
            "Select components to remove:", choices=choices
        ).ask()

        return selected or []

    def display_generation_progress(self, message: str) -> None:
        """
        Display progress message during diagram generation.

        Args:
            message: Progress message to display
        """
        self.console.print(f"[blue]⚙️  {message}[/blue]")

    def display_success_message(self, output_path: str, metadata: Any) -> None:
        """
        Display success message after diagram generation.

        Args:
            output_path: Path to the generated diagram
            metadata: Diagram metadata object
        """
        self.console.print(
            Panel(
                f"[bold green]✅ Diagram Generated Successfully![/bold green]\\n\\n"
                f"📁 File: {output_path}\\n"
                f"📊 Components: {metadata.component_count}\\n"
                f"🔗 Integrations: {metadata.integration_count}\\n"
                f"⚡ Complexity: {metadata.complexity_score}/10\\n"
                f"⏱️  Generation Time: {metadata.generation_time_seconds:.2f}s",
                border_style="green",
            )
        )

    def display_error_message(self, error: str) -> None:
        """
        Display error message.

        Args:
            error: Error message to display
        """
        self.console.print(
            Panel(f"[bold red]❌ Error[/bold red]\\n\\n{error}", border_style="red")
        )
