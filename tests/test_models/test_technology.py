"""
Tests for technology models.
"""

import pytest
from pydantic import ValidationError

from src.models.technology import (
    TechnologyComponent, 
    TechnologyCategory, 
    LayerType, 
    IntegrationPattern,
    IntegrationFlow,
    TechnologyStack
)


class TestTechnologyComponent:
    """Tests for TechnologyComponent model."""
    
    def test_create_valid_component(self, sample_component_data):
        """Test creating a valid technology component."""
        component = TechnologyComponent(**sample_component_data)
        
        assert component.id == "test_component"
        assert component.name == "Test Component"
        assert component.category == TechnologyCategory.POWER_PLATFORM
        assert component.layer == LayerType.APPLICATION
        assert component.is_core == True
    
    def test_component_id_validation(self, sample_component_data):
        """Test component ID validation."""
        # Invalid ID with uppercase
        sample_component_data["id"] = "TEST_Component"
        with pytest.raises(ValidationError):
            TechnologyComponent(**sample_component_data)
        
        # Invalid ID with spaces
        sample_component_data["id"] = "test component"
        with pytest.raises(ValidationError):
            TechnologyComponent(**sample_component_data)
        
        # Valid ID
        sample_component_data["id"] = "test_component_123"
        component = TechnologyComponent(**sample_component_data)
        assert component.id == "test_component_123"
    
    def test_has_dependency(self, sample_power_apps_component):
        """Test dependency checking."""
        assert sample_power_apps_component.has_dependency("dataverse")
        assert not sample_power_apps_component.has_dependency("power_bi")
    
    def test_conflicts_with(self, mock_components_with_conflicts):
        """Test conflict checking."""
        copilot, virtual_agents = mock_components_with_conflicts
        
        assert copilot.conflicts_with("power_virtual_agents")
        assert virtual_agents.conflicts_with("copilot_studio")
        assert not copilot.conflicts_with("dataverse")
    
    def test_supports_integration(self, sample_power_bi_component):
        """Test integration pattern support."""
        assert sample_power_bi_component.supports_integration(IntegrationPattern.REST_API)
        assert sample_power_bi_component.supports_integration(IntegrationPattern.ODATA)
        assert not sample_power_bi_component.supports_integration(IntegrationPattern.SERVICE_BUS)


class TestIntegrationFlow:
    """Tests for IntegrationFlow model."""
    
    def test_create_valid_flow(self):
        """Test creating a valid integration flow."""
        flow = IntegrationFlow(
            id="test_flow",
            name="Test Flow",
            source_component_id="power_bi",
            target_component_id="dataverse",
            integration_pattern=IntegrationPattern.REST_API,
            description="Test integration flow"
        )
        
        assert flow.id == "test_flow"
        assert flow.source_component_id == "power_bi"
        assert flow.target_component_id == "dataverse"
        assert flow.bidirectional == False
    
    def test_flow_validation_different_components(self):
        """Test that source and target components must be different."""
        with pytest.raises(ValidationError):
            IntegrationFlow(
                id="invalid_flow",
                name="Invalid Flow",
                source_component_id="same_component",
                target_component_id="same_component",
                integration_pattern=IntegrationPattern.REST_API,
                description="Invalid flow"
            )


class TestTechnologyStack:
    """Tests for TechnologyStack model."""
    
    def test_create_empty_stack(self):
        """Test creating an empty technology stack."""
        stack = TechnologyStack(
            name="Empty Stack",
            description="An empty stack for testing"
        )
        
        assert stack.name == "Empty Stack"
        assert len(stack.components) == 0
        assert len(stack.integration_flows) == 0
    
    def test_add_component(self, sample_power_bi_component):
        """Test adding a component to the stack."""
        stack = TechnologyStack(name="Test Stack", description="Test")
        
        # Add component successfully
        success = stack.add_component(sample_power_bi_component)
        assert success == True
        assert len(stack.components) == 1
        assert stack.components[0].id == "power_bi"
        
        # Try to add same component again
        success = stack.add_component(sample_power_bi_component)
        assert success == False
        assert len(stack.components) == 1
    
    def test_add_conflicting_components(self, mock_components_with_conflicts):
        """Test adding conflicting components."""
        stack = TechnologyStack(name="Test Stack", description="Test")
        copilot, virtual_agents = mock_components_with_conflicts
        
        # Add first component
        success = stack.add_component(copilot)
        assert success == True
        
        # Try to add conflicting component
        with pytest.raises(ValueError):
            stack.add_component(virtual_agents)
    
    def test_remove_component(self, sample_technology_stack):
        """Test removing a component from the stack."""
        initial_count = len(sample_technology_stack.components)
        
        # Remove existing component
        success = sample_technology_stack.remove_component("power_bi")
        assert success == True
        assert len(sample_technology_stack.components) == initial_count - 1
        
        # Try to remove non-existent component
        success = sample_technology_stack.remove_component("non_existent")
        assert success == False
    
    def test_get_component_by_id(self, sample_technology_stack):
        """Test retrieving component by ID."""
        component = sample_technology_stack.get_component_by_id("power_bi")
        assert component is not None
        assert component.name == "Power BI"
        
        component = sample_technology_stack.get_component_by_id("non_existent")
        assert component is None
    
    def test_get_components_by_category(self, sample_technology_stack):
        """Test filtering components by category."""
        power_platform_components = sample_technology_stack.get_components_by_category(
            TechnologyCategory.POWER_PLATFORM
        )
        
        assert len(power_platform_components) == 2  # Power BI and Dataverse
        assert all(comp.category == TechnologyCategory.POWER_PLATFORM for comp in power_platform_components)
    
    def test_get_components_by_layer(self, sample_technology_stack):
        """Test filtering components by layer."""
        data_components = sample_technology_stack.get_components_by_layer(LayerType.DATA)
        
        assert len(data_components) == 1
        assert data_components[0].id == "dataverse"
    
    def test_validate_dependencies_missing(self, mock_components_with_dependencies):
        """Test dependency validation with missing dependencies."""
        stack = TechnologyStack(name="Test Stack", description="Test")
        power_app, dataverse, security = mock_components_with_dependencies
        
        # Add only the power app (missing its dependencies)
        stack.add_component(power_app)
        
        errors = stack.validate_dependencies()
        assert len(errors) == 1
        assert "dataverse" in errors[0]
    
    def test_validate_dependencies_satisfied(self, mock_components_with_dependencies):
        """Test dependency validation with satisfied dependencies."""
        stack = TechnologyStack(name="Test Stack", description="Test")
        power_app, dataverse, security = mock_components_with_dependencies
        
        # Add all components
        for component in [security, dataverse, power_app]:
            stack.add_component(component)
        
        errors = stack.validate_dependencies()
        assert len(errors) == 0
    
    def test_get_suggested_integrations(self, mock_components_with_dependencies):
        """Test getting suggested integration flows."""
        stack = TechnologyStack(name="Test Stack", description="Test")
        power_app, dataverse, security = mock_components_with_dependencies
        
        # Add all components
        for component in [security, dataverse, power_app]:
            stack.add_component(component)
        
        suggestions = stack.get_suggested_integrations()
        
        # Should suggest flows based on dependencies
        assert len(suggestions) >= 1  # At least one flow should be suggested
        
        # Check that suggested flows have valid IDs
        flow_ids = [flow.id for flow in suggestions]
        assert len(flow_ids) > 0  # Should have at least one suggested flow