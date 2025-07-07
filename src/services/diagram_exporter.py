"""
Diagram exporter service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides functionality for generating visual diagrams from architecture models.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# Diagram generation imports
def _check_diagrams_availability():
    """Check if diagrams library is available and import necessary classes."""
    try:
        from diagrams import Cluster, Diagram, Edge
        from diagrams.azure.analytics import (
            AnalysisServices,  # Using AnalysisServices as PowerBI substitute
        )
        from diagrams.azure.compute import FunctionApps
        from diagrams.azure.database import CosmosDb
        from diagrams.azure.devops import ApplicationInsights
        from diagrams.azure.identity import ActiveDirectory
        from diagrams.azure.integration import EventGridTopics, LogicApps, ServiceBus
        from diagrams.azure.security import KeyVaults
        from diagrams.custom import Custom

        return True, {
            "Diagram": Diagram,
            "Edge": Edge,
            "Cluster": Cluster,
            "PowerBi": AnalysisServices,
            "FunctionApps": FunctionApps,
            "CosmosDb": CosmosDb,
            "ApplicationInsights": ApplicationInsights,
            "ActiveDirectory": ActiveDirectory,
            "EventGrid": EventGridTopics,
            "LogicApps": LogicApps,
            "ServiceBus": ServiceBus,
            "KeyVault": KeyVaults,
            "Custom": Custom,
        }
    except ImportError:
        # Create dummy classes for when diagrams is not available
        class Diagram:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        class Edge:
            def __init__(self, *args, **kwargs):
                pass

        class Cluster:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        def dummy_class(x):
            return None
        return False, {
            "Diagram": Diagram,
            "Edge": Edge,
            "Cluster": Cluster,
            "PowerBi": dummy_class,
            "FunctionApps": dummy_class,
            "CosmosDb": dummy_class,
            "ApplicationInsights": dummy_class,
            "ActiveDirectory": dummy_class,
            "EventGrid": dummy_class,
            "LogicApps": dummy_class,
            "ServiceBus": dummy_class,
            "KeyVault": dummy_class,
            "Custom": dummy_class,
        }


# Initialize diagrams availability and classes
DIAGRAMS_AVAILABLE, DIAGRAM_CLASSES = _check_diagrams_availability()

# Make classes available at module level for backwards compatibility
Diagram = DIAGRAM_CLASSES["Diagram"]
Edge = DIAGRAM_CLASSES["Edge"]
Cluster = DIAGRAM_CLASSES["Cluster"]
PowerBi = DIAGRAM_CLASSES["PowerBi"]
FunctionApps = DIAGRAM_CLASSES["FunctionApps"]
CosmosDb = DIAGRAM_CLASSES["CosmosDb"]
ApplicationInsights = DIAGRAM_CLASSES["ApplicationInsights"]
ActiveDirectory = DIAGRAM_CLASSES["ActiveDirectory"]
EventGrid = DIAGRAM_CLASSES["EventGrid"]
LogicApps = DIAGRAM_CLASSES["LogicApps"]
ServiceBus = DIAGRAM_CLASSES["ServiceBus"]
KeyVault = DIAGRAM_CLASSES["KeyVault"]
Custom = DIAGRAM_CLASSES["Custom"]

from models.architecture import Architecture, DiagramConfig, DiagramMetadata
from models.technology import TechnologyCategory
from services.icon_manager import get_icon_manager
from services.visio_exporter import get_visio_exporter

logger = logging.getLogger(__name__)


class DiagramExportError(Exception):
    """Custom exception for diagram export operations."""

    pass


class DiagramExporter:
    """
    Service class for exporting architecture diagrams.

    This class handles the conversion of architecture models into visual diagrams
    using the diagrams library.
    """

    def __init__(self):
        """Initialize the diagram exporter."""
        # Check diagrams availability dynamically
        self.diagrams_available, self.diagram_classes = _check_diagrams_availability()

        # Component to diagram node mapping
        self.component_mappings = self._initialize_component_mappings()
        
        # Initialize icon manager and Visio exporter
        self.icon_manager = get_icon_manager()
        self.visio_exporter = get_visio_exporter()

    def _initialize_component_mappings(self) -> dict[str, Any]:
        """
        Initialize mappings from component IDs to diagram node types.

        Returns:
            Dictionary mapping component IDs to diagram node classes
        """
        if not self.diagrams_available:
            return {}

        return {
            # Power Platform
            "power_bi": self.diagram_classes["PowerBi"],
            "dataverse": self.diagram_classes[
                "CosmosDb"
            ],  # Using CosmosDB as closest equivalent
            # Azure Services
            "azure_functions": self.diagram_classes["FunctionApps"],
            "azure_logic_apps": self.diagram_classes["LogicApps"],
            "azure_service_bus": self.diagram_classes["ServiceBus"],
            "azure_event_grid": self.diagram_classes["EventGrid"],
            "azure_ad": self.diagram_classes["ActiveDirectory"],
            "azure_key_vault": self.diagram_classes["KeyVault"],
            "azure_application_insights": self.diagram_classes["ApplicationInsights"],
            # Default fallback - we'll use Custom for components without specific icons
        }

    def export_diagram(
        self,
        architecture: Architecture,
        config: DiagramConfig,
        output_path: Optional[str] = None,
    ) -> tuple[str, DiagramMetadata]:
        """
        Export an architecture as a visual diagram.

        Args:
            architecture: The architecture to export
            config: Diagram configuration settings
            output_path: Optional custom output path

        Returns:
            Tuple of (output_file_path, diagram_metadata)

        Raises:
            DiagramExportError: If diagram export fails
        """
        start_time = datetime.now()

        # Handle Visio export separately
        if config.format.value == "vsdx":
            return self.visio_exporter.export_visio_diagram(architecture, config, output_path)

        if not self.diagrams_available:
            raise DiagramExportError(
                "Diagrams library not available. Please install with: pip install diagrams"
            )

        try:
            # Prepare output path
            if output_path:
                final_output_path = output_path
            else:
                # Ensure output directory exists
                output_dir = Path(config.output_directory)
                output_dir.mkdir(parents=True, exist_ok=True)
                final_output_path = str(
                    output_dir / f"{config.filename}.{config.format.value}"
                )

            # Generate the diagram
            self._generate_diagram_file(architecture, config, final_output_path)

            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()

            # Get file size
            file_size = (
                Path(final_output_path).stat().st_size
                if Path(final_output_path).exists()
                else 0
            )

            # Create metadata
            metadata = DiagramMetadata(
                architecture_name=architecture.name,
                component_count=len(architecture.technology_stack.components),
                integration_count=len(architecture.technology_stack.integration_flows),
                layers_included=list(architecture.layer_organization.keys()),
                format=config.format,
                complexity_score=architecture.get_integration_complexity_score(),
                generation_time_seconds=generation_time,
                file_size_bytes=file_size,
            )

            logger.info(
                f"Exported diagram to {final_output_path} in {generation_time:.2f}s"
            )
            return final_output_path, metadata

        except Exception as e:
            raise DiagramExportError(f"Failed to export diagram: {e}")

    def _generate_diagram_file(
        self, architecture: Architecture, config: DiagramConfig, output_path: str
    ) -> None:
        """
        Generate the actual diagram file using the diagrams library.

        Args:
            architecture: The architecture to diagram
            config: Diagram configuration
            output_path: Path where to save the diagram
        """
        # Remove extension from output path as diagrams library adds it
        base_path = str(Path(output_path).with_suffix(""))

        # Configure diagram attributes
        diagram_attrs = {
            "fontsize": "12",
            "bgcolor": "white",
            "pad": "0.5",
            "nodesep": str(config.node_spacing),
            "ranksep": str(config.layer_spacing),
            "rankdir": "LR",  # Force left-to-right layout
            "splines": "ortho",  # Use orthogonal edge routing
        }

        with self.diagram_classes["Diagram"](
            name=architecture.name,
            filename=base_path,
            show=False,
            direction="LR",  # Left to right layout
            graph_attr=diagram_attrs,
        ):
            self._create_layered_diagram(architecture, config)

    def _create_layered_diagram(
        self, architecture: Architecture, config: DiagramConfig
    ) -> None:
        """
        Create a layered diagram following Microsoft architecture patterns.

        Args:
            architecture: The architecture to diagram
            config: Diagram configuration
        """
        layer_nodes = {}
        layer_order = architecture.get_layer_order()

        # Create all nodes first without clusters for better layout control
        for layer in layer_order:
            layer_components = architecture.get_layer_components(layer)
            if not layer_components:
                continue

            layer_nodes[layer] = []
            for component in layer_components:
                node = self._create_component_node(component, config)
                layer_nodes[layer].append((component.id, node))

        # Create invisible edges between layers to force horizontal layout
        self._create_layer_ordering_edges(layer_nodes, layer_order)

        # Create edges for integration flows
        self._create_integration_edges(architecture, layer_nodes, config)

    def _create_layer_ordering_edges(
        self, layer_nodes: dict, layer_order: list
    ) -> None:
        """
        Create invisible edges to force horizontal layer ordering.

        Args:
            layer_nodes: Dictionary of layer nodes
            layer_order: Ordered list of layers
        """
        for i in range(len(layer_order) - 1):
            current_layer = layer_order[i]
            next_layer = layer_order[i + 1]

            if current_layer in layer_nodes and next_layer in layer_nodes:
                # Create invisible edge from first node of current layer to first node of next layer
                current_nodes = layer_nodes[current_layer]
                next_nodes = layer_nodes[next_layer]

                if current_nodes and next_nodes:
                    # Use invisible edge to control layout
                    (
                        current_nodes[0][1]
                        >> self.diagram_classes["Edge"](style="invis")
                        >> next_nodes[0][1]
                    )

    def _create_component_node(self, component, config: DiagramConfig):
        """
        Create a diagram node for a technology component.

        Args:
            component: The technology component
            config: Diagram configuration

        Returns:
            Diagram node object
        """
        # Check if we have a custom Microsoft icon for this component
        icon_path = self.icon_manager.get_component_icon_path(component.id)
        
        if icon_path and icon_path.exists():
            # Use Custom node with Microsoft icon
            node_class = self.diagram_classes["Custom"]
            
            # Create the node with custom icon
            label = component.name
            if config.show_descriptions and component.description:
                # Truncate description for readability
                desc = (
                    component.description[:50] + "..."
                    if len(component.description) > 50
                    else component.description
                )
                label = f"{component.name}\\n{desc}"

            return node_class(label, icon_path=str(icon_path))
        
        # Fall back to built-in diagrams library icons
        # Try to find a specific mapping for this component
        node_class = self.component_mappings.get(component.id)

        if not node_class:
            # Try category-based mapping
            category_mappings = {
                TechnologyCategory.POWER_PLATFORM: self.diagram_classes[
                    "PowerBi"
                ],  # Generic Power Platform
                TechnologyCategory.DYNAMICS_365: self.diagram_classes[
                    "CosmosDb"
                ],  # Generic Dynamics
                TechnologyCategory.AZURE_SERVICES: self.diagram_classes[
                    "FunctionApps"
                ],  # Generic Azure
                TechnologyCategory.SECURITY_OPS: self.diagram_classes[
                    "ActiveDirectory"
                ],  # Generic Security
            }
            node_class = category_mappings.get(
                component.category, self.diagram_classes["PowerBi"]
            )

        # Create the node with appropriate label
        label = component.name
        if config.show_descriptions and component.description:
            # Truncate description for readability
            desc = (
                component.description[:50] + "..."
                if len(component.description) > 50
                else component.description
            )
            label = f"{component.name}\\n{desc}"

        return node_class(label)

    def _create_integration_edges(
        self, architecture: Architecture, layer_nodes: dict, config: DiagramConfig
    ) -> None:
        """
        Create edges representing integration flows between components.

        Args:
            architecture: The architecture model
            layer_nodes: Dictionary of layer nodes
            config: Diagram configuration
        """
        # Create a mapping from component ID to node
        id_to_node = {}
        for _layer, nodes in layer_nodes.items():
            for comp_id, node in nodes:
                id_to_node[comp_id] = node

        # Create edges for integration flows
        for flow in architecture.technology_stack.integration_flows:
            source_node = id_to_node.get(flow.source_component_id)
            target_node = id_to_node.get(flow.target_component_id)

            if source_node and target_node:
                # Create edge with optional label
                if architecture.show_integration_flows:
                    pattern_name = flow.integration_pattern.value.replace(
                        "_", " "
                    ).title()
                    edge = self.diagram_classes["Edge"](
                        label=pattern_name, style="solid"
                    )
                else:
                    edge = self.diagram_classes["Edge"](style="solid")

                source_node >> edge >> target_node

    def create_diagram_preview(
        self, architecture: Architecture, config: DiagramConfig
    ) -> dict[str, Any]:
        """
        Create a preview of what the diagram will contain without generating the file.

        Args:
            architecture: The architecture to preview
            config: Diagram configuration

        Returns:
            Dictionary with preview information
        """
        preview = {
            "architecture_name": architecture.name,
            "layers": {},
            "integration_flows": [],
            "estimated_complexity": architecture.get_integration_complexity_score(),
            "output_format": config.format.value,
            "estimated_file_size": "Unknown",
        }

        # Layer preview
        for layer in architecture.get_layer_order():
            layer_components = architecture.get_layer_components(layer)
            preview["layers"][layer.value] = [
                {"id": comp.id, "name": comp.name, "description": comp.description}
                for comp in layer_components
            ]

        # Integration flows preview
        for flow in architecture.technology_stack.integration_flows:
            preview["integration_flows"].append(
                {
                    "name": flow.name,
                    "source": flow.source_component_id,
                    "target": flow.target_component_id,
                    "pattern": flow.integration_pattern.value,
                }
            )

        return preview

    def validate_export_requirements(
        self, architecture: Architecture, config: DiagramConfig
    ) -> list[str]:
        """
        Validate that all requirements for diagram export are met.

        Args:
            architecture: The architecture to validate
            config: Diagram configuration to validate

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.diagrams_available:
            errors.append("Diagrams library is not available")

        # Validate architecture
        arch_errors = architecture.validate_architecture()
        errors.extend(arch_errors)

        # Validate minimum components
        if len(architecture.technology_stack.components) == 0:
            errors.append("No components to display in diagram")

        # Validate output directory
        output_dir = Path(config.output_directory)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory: {e}")

        # Check for potential file conflicts
        output_path = output_dir / f"{config.filename}.{config.format.value}"
        if output_path.exists():
            errors.append(f"Output file already exists: {output_path}")

        return errors

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported diagram output formats.

        Returns:
            List of supported format strings
        """
        formats = []
        
        if self.diagrams_available:
            formats.extend(["png", "svg", "pdf", "jpg"])
            
        if self.visio_exporter.vsdx_available:
            formats.append("vsdx")
            
        return formats

    def create_multiple_formats(
        self, architecture: Architecture, base_config: DiagramConfig, formats: list[str]
    ) -> dict[str, tuple[str, DiagramMetadata]]:
        """
        Export the same diagram in multiple formats.

        Args:
            architecture: The architecture to export
            base_config: Base configuration to use
            formats: List of formats to export

        Returns:
            Dictionary mapping format to (file_path, metadata) tuples
        """
        results = {}

        for format_str in formats:
            try:
                # Create config for this format
                format_config = DiagramConfig(
                    format=format_str,
                    filename=f"{base_config.filename}_{format_str}",
                    output_directory=base_config.output_directory,
                    width=base_config.width,
                    height=base_config.height,
                    dpi=base_config.dpi,
                    show_icons=base_config.show_icons,
                    show_labels=base_config.show_labels,
                    show_descriptions=base_config.show_descriptions,
                    color_by_category=base_config.color_by_category,
                )

                file_path, metadata = self.export_diagram(architecture, format_config)
                results[format_str] = (file_path, metadata)

            except Exception as e:
                logger.error(f"Failed to export format {format_str}: {e}")
                continue

        return results

    def download_microsoft_icons(self) -> bool:
        """
        Download official Microsoft icons for use in diagrams.

        Returns:
            True if download was successful, False otherwise
        """
        try:
            success = self.icon_manager.download_power_platform_icons()
            if success:
                logger.info("Microsoft Power Platform icons downloaded successfully")
            return success
        except Exception as e:
            logger.error(f"Failed to download Microsoft icons: {e}")
            return False

    def list_available_icons(self) -> dict[str, Any]:
        """
        List all available Microsoft icons.

        Returns:
            Dictionary of available icons by category
        """
        return self.icon_manager.list_available_icons()

    def create_visio_template(self, template_name: str = "Microsoft Architecture") -> str:
        """
        Create a Visio template with Microsoft branding.

        Args:
            template_name: Name for the template

        Returns:
            Path to the created template file
        """
        return self.visio_exporter.create_visio_template(template_name)
