"""
Architecture models for Microsoft Dynamics & Power Platform Architecture Builder.

This module defines the models for architectural diagrams and their generation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .technology import LayerType, TechnologyComponent, TechnologyStack


class DiagramFormat(str, Enum):
    """Enumeration of supported diagram output formats."""

    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    JPG = "jpg"


class DiagramLayout(str, Enum):
    """Enumeration of diagram layout styles."""

    LAYERED = "layered"
    FLOWCHART = "flowchart"
    NETWORK = "network"
    HIERARCHICAL = "hierarchical"


class Architecture(BaseModel):
    """
    Model representing a complete Microsoft technology architecture.
    
    This model combines a technology stack with layout and presentation information
    to generate architectural diagrams.
    """

    name: str = Field(..., description="Name of the architecture")
    description: str = Field(..., description="Description of the architecture purpose")
    technology_stack: TechnologyStack = Field(..., description="The selected technology components")
    layout: DiagramLayout = Field(default=DiagramLayout.LAYERED, description="Diagram layout style")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    # Diagram organization
    layer_organization: Dict[LayerType, List[str]] = Field(
        default_factory=dict,
        description="Organization of components by architectural layer"
    )

    # Visual customization
    show_integration_flows: bool = Field(default=True, description="Whether to show integration flows")
    show_layer_labels: bool = Field(default=True, description="Whether to show layer labels")
    show_component_descriptions: bool = Field(default=False, description="Whether to show component descriptions")

    def __init__(self, **data):
        """Initialize architecture and organize components by layer."""
        super().__init__(**data)
        self._organize_components_by_layer()

    def _organize_components_by_layer(self) -> None:
        """Organize components into architectural layers."""
        self.layer_organization = {}

        for component in self.technology_stack.components:
            if component.layer not in self.layer_organization:
                self.layer_organization[component.layer] = []
            self.layer_organization[component.layer].append(component.id)

    def add_component(self, component: TechnologyComponent) -> bool:
        """
        Add a component to the architecture.
        
        Args:
            component: The component to add
            
        Returns:
            True if the component was added successfully
        """
        success = self.technology_stack.add_component(component)
        if success:
            self._organize_components_by_layer()
            self.updated_at = datetime.now()
        return success

    def remove_component(self, component_id: str) -> bool:
        """
        Remove a component from the architecture.
        
        Args:
            component_id: ID of the component to remove
            
        Returns:
            True if the component was removed
        """
        success = self.technology_stack.remove_component(component_id)
        if success:
            self._organize_components_by_layer()
            self.updated_at = datetime.now()
        return success

    def validate_architecture(self) -> List[str]:
        """
        Validate the complete architecture for consistency and completeness.
        
        Returns:
            List of validation error messages
        """
        errors = []

        # Validate technology stack dependencies
        dependency_errors = self.technology_stack.validate_dependencies()
        errors.extend(dependency_errors)

        # Validate integration flows
        for flow in self.technology_stack.integration_flows:
            source = self.technology_stack.get_component_by_id(flow.source_component_id)
            target = self.technology_stack.get_component_by_id(flow.target_component_id)

            if not source:
                errors.append(f"Integration flow {flow.id} references missing source component {flow.source_component_id}")
            if not target:
                errors.append(f"Integration flow {flow.id} references missing target component {flow.target_component_id}")

            # Validate integration pattern compatibility
            if source and not source.supports_integration(flow.integration_pattern):
                errors.append(f"Component {source.id} does not support integration pattern {flow.integration_pattern}")
            if target and not target.supports_integration(flow.integration_pattern):
                errors.append(f"Component {target.id} does not support integration pattern {flow.integration_pattern}")

        # Check for minimum components in critical layers
        if LayerType.DATA not in self.layer_organization or not self.layer_organization[LayerType.DATA]:
            errors.append("Architecture should include at least one data layer component")

        return errors

    def get_layer_components(self, layer: LayerType) -> List[TechnologyComponent]:
        """
        Get all components in a specific layer.
        
        Args:
            layer: The layer to retrieve components for
            
        Returns:
            List of components in the specified layer
        """
        if layer not in self.layer_organization:
            return []

        components = []
        for component_id in self.layer_organization[layer]:
            component = self.technology_stack.get_component_by_id(component_id)
            if component:
                components.append(component)

        return components

    def get_layer_order(self) -> List[LayerType]:
        """
        Get the ordered list of layers for diagram generation.
        
        Returns:
            List of layers in the order they should appear in diagrams
        """
        # Define the canonical layer order for Microsoft architectures
        canonical_order = [
            LayerType.PRESENTATION,
            LayerType.APPLICATION,
            LayerType.INTEGRATION,
            LayerType.DATA,
            LayerType.SECURITY
        ]

        # Return only layers that have components
        return [layer for layer in canonical_order if layer in self.layer_organization and self.layer_organization[layer]]

    def generate_layer_matrix(self) -> Dict[LayerType, List[TechnologyComponent]]:
        """
        Generate a matrix of layers and their components for diagram layout.
        
        Returns:
            Dictionary mapping layers to their components
        """
        matrix = {}
        for layer in self.get_layer_order():
            matrix[layer] = self.get_layer_components(layer)
        return matrix

    def suggest_missing_components(self) -> List[str]:
        """
        Suggest missing components based on selected technologies.
        
        Returns:
            List of component IDs that might be missing
        """
        suggestions = []

        # Check for common patterns
        has_power_apps = any(
            'power_apps' in c.id for c in self.technology_stack.components
        )
        has_dataverse = any(
            'dataverse' in c.id for c in self.technology_stack.components
        )

        if has_power_apps and not has_dataverse:
            suggestions.append("dataverse")

        # Check for security components
        has_security = any(
            c.layer == LayerType.SECURITY for c in self.technology_stack.components
        )
        if not has_security:
            suggestions.append("azure_ad")

        return suggestions

    def get_integration_complexity_score(self) -> int:
        """
        Calculate a complexity score based on the number of components and integrations.
        
        Returns:
            Complexity score from 1 (simple) to 10 (very complex)
        """
        component_count = len(self.technology_stack.components)
        flow_count = len(self.technology_stack.integration_flows)
        layer_count = len(self.layer_organization)

        # Basic scoring algorithm
        score = min(10, max(1,
            (component_count // 3) +
            (flow_count // 2) +
            layer_count
        ))

        return score


class DiagramConfig(BaseModel):
    """
    Configuration model for diagram generation.
    
    This model defines all the visual and formatting options for generating
    architectural diagrams.
    """

    # Output settings
    format: DiagramFormat = Field(default=DiagramFormat.PNG, description="Output format")
    filename: str = Field(..., description="Output filename (without extension)")
    output_directory: str = Field(default="output", description="Output directory path")

    # Visual settings
    width: int = Field(default=1200, description="Diagram width in pixels", ge=400, le=4000)
    height: int = Field(default=800, description="Diagram height in pixels", ge=300, le=3000)
    dpi: int = Field(default=300, description="DPI for raster formats", ge=72, le=600)

    # Layout settings
    node_spacing: float = Field(default=1.0, description="Spacing between nodes", ge=0.5, le=3.0)
    layer_spacing: float = Field(default=2.0, description="Spacing between layers", ge=1.0, le=5.0)

    # Style settings
    show_icons: bool = Field(default=True, description="Whether to show component icons")
    show_labels: bool = Field(default=True, description="Whether to show component labels")
    show_descriptions: bool = Field(default=False, description="Whether to show component descriptions")
    color_by_category: bool = Field(default=True, description="Whether to color components by category")

    # Microsoft branding
    use_microsoft_colors: bool = Field(default=True, description="Whether to use Microsoft brand colors")
    show_microsoft_logo: bool = Field(default=False, description="Whether to include Microsoft logo")

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename doesn't contain invalid characters."""
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in v for char in invalid_chars):
            raise ValueError(f'Filename cannot contain: {", ".join(invalid_chars)}')
        return v

    def get_output_path(self) -> str:
        """
        Get the complete output path including extension.
        
        Returns:
            Complete file path for the output diagram
        """
        return f"{self.output_directory}/{self.filename}.{self.format.value}"

    def get_microsoft_color_palette(self) -> Dict[str, str]:
        """
        Get Microsoft brand color palette.
        
        Returns:
            Dictionary mapping color names to hex values
        """
        return {
            "blue": "#0078d4",
            "light_blue": "#40e0d0",
            "green": "#107c10",
            "orange": "#ff8c00",
            "red": "#d13438",
            "purple": "#5c2d91",
            "gray": "#737373",
            "dark_gray": "#323130"
        }


class DiagramMetadata(BaseModel):
    """
    Metadata model for generated diagrams.
    
    This model stores information about how and when a diagram was generated.
    """

    architecture_name: str = Field(..., description="Name of the architecture")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    component_count: int = Field(..., description="Number of components in the diagram")
    integration_count: int = Field(..., description="Number of integration flows")
    layers_included: List[LayerType] = Field(..., description="Layers included in the diagram")
    format: DiagramFormat = Field(..., description="Output format used")
    complexity_score: int = Field(..., description="Architecture complexity score")

    # Generation details
    generation_time_seconds: Optional[float] = Field(None, description="Time taken to generate diagram")
    file_size_bytes: Optional[int] = Field(None, description="Size of generated file")

    def summary(self) -> str:
        """
        Generate a summary description of the diagram.
        
        Returns:
            Human-readable summary of the diagram
        """
        layer_names = [layer.value.replace('_', ' ').title() for layer in self.layers_included]
        return (
            f"Architecture '{self.architecture_name}' with {self.component_count} components "
            f"across {len(self.layers_included)} layers ({', '.join(layer_names)}). "
            f"Complexity score: {self.complexity_score}/10."
        )
