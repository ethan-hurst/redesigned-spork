"""
Diagram generation models for Microsoft Dynamics & Power Platform Architecture Builder.

This module defines models specifically for diagram generation and visualization.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .architecture import DiagramConfig
from .technology import (
    IntegrationFlow,
    LayerType,
    TechnologyCategory,
    TechnologyComponent,
)


class NodeStyle(BaseModel):
    """Style configuration for diagram nodes."""

    shape: str = Field(default="box", description="Node shape")
    color: str = Field(default="#ffffff", description="Node background color")
    border_color: str = Field(default="#000000", description="Node border color")
    text_color: str = Field(default="#000000", description="Text color")
    font_size: int = Field(default=12, description="Font size")
    width: Optional[float] = Field(None, description="Node width")
    height: Optional[float] = Field(None, description="Node height")


class EdgeStyle(BaseModel):
    """Style configuration for diagram edges."""

    color: str = Field(default="#000000", description="Edge color")
    style: str = Field(default="solid", description="Edge style (solid, dashed, dotted)")
    width: float = Field(default=1.0, description="Edge width")
    arrow_style: str = Field(default="normal", description="Arrow style")
    label_font_size: int = Field(default=10, description="Label font size")


class DiagramNode(BaseModel):
    """
    Model representing a node in the architectural diagram.
    
    This maps a technology component to its visual representation.
    """

    id: str = Field(..., description="Unique node identifier")
    component: TechnologyComponent = Field(..., description="Associated technology component")
    label: str = Field(..., description="Display label for the node")
    layer: LayerType = Field(..., description="Architectural layer")

    # Position and layout
    x_position: Optional[float] = Field(None, description="X coordinate in diagram")
    y_position: Optional[float] = Field(None, description="Y coordinate in diagram")
    layer_index: int = Field(..., description="Index within the layer")

    # Visual properties
    style: NodeStyle = Field(default_factory=NodeStyle, description="Node visual style")
    icon_path: Optional[str] = Field(None, description="Path to node icon")
    show_description: bool = Field(default=False, description="Whether to show component description")

    @property
    def display_text(self) -> str:
        """Get the text to display on the node."""
        if self.show_description and self.component.description:
            return f"{self.label}\n{self.component.description}"
        return self.label

    def get_category_color(self) -> str:
        """
        Get color based on component category.
        
        Returns:
            Hex color code for the component category
        """
        color_map = {
            TechnologyCategory.POWER_PLATFORM: "#742774",  # Power Platform purple
            TechnologyCategory.DYNAMICS_365: "#0078d4",    # Dynamics blue
            TechnologyCategory.AZURE_SERVICES: "#0072c6",  # Azure blue
            TechnologyCategory.SECURITY_OPS: "#107c10"     # Security green
        }
        return color_map.get(self.component.category, "#737373")  # Default gray


class DiagramEdge(BaseModel):
    """
    Model representing an edge (connection) in the architectural diagram.
    
    This maps an integration flow to its visual representation.
    """

    id: str = Field(..., description="Unique edge identifier")
    flow: IntegrationFlow = Field(..., description="Associated integration flow")
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Display label for the edge")

    # Visual properties
    style: EdgeStyle = Field(default_factory=EdgeStyle, description="Edge visual style")
    show_pattern_label: bool = Field(default=True, description="Whether to show integration pattern")

    @property
    def display_label(self) -> str:
        """Get the label to display on the edge."""
        if self.show_pattern_label:
            pattern_name = self.flow.integration_pattern.value.replace('_', ' ').title()
            return f"{pattern_name}"
        return self.label


class LayerGroup(BaseModel):
    """
    Model representing a layer group in the diagram.
    
    This organizes nodes by architectural layer for layout purposes.
    """

    layer: LayerType = Field(..., description="Layer type")
    label: str = Field(..., description="Display label for the layer")
    nodes: List[DiagramNode] = Field(default_factory=list, description="Nodes in this layer")

    # Layout properties
    x_position: float = Field(..., description="X position of the layer")
    y_position: float = Field(default=0.0, description="Y position of the layer")
    width: float = Field(..., description="Width of the layer")
    height: float = Field(default=100.0, description="Height of the layer")

    # Visual properties
    background_color: str = Field(default="#f8f9fa", description="Layer background color")
    border_color: str = Field(default="#dee2e6", description="Layer border color")
    show_background: bool = Field(default=True, description="Whether to show layer background")

    def add_node(self, node: DiagramNode) -> None:
        """
        Add a node to this layer.
        
        Args:
            node: The node to add
        """
        node.layer_index = len(self.nodes)
        self.nodes.append(node)

    def arrange_nodes_vertically(self, spacing: float = 1.0) -> None:
        """
        Arrange nodes vertically within the layer.
        
        Args:
            spacing: Vertical spacing between nodes
        """
        for i, node in enumerate(self.nodes):
            node.x_position = self.x_position + (self.width / 2)
            node.y_position = self.y_position + (i * spacing) + spacing


class DiagramLayout(BaseModel):
    """
    Model representing the complete layout of an architectural diagram.
    
    This coordinates the positioning and organization of all diagram elements.
    """

    name: str = Field(..., description="Layout name")
    layers: List[LayerGroup] = Field(default_factory=list, description="Layer groups")
    nodes: Dict[str, DiagramNode] = Field(default_factory=dict, description="All nodes by ID")
    edges: List[DiagramEdge] = Field(default_factory=list, description="All edges")

    # Layout dimensions
    total_width: float = Field(default=1200.0, description="Total diagram width")
    total_height: float = Field(default=800.0, description="Total diagram height")
    margin: float = Field(default=50.0, description="Diagram margin")

    def add_layer(self, layer: LayerGroup) -> None:
        """
        Add a layer to the layout.
        
        Args:
            layer: The layer to add
        """
        self.layers.append(layer)

        # Add all nodes from the layer to the nodes dictionary
        for node in layer.nodes:
            self.nodes[node.id] = node

    def add_edge(self, edge: DiagramEdge) -> None:
        """
        Add an edge to the layout.
        
        Args:
            edge: The edge to add
        """
        self.edges.append(edge)

    def arrange_layers_horizontally(self, spacing: float = 2.0) -> None:
        """
        Arrange layers horizontally across the diagram.
        
        Args:
            spacing: Horizontal spacing between layers
        """
        if not self.layers:
            return

        layer_width = (self.total_width - (2 * self.margin) - ((len(self.layers) - 1) * spacing)) / len(self.layers)

        for i, layer in enumerate(self.layers):
            layer.x_position = self.margin + (i * (layer_width + spacing))
            layer.width = layer_width
            layer.height = self.total_height - (2 * self.margin)
            layer.y_position = self.margin

            # Arrange nodes within the layer
            layer.arrange_nodes_vertically(spacing)

    def get_node_by_id(self, node_id: str) -> Optional[DiagramNode]:
        """
        Get a node by its ID.
        
        Args:
            node_id: The node ID to find
            
        Returns:
            The node if found, None otherwise
        """
        return self.nodes.get(node_id)

    def validate_layout(self) -> List[str]:
        """
        Validate the layout for consistency.
        
        Returns:
            List of validation errors
        """
        errors = []

        # Check that all edge endpoints exist
        for edge in self.edges:
            if edge.source_node_id not in self.nodes:
                errors.append(f"Edge {edge.id} references missing source node {edge.source_node_id}")
            if edge.target_node_id not in self.nodes:
                errors.append(f"Edge {edge.id} references missing target node {edge.target_node_id}")

        # Check for node position overlaps within layers
        for layer in self.layers:
            positions = [(node.x_position, node.y_position) for node in layer.nodes if node.x_position is not None]
            if len(positions) != len(set(positions)):
                errors.append(f"Layer {layer.label} has overlapping node positions")

        return errors


class DiagramGenerator(BaseModel):
    """
    Model for diagram generation configuration and state.
    
    This coordinates the conversion from architecture models to visual diagrams.
    """

    config: DiagramConfig = Field(..., description="Diagram configuration")
    layout: Optional[DiagramLayout] = Field(None, description="Current diagram layout")

    # Generation state
    is_generated: bool = Field(default=False, description="Whether diagram has been generated")
    generation_errors: List[str] = Field(default_factory=list, description="Generation errors")

    def create_layout_from_architecture(self, architecture: 'Architecture') -> DiagramLayout:
        """
        Create a diagram layout from an architecture model.
        
        Args:
            architecture: The architecture to create layout for
            
        Returns:
            Generated diagram layout
        """
        layout = DiagramLayout(name=f"{architecture.name} Layout")

        # Create layer groups
        for layer_type in architecture.get_layer_order():
            layer_components = architecture.get_layer_components(layer_type)

            layer_group = LayerGroup(
                layer=layer_type,
                label=layer_type.value.replace('_', ' ').title(),
                x_position=0.0,  # Will be set during arrangement
                width=200.0      # Will be adjusted during arrangement
            )

            # Create nodes for each component in the layer
            for component in layer_components:
                node = DiagramNode(
                    id=f"node_{component.id}",
                    component=component,
                    label=component.name,
                    layer=layer_type,
                    layer_index=len(layer_group.nodes),
                    icon_path=component.icon_path
                )

                # Apply category-based styling
                if self.config.color_by_category:
                    node.style.color = node.get_category_color()

                layer_group.add_node(node)

            layout.add_layer(layer_group)

        # Create edges for integration flows
        for flow in architecture.technology_stack.integration_flows:
            source_node_id = f"node_{flow.source_component_id}"
            target_node_id = f"node_{flow.target_component_id}"

            edge = DiagramEdge(
                id=f"edge_{flow.id}",
                flow=flow,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                label=flow.name
            )

            layout.add_edge(edge)

        # Arrange the layout
        layout.total_width = self.config.width
        layout.total_height = self.config.height
        layout.arrange_layers_horizontally(self.config.layer_spacing)

        self.layout = layout
        return layout

    def validate_generation_requirements(self) -> List[str]:
        """
        Validate that all requirements for diagram generation are met.
        
        Returns:
            List of validation errors
        """
        errors = []

        if not self.layout:
            errors.append("No layout has been created")
            return errors

        # Validate layout
        layout_errors = self.layout.validate_layout()
        errors.extend(layout_errors)

        # Check for minimum components
        if len(self.layout.nodes) == 0:
            errors.append("No components to display in diagram")

        return errors
