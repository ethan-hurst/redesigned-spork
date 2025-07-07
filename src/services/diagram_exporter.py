"""
Diagram exporter service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides functionality for generating visual diagrams from architecture models.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Diagram generation imports
try:
    from diagrams import Cluster, Diagram, Edge
    from diagrams.azure.analytics import (
        PowerBi,  # Using PowerBi instead of PowerBiEmbedded
    )
    from diagrams.azure.compute import FunctionApps
    from diagrams.azure.database import CosmosDb
    from diagrams.azure.devops import ApplicationInsights
    from diagrams.azure.identity import ActiveDirectory
    from diagrams.azure.integration import EventGrid, LogicApps, ServiceBus
    from diagrams.azure.security import KeyVault
    from diagrams.custom import Custom
    DIAGRAMS_AVAILABLE = True
except ImportError:
    DIAGRAMS_AVAILABLE = False
    # Create dummy classes for when diagrams is not available
    class Diagram:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class Edge:
        def __init__(self, *args, **kwargs): pass

    class Cluster:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    PowerBi = FunctionApps = CosmosDb = ActiveDirectory = LogicApps = ServiceBus = EventGrid = KeyVault = ApplicationInsights = Custom = lambda x: None
    # Don't log here since logger is not yet defined

from ..models.architecture import Architecture, DiagramConfig, DiagramMetadata
from ..models.technology import TechnologyCategory

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
        self.diagrams_available = DIAGRAMS_AVAILABLE

        # Component to diagram node mapping
        self.component_mappings = self._initialize_component_mappings()

    def _initialize_component_mappings(self) -> Dict[str, Any]:
        """
        Initialize mappings from component IDs to diagram node types.
        
        Returns:
            Dictionary mapping component IDs to diagram node classes
        """
        return {
            # Power Platform
            'power_bi': PowerBi,
            'dataverse': CosmosDb,  # Using CosmosDB as closest equivalent

            # Azure Services
            'azure_functions': FunctionApps,
            'azure_logic_apps': LogicApps,
            'azure_service_bus': ServiceBus,
            'azure_event_grid': EventGrid,
            'azure_ad': ActiveDirectory,
            'azure_key_vault': KeyVault,
            'azure_application_insights': ApplicationInsights,

            # Default fallback - we'll use Custom for components without specific icons
        }

    def export_diagram(
        self,
        architecture: Architecture,
        config: DiagramConfig,
        output_path: Optional[str] = None
    ) -> Tuple[str, DiagramMetadata]:
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

        if not self.diagrams_available:
            raise DiagramExportError("Diagrams library not available. Please install with: pip install diagrams")

        try:
            # Prepare output path
            if output_path:
                final_output_path = output_path
            else:
                # Ensure output directory exists
                output_dir = Path(config.output_directory)
                output_dir.mkdir(parents=True, exist_ok=True)
                final_output_path = str(output_dir / f"{config.filename}.{config.format.value}")

            # Generate the diagram
            self._generate_diagram_file(architecture, config, final_output_path)

            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()

            # Get file size
            file_size = Path(final_output_path).stat().st_size if Path(final_output_path).exists() else 0

            # Create metadata
            metadata = DiagramMetadata(
                architecture_name=architecture.name,
                component_count=len(architecture.technology_stack.components),
                integration_count=len(architecture.technology_stack.integration_flows),
                layers_included=list(architecture.layer_organization.keys()),
                format=config.format,
                complexity_score=architecture.get_integration_complexity_score(),
                generation_time_seconds=generation_time,
                file_size_bytes=file_size
            )

            logger.info(f"Exported diagram to {final_output_path} in {generation_time:.2f}s")
            return final_output_path, metadata

        except Exception as e:
            raise DiagramExportError(f"Failed to export diagram: {e}")

    def _generate_diagram_file(
        self,
        architecture: Architecture,
        config: DiagramConfig,
        output_path: str
    ) -> None:
        """
        Generate the actual diagram file using the diagrams library.
        
        Args:
            architecture: The architecture to diagram
            config: Diagram configuration
            output_path: Path where to save the diagram
        """
        # Remove extension from output path as diagrams library adds it
        base_path = str(Path(output_path).with_suffix(''))

        # Configure diagram attributes
        diagram_attrs = {
            "fontsize": "12",
            "bgcolor": "white",
            "pad": "0.5",
            "nodesep": str(config.node_spacing),
            "ranksep": str(config.layer_spacing)
        }

        with Diagram(
            name=architecture.name,
            filename=base_path,
            show=False,
            direction="LR",  # Left to right layout
            graph_attr=diagram_attrs
        ):
            self._create_layered_diagram(architecture, config)

    def _create_layered_diagram(self, architecture: Architecture, config: DiagramConfig) -> None:
        """
        Create a layered diagram following Microsoft architecture patterns.
        
        Args:
            architecture: The architecture to diagram
            config: Diagram configuration
        """
        layer_nodes = {}

        # Create clusters for each layer
        layer_order = architecture.get_layer_order()

        for layer in layer_order:
            layer_components = architecture.get_layer_components(layer)
            if not layer_components:
                continue

            layer_name = layer.value.replace('_', ' ').title()

            with Cluster(layer_name):
                layer_nodes[layer] = []

                for component in layer_components:
                    node = self._create_component_node(component, config)
                    layer_nodes[layer].append((component.id, node))

        # Create edges for integration flows
        self._create_integration_edges(architecture, layer_nodes, config)

    def _create_component_node(self, component, config: DiagramConfig):
        """
        Create a diagram node for a technology component.
        
        Args:
            component: The technology component
            config: Diagram configuration
            
        Returns:
            Diagram node object
        """
        # Try to find a specific mapping for this component
        node_class = self.component_mappings.get(component.id)

        if not node_class:
            # Try category-based mapping
            category_mappings = {
                TechnologyCategory.POWER_PLATFORM: PowerBi,  # Generic Power Platform
                TechnologyCategory.DYNAMICS_365: CosmosDb,  # Generic Dynamics
                TechnologyCategory.AZURE_SERVICES: FunctionApps,  # Generic Azure
                TechnologyCategory.SECURITY_OPS: ActiveDirectory  # Generic Security
            }
            node_class = category_mappings.get(component.category, PowerBi)

        # Create the node with appropriate label
        label = component.name
        if config.show_descriptions and component.description:
            # Truncate description for readability
            desc = component.description[:50] + "..." if len(component.description) > 50 else component.description
            label = f"{component.name}\\n{desc}"

        return node_class(label)

    def _create_integration_edges(
        self,
        architecture: Architecture,
        layer_nodes: Dict,
        config: DiagramConfig
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
        for layer, nodes in layer_nodes.items():
            for comp_id, node in nodes:
                id_to_node[comp_id] = node

        # Create edges for integration flows
        for flow in architecture.technology_stack.integration_flows:
            source_node = id_to_node.get(flow.source_component_id)
            target_node = id_to_node.get(flow.target_component_id)

            if source_node and target_node:
                # Create edge with optional label
                if config.show_integration_flows:
                    pattern_name = flow.integration_pattern.value.replace('_', ' ').title()
                    edge = Edge(label=pattern_name, style="solid")
                else:
                    edge = Edge(style="solid")

                source_node >> edge >> target_node

    def create_diagram_preview(
        self,
        architecture: Architecture,
        config: DiagramConfig
    ) -> Dict[str, Any]:
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
            "estimated_file_size": "Unknown"
        }

        # Layer preview
        for layer in architecture.get_layer_order():
            layer_components = architecture.get_layer_components(layer)
            preview["layers"][layer.value] = [
                {
                    "id": comp.id,
                    "name": comp.name,
                    "description": comp.description
                }
                for comp in layer_components
            ]

        # Integration flows preview
        for flow in architecture.technology_stack.integration_flows:
            preview["integration_flows"].append({
                "name": flow.name,
                "source": flow.source_component_id,
                "target": flow.target_component_id,
                "pattern": flow.integration_pattern.value
            })

        return preview

    def validate_export_requirements(
        self,
        architecture: Architecture,
        config: DiagramConfig
    ) -> List[str]:
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

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported diagram output formats.
        
        Returns:
            List of supported format strings
        """
        if not self.diagrams_available:
            return []

        return ["png", "svg", "pdf", "jpg"]

    def create_multiple_formats(
        self,
        architecture: Architecture,
        base_config: DiagramConfig,
        formats: List[str]
    ) -> Dict[str, Tuple[str, DiagramMetadata]]:
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
                    color_by_category=base_config.color_by_category
                )

                file_path, metadata = self.export_diagram(architecture, format_config)
                results[format_str] = (file_path, metadata)

            except Exception as e:
                logger.error(f"Failed to export format {format_str}: {e}")
                continue

        return results
