"""
Technology component models for Microsoft Dynamics & Power Platform Architecture Builder.

This module defines the core data models for technology components and their relationships.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TechnologyCategory(str, Enum):
    """Enumeration of technology categories."""

    POWER_PLATFORM = "power_platform"
    DYNAMICS_365 = "dynamics_365"
    AZURE_SERVICES = "azure_services"
    SECURITY_OPS = "security_ops"


class LayerType(str, Enum):
    """Enumeration of architectural layers."""

    PRESENTATION = "presentation"
    APPLICATION = "application"
    INTEGRATION = "integration"
    DATA = "data"
    SECURITY = "security"


class IntegrationPattern(str, Enum):
    """Enumeration of integration patterns."""

    DATAVERSE_CONNECTOR = "dataverse_connector"
    CUSTOM_CONNECTOR = "custom_connector"
    REST_API = "rest_api"
    ODATA = "odata"
    WEB_API = "web_api"
    LOGIC_APPS = "logic_apps"
    POWER_AUTOMATE = "power_automate"
    AZURE_FUNCTIONS = "azure_functions"
    SERVICE_BUS = "service_bus"
    EVENT_GRID = "event_grid"


class TechnologyComponent(BaseModel):
    """
    Model representing a Microsoft technology component.

    This model defines all the properties and relationships of a technology component
    that can be used in architectural diagrams.
    """

    id: str = Field(..., description="Unique identifier for the component")
    name: str = Field(..., description="Display name of the component")
    category: TechnologyCategory = Field(..., description="Technology category")
    subcategory: str = Field(..., description="Subcategory within the main category")
    description: str = Field(..., description="Brief description of the component")
    layer: LayerType = Field(
        ..., description="Architectural layer this component belongs to"
    )
    icon_path: Optional[str] = Field(None, description="Path to the component icon")
    dependencies: list[str] = Field(
        default_factory=list, description="List of component IDs this depends on"
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="List of component IDs that conflict with this",
    )
    integration_patterns: list[IntegrationPattern] = Field(
        default_factory=list, description="List of supported integration patterns"
    )
    is_core: bool = Field(
        default=False, description="Whether this is a core/foundational component"
    )
    pricing_tier: Optional[str] = Field(
        None, description="Pricing tier or licensing requirement"
    )

    @field_validator("id")
    @classmethod
    def id_must_be_lowercase_with_underscores(cls, v):
        """Validate that ID follows naming convention."""
        if not v.islower() or " " in v:
            raise ValueError("ID must be lowercase with underscores, no spaces")
        return v

    @field_validator("dependencies", "conflicts")
    @classmethod
    def validate_component_lists(cls, v):
        """Validate that component lists contain valid IDs."""
        for item in v:
            if not isinstance(item, str) or not item:
                raise ValueError("Component lists must contain non-empty strings")
        return v

    def has_dependency(self, component_id: str) -> bool:
        """
        Check if this component depends on another component.

        Args:
            component_id: The ID of the component to check

        Returns:
            True if this component depends on the specified component
        """
        return component_id in self.dependencies

    def conflicts_with(self, component_id: str) -> bool:
        """
        Check if this component conflicts with another component.

        Args:
            component_id: The ID of the component to check

        Returns:
            True if this component conflicts with the specified component
        """
        return component_id in self.conflicts

    def supports_integration(self, pattern: IntegrationPattern) -> bool:
        """
        Check if this component supports a specific integration pattern.

        Args:
            pattern: The integration pattern to check

        Returns:
            True if this component supports the specified pattern
        """
        return pattern in self.integration_patterns


class IntegrationFlow(BaseModel):
    """
    Model representing a data/process flow between components.

    This model defines how two components are connected and what type of
    integration pattern is used between them.
    """

    id: str = Field(..., description="Unique identifier for the flow")
    name: str = Field(..., description="Display name of the flow")
    source_component_id: str = Field(..., description="ID of the source component")
    target_component_id: str = Field(..., description="ID of the target component")
    integration_pattern: IntegrationPattern = Field(
        ..., description="Integration pattern used"
    )
    description: str = Field(
        ..., description="Description of what flows between components"
    )
    bidirectional: bool = Field(
        default=False, description="Whether the flow is bidirectional"
    )

    @field_validator("target_component_id")
    @classmethod
    def component_ids_must_be_different(cls, v, info):
        """Validate that source and target are different components."""
        if hasattr(info, "data") and "source_component_id" in info.data:
            if v == info.data["source_component_id"]:
                raise ValueError("Source and target component IDs must be different")
        return v


class TechnologyStack(BaseModel):
    """
    Model representing a collection of selected technology components.

    This model holds the user's technology selections and provides
    validation and organization capabilities.
    """

    name: str = Field(..., description="Name of the technology stack")
    description: str = Field(..., description="Description of the stack purpose")
    components: list[TechnologyComponent] = Field(
        default_factory=list, description="List of selected components"
    )
    integration_flows: list[IntegrationFlow] = Field(
        default_factory=list, description="List of integration flows between components"
    )

    def add_component(self, component: TechnologyComponent) -> bool:
        """
        Add a component to the stack with validation.

        Args:
            component: The component to add

        Returns:
            True if the component was added successfully

        Raises:
            ValueError: If the component conflicts with existing components
        """
        # Check for conflicts with existing components
        for existing in self.components:
            if component.conflicts_with(existing.id) or existing.conflicts_with(
                component.id
            ):
                raise ValueError(
                    f"Component {component.id} conflicts with {existing.id}"
                )

        # Check if component already exists
        if any(c.id == component.id for c in self.components):
            return False  # Already exists

        self.components.append(component)
        return True

    def remove_component(self, component_id: str) -> bool:
        """
        Remove a component from the stack.

        Args:
            component_id: ID of the component to remove

        Returns:
            True if the component was removed
        """
        original_length = len(self.components)
        self.components = [c for c in self.components if c.id != component_id]

        # Remove any flows involving this component
        self.integration_flows = [
            flow
            for flow in self.integration_flows
            if flow.source_component_id != component_id
            and flow.target_component_id != component_id
        ]

        return len(self.components) < original_length

    def get_component_by_id(self, component_id: str) -> Optional[TechnologyComponent]:
        """
        Get a component by its ID.

        Args:
            component_id: The ID of the component to retrieve

        Returns:
            The component if found, None otherwise
        """
        return next((c for c in self.components if c.id == component_id), None)

    def get_components_by_category(
        self, category: TechnologyCategory
    ) -> list[TechnologyComponent]:
        """
        Get all components in a specific category.

        Args:
            category: The category to filter by

        Returns:
            List of components in the specified category
        """
        return [c for c in self.components if c.category == category]

    def get_components_by_layer(self, layer: LayerType) -> list[TechnologyComponent]:
        """
        Get all components in a specific architectural layer.

        Args:
            layer: The layer to filter by

        Returns:
            List of components in the specified layer
        """
        return [c for c in self.components if c.layer == layer]

    def validate_dependencies(self) -> list[str]:
        """
        Validate that all component dependencies are satisfied.

        Returns:
            List of missing dependency error messages
        """
        errors = []
        component_ids = {c.id for c in self.components}

        for component in self.components:
            for dependency in component.dependencies:
                if dependency not in component_ids:
                    errors.append(
                        f"Component {component.id} requires {dependency} which is not selected"
                    )

        return errors

    def get_suggested_integrations(self) -> list[IntegrationFlow]:
        """
        Generate suggested integration flows based on component relationships.

        Returns:
            List of suggested integration flows
        """
        suggestions = []

        for component in self.components:
            for dependency in component.dependencies:
                dep_component = self.get_component_by_id(dependency)
                if dep_component:
                    # Find common integration patterns
                    common_patterns = set(component.integration_patterns) & set(
                        dep_component.integration_patterns
                    )
                    if common_patterns:
                        pattern = list(common_patterns)[0]  # Use first common pattern
                        flow_id = f"{dependency}_to_{component.id}"

                        # Check if flow already exists
                        if not any(f.id == flow_id for f in self.integration_flows):
                            suggestions.append(
                                IntegrationFlow(
                                    id=flow_id,
                                    name=f"{dep_component.name} → {component.name}",
                                    source_component_id=dependency,
                                    target_component_id=component.id,
                                    integration_pattern=pattern,
                                    description=f"Data flow from {dep_component.name} to {component.name}",
                                )
                            )

        return suggestions
