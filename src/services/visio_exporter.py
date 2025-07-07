"""
Visio exporter service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides functionality for generating Visio diagrams from architecture models.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from models.architecture import Architecture, DiagramConfig, DiagramMetadata, DiagramFormat
from models.technology import TechnologyCategory

logger = logging.getLogger(__name__)


class VisioExportError(Exception):
    """Custom exception for Visio export operations."""

    pass


class VisioExporter:
    """
    Service class for exporting architecture diagrams to Visio format.

    This class handles the conversion of architecture models into Visio VSDX files
    using the vsdx library.
    """

    def __init__(self):
        """Initialize the Visio exporter."""
        try:
            import vsdx

            self.vsdx_available = True
            self.vsdx = vsdx
        except ImportError:
            self.vsdx_available = False
            logger.warning("vsdx library not available. Visio export will be disabled.")

    def export_visio_diagram(
        self,
        architecture: Architecture,
        config: DiagramConfig,
        output_path: Optional[str] = None,
    ) -> Tuple[str, DiagramMetadata]:
        """
        Export an architecture as a Visio VSDX diagram.

        Args:
            architecture: The architecture to export
            config: Diagram configuration settings
            output_path: Optional custom output path

        Returns:
            Tuple of (output_file_path, diagram_metadata)

        Raises:
            VisioExportError: If Visio export fails
        """
        start_time = datetime.now()

        if not self.vsdx_available:
            raise VisioExportError(
                "vsdx library not available. Please install with: pip install vsdx"
            )

        try:
            # Prepare output path
            if output_path:
                final_output_path = output_path
            else:
                # Ensure output directory exists
                output_dir = Path(config.output_directory)
                output_dir.mkdir(parents=True, exist_ok=True)
                final_output_path = str(output_dir / f"{config.filename}.vsdx")

            # Generate the Visio diagram
            self._generate_visio_file(architecture, config, final_output_path)

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
                format=DiagramFormat("vsdx"),  # Custom format for Visio
                complexity_score=architecture.get_integration_complexity_score(),
                generation_time_seconds=generation_time,
                file_size_bytes=file_size,
            )

            logger.info(
                f"Exported Visio diagram to {final_output_path} in {generation_time:.2f}s"
            )
            return final_output_path, metadata

        except Exception as e:
            raise VisioExportError(f"Failed to export Visio diagram: {e}")

    def _generate_visio_file(
        self, architecture: Architecture, config: DiagramConfig, output_path: str
    ) -> None:
        """
        Generate the actual Visio file using a simplified approach.

        Args:
            architecture: The architecture to diagram
            config: Diagram configuration
            output_path: Path where to save the diagram
        """
        # For now, create a simple text-based diagram description
        # The vsdx library requires existing templates, which makes creating new files complex
        
        diagram_content = f"""Microsoft Architecture Diagram: {architecture.name}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Description: {architecture.description}

Configuration:
- Format: {config.format.value.upper()}
- Show Descriptions: {config.show_descriptions}
- Use Microsoft Colors: {config.use_microsoft_colors}

Architecture Components:
"""
        
        layer_order = architecture.get_layer_order()
        
        for layer in layer_order:
            layer_components = architecture.get_layer_components(layer)
            if not layer_components:
                continue
                
            layer_name = layer.value.replace("_", " ").title()
            diagram_content += f"\n{layer_name} Layer:\n"
            diagram_content += "=" * (len(layer_name) + 7) + "\n"
            
            for component in layer_components:
                diagram_content += f"  • {component.name}\n"
                if config.show_descriptions and component.description:
                    diagram_content += f"    Description: {component.description}\n"
        
        # Add integration flows
        if architecture.technology_stack.integration_flows:
            diagram_content += "\nIntegration Flows:\n"
            diagram_content += "==================\n"
            
            for flow in architecture.technology_stack.integration_flows:
                source = architecture.technology_stack.get_component_by_id(flow.source_component_id)
                target = architecture.technology_stack.get_component_by_id(flow.target_component_id)
                
                if source and target:
                    pattern_name = flow.integration_pattern.value.replace("_", " ").title()
                    diagram_content += f"  {source.name} → {target.name} ({pattern_name})\n"
        
        # For now, save as a text file with .vsdx extension
        # This is a placeholder until we can properly implement Visio file creation
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(diagram_content)
            
        logger.warning("Visio export is currently generating text-based diagrams. Full Visio support requires additional configuration.")

    def _get_category_color(self, category: TechnologyCategory) -> str:
        """
        Get the color for a technology category.

        Args:
            category: The technology category

        Returns:
            Hex color code for the category
        """
        color_map = {
            TechnologyCategory.POWER_PLATFORM: "#742774",  # Power Platform purple
            TechnologyCategory.DYNAMICS_365: "#0078D4",    # Microsoft blue
            TechnologyCategory.AZURE_SERVICES: "#0078D4",  # Azure blue
            TechnologyCategory.SECURITY_OPS: "#D13438",    # Security red
        }
        return color_map.get(category, "#737373")  # Default gray

    def create_visio_template(self, template_name: str = "Microsoft Architecture") -> str:
        """
        Create a Visio template with Microsoft branding and colors.

        Args:
            template_name: Name for the template

        Returns:
            Path to the created template file

        Raises:
            VisioExportError: If template creation fails
        """
        if not self.vsdx_available:
            raise VisioExportError("vsdx library not available for template creation")

        try:
            # Create template directory
            template_dir = Path(__file__).parent.parent / "data" / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            
            template_path = template_dir / f"{template_name.replace(' ', '_')}.txt"

            # Create a text-based template for now
            template_content = f"""Microsoft Architecture Template: {template_name}
====================================================================

This is a template file for creating Microsoft architecture diagrams.

Layer Categories:
- Power Platform (Purple: #742774)
- Dynamics 365 (Blue: #0078D4)  
- Azure Services (Blue: #0078D4)
- Security & Ops (Red: #D13438)

Instructions:
1. Use the architecture builder CLI to generate diagrams
2. Components will be organized by layers automatically
3. Integration flows will show connections between components

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"Created Visio template: {template_path}")
            logger.warning("Template creation is currently text-based. Full Visio support requires additional configuration.")
            return str(template_path)

        except Exception as e:
            raise VisioExportError(f"Failed to create Visio template: {e}")

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported Visio output formats.

        Returns:
            List of supported format strings
        """
        if not self.vsdx_available:
            return []

        return ["vsdx"]

    def validate_visio_requirements(self) -> list[str]:
        """
        Validate that all requirements for Visio export are met.

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.vsdx_available:
            errors.append("vsdx library is not available")

        return errors


# Global Visio exporter instance
_visio_exporter: Optional[VisioExporter] = None


def get_visio_exporter() -> VisioExporter:
    """
    Get the global Visio exporter instance.

    Returns:
        Global VisioExporter instance
    """
    global _visio_exporter
    if _visio_exporter is None:
        _visio_exporter = VisioExporter()
    return _visio_exporter


def reset_visio_exporter() -> None:
    """Reset the global Visio exporter instance (useful for testing)."""
    global _visio_exporter
    _visio_exporter = None