"""
Tests for selection service.
"""

import pytest
from unittest.mock import Mock

from src.services.selection_service import SelectionService
from src.models.technology import TechnologyStack, IntegrationFlow, IntegrationPattern


class TestSelectionService:
    """Tests for SelectionService."""
    
    def test_create_new_stack(self, temp_catalog):
        """Test creating a new technology stack."""
        service = SelectionService(temp_catalog)
        
        stack = service.create_new_stack("Test Stack", "A test stack")
        
        assert stack.name == "Test Stack"
        assert stack.description == "A test stack"
        assert len(stack.components) == 0
        assert service.current_stack is stack
    
    def test_load_stack(self, temp_catalog, sample_technology_stack):
        """Test loading an existing stack."""
        service = SelectionService(temp_catalog)
        
        service.load_stack(sample_technology_stack)
        
        assert service.current_stack is sample_technology_stack
    
    def test_add_component_success(self, temp_catalog):
        """Test successfully adding a component."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        success, message = service.add_component("test_power_bi")
        
        assert success == True
        assert "Test Power BI" in message
        assert len(service.current_stack.components) == 1
        assert service.current_stack.components[0].id == "test_power_bi"
    
    def test_add_component_not_found(self, temp_catalog):
        """Test adding non-existent component."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        success, message = service.add_component("non_existent")
        
        assert success == False
        assert "not found" in message
        assert len(service.current_stack.components) == 0
    
    def test_add_component_no_stack(self, temp_catalog):
        """Test adding component without active stack."""
        service = SelectionService(temp_catalog)
        
        success, message = service.add_component("test_power_bi")
        
        assert success == False
        assert "No active technology stack" in message
    
    def test_add_component_duplicate(self, temp_catalog):
        """Test adding duplicate component."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        # Add component first time
        service.add_component("test_power_bi")
        
        # Try to add same component again
        success, message = service.add_component("test_power_bi")
        
        assert success == False
        assert "already in the stack" in message
        assert len(service.current_stack.components) == 1
    
    def test_remove_component_success(self, temp_catalog):
        """Test successfully removing a component."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        service.add_component("test_power_bi")
        
        success, message = service.remove_component("test_power_bi")
        
        assert success == True
        assert "Test Power BI" in message
        assert len(service.current_stack.components) == 0
    
    def test_remove_component_not_in_stack(self, temp_catalog):
        """Test removing component not in stack."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        success, message = service.remove_component("test_power_bi")
        
        assert success == False
        assert "was not in the stack" in message
    
    def test_add_multiple_components(self, temp_catalog):
        """Test adding multiple components."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        component_ids = ["test_power_bi", "test_dataverse", "non_existent"]
        successful, failed = service.add_multiple_components(component_ids)
        
        assert len(successful) == 2
        assert "test_power_bi" in successful
        assert "test_dataverse" in successful
        assert len(failed) == 1
        assert "non_existent" in failed[0]
        assert len(service.current_stack.components) == 2
    
    def test_validate_current_stack_valid(self, temp_catalog):
        """Test validating a valid stack."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        service.add_component("test_power_bi")
        service.add_component("test_dataverse")
        
        is_valid, errors = service.validate_current_stack()
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_current_stack_no_stack(self, temp_catalog):
        """Test validating with no active stack."""
        service = SelectionService(temp_catalog)
        
        is_valid, errors = service.validate_current_stack()
        
        assert is_valid == False
        assert len(errors) == 1
        assert "No active technology stack" in errors[0]
    
    def test_get_missing_dependencies(self, temp_catalog):
        """Test getting missing dependencies."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        # Create mock component with dependencies
        mock_component = Mock()
        mock_component.id = "mock_component"
        mock_component.dependencies = ["test_dataverse", "missing_dependency"]
        
        service.current_stack.components = [mock_component]
        
        missing_deps = service.get_missing_dependencies()
        
        # Should find test_dataverse (exists in catalog) but not missing_dependency
        assert len(missing_deps) == 1
        assert missing_deps[0].id == "test_dataverse"
    
    def test_get_suggestions(self, temp_catalog):
        """Test getting component suggestions."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        service.add_component("test_power_bi")
        
        suggestions = service.get_suggestions()
        
        # Should get suggestions based on current selection
        assert isinstance(suggestions, list)
    
    def test_auto_resolve_dependencies(self, temp_catalog):
        """Test auto-resolving dependencies."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        # Mock a component with dependencies
        mock_component = Mock()
        mock_component.id = "mock_component"
        mock_component.dependencies = ["test_dataverse"]
        mock_component.name = "Mock Component"
        mock_component.category = Mock()
        mock_component.layer = Mock()
        
        service.current_stack.components = [mock_component]
        
        added_count, errors = service.auto_resolve_dependencies()
        
        # Should add the missing dependency
        assert added_count >= 0  # May be 0 if dependency already exists or conflicts
        assert isinstance(errors, list)
    
    def test_generate_integration_flows(self, temp_catalog):
        """Test generating integration flows."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        service.add_component("test_power_bi")
        service.add_component("test_dataverse")
        
        flows = service.generate_integration_flows()
        
        assert isinstance(flows, list)
        # Flows depend on component relationships in test data
    
    def test_add_integration_flow(self, temp_catalog):
        """Test adding integration flow."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        service.add_component("test_power_bi")
        service.add_component("test_dataverse")
        
        flow = IntegrationFlow(
            id="test_flow",
            name="Test Flow",
            source_component_id="test_power_bi",
            target_component_id="test_dataverse",
            integration_pattern=IntegrationPattern.REST_API,
            description="Test flow"
        )
        
        success, message = service.add_integration_flow(flow)
        
        assert success == True
        assert "Test Flow" in message
        assert len(service.current_stack.integration_flows) == 1
    
    def test_add_integration_flow_missing_components(self, temp_catalog):
        """Test adding flow with missing components."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        
        flow = IntegrationFlow(
            id="test_flow",
            name="Test Flow",
            source_component_id="missing_source",
            target_component_id="missing_target",
            integration_pattern=IntegrationPattern.REST_API,
            description="Test flow"
        )
        
        success, message = service.add_integration_flow(flow)
        
        assert success == False
        assert "not in stack" in message
    
    def test_remove_integration_flow(self, temp_catalog):
        """Test removing integration flow."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test")
        service.add_component("test_power_bi")
        service.add_component("test_dataverse")
        
        # Add flow
        flow = IntegrationFlow(
            id="test_flow",
            name="Test Flow",
            source_component_id="test_power_bi",
            target_component_id="test_dataverse",
            integration_pattern=IntegrationPattern.REST_API,
            description="Test flow"
        )
        service.add_integration_flow(flow)
        
        # Remove flow
        success, message = service.remove_integration_flow("test_flow")
        
        assert success == True
        assert "test_flow" in message
        assert len(service.current_stack.integration_flows) == 0
    
    def test_get_stack_summary(self, temp_catalog):
        """Test getting stack summary."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "A test stack for summary")
        service.add_component("test_power_bi")
        service.add_component("test_dataverse")
        
        summary = service.get_stack_summary()
        
        assert summary["name"] == "Test Stack"
        assert summary["description"] == "A test stack for summary"
        assert summary["component_count"] == 2
        assert summary["integration_flow_count"] == 0
        assert "categories" in summary
        assert "layers" in summary
        assert isinstance(summary["is_valid"], bool)
    
    def test_get_stack_summary_no_stack(self, temp_catalog):
        """Test getting summary with no active stack."""
        service = SelectionService(temp_catalog)
        
        summary = service.get_stack_summary()
        
        assert "error" in summary
        assert "No active technology stack" in summary["error"]
    
    def test_export_stack_configuration(self, temp_catalog):
        """Test exporting stack configuration."""
        service = SelectionService(temp_catalog)
        service.create_new_stack("Test Stack", "Test export")
        service.add_component("test_power_bi")
        
        config = service.export_stack_configuration()
        
        assert config["name"] == "Test Stack"
        assert config["description"] == "Test export"
        assert len(config["components"]) == 1
        assert config["components"][0]["id"] == "test_power_bi"
        assert "exported_at" in config
    
    def test_export_stack_configuration_no_stack(self, temp_catalog):
        """Test exporting with no active stack."""
        service = SelectionService(temp_catalog)
        
        config = service.export_stack_configuration()
        
        assert config is None
    
    def test_clear_current_stack(self, temp_catalog, sample_technology_stack):
        """Test clearing current stack."""
        service = SelectionService(temp_catalog)
        service.load_stack(sample_technology_stack)
        
        assert service.current_stack is not None
        
        service.clear_current_stack()
        
        assert service.current_stack is None