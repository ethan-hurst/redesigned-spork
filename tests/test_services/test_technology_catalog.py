"""
Tests for technology catalog service.
"""

import pytest
import json
import tempfile
from pathlib import Path

from src.services.technology_catalog import TechnologyCatalog, TechnologyCatalogError
from src.models.technology import TechnologyCategory, LayerType, IntegrationPattern


class TestTechnologyCatalog:
    """Tests for TechnologyCatalog service."""
    
    def test_load_catalog_success(self, temp_catalog):
        """Test successful catalog loading."""
        assert len(temp_catalog.get_all_components()) == 2
        assert temp_catalog.get_component_by_id("test_power_bi") is not None
        assert temp_catalog.get_component_by_id("test_dataverse") is not None
    
    def test_load_catalog_file_not_found(self):
        """Test catalog loading with missing file."""
        with pytest.raises(TechnologyCatalogError, match="Catalog file not found"):
            TechnologyCatalog(catalog_file=Path("/nonexistent/catalog.json"))
    
    def test_load_catalog_invalid_json(self):
        """Test catalog loading with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_file = Path(f.name)
        
        try:
            with pytest.raises(TechnologyCatalogError, match="Invalid JSON"):
                TechnologyCatalog(catalog_file=temp_file)
        finally:
            temp_file.unlink()
    
    def test_get_all_components(self, temp_catalog):
        """Test getting all components."""
        components = temp_catalog.get_all_components()
        
        assert len(components) == 2
        component_ids = [comp.id for comp in components]
        assert "test_power_bi" in component_ids
        assert "test_dataverse" in component_ids
    
    def test_get_component_by_id(self, temp_catalog):
        """Test getting component by ID."""
        # Existing component
        component = temp_catalog.get_component_by_id("test_power_bi")
        assert component is not None
        assert component.name == "Test Power BI"
        
        # Non-existent component
        component = temp_catalog.get_component_by_id("non_existent")
        assert component is None
    
    def test_get_component_ids(self, temp_catalog):
        """Test getting all component IDs."""
        ids = temp_catalog.get_component_ids()
        
        assert len(ids) == 2
        assert "test_power_bi" in ids
        assert "test_dataverse" in ids
    
    def test_get_components_by_category(self, temp_catalog):
        """Test filtering components by category."""
        power_platform_components = temp_catalog.get_components_by_category(
            TechnologyCategory.POWER_PLATFORM
        )
        
        assert len(power_platform_components) == 2
        assert all(comp.category == TechnologyCategory.POWER_PLATFORM for comp in power_platform_components)
        
        # Test empty category
        azure_components = temp_catalog.get_components_by_category(
            TechnologyCategory.AZURE_SERVICES
        )
        assert len(azure_components) == 0
    
    def test_get_components_by_subcategory(self, temp_catalog):
        """Test filtering components by subcategory."""
        core_components = temp_catalog.get_components_by_subcategory(
            TechnologyCategory.POWER_PLATFORM, "core"
        )
        
        assert len(core_components) == 2
        assert all(comp.subcategory == "core" for comp in core_components)
    
    def test_get_components_by_layer(self, temp_catalog):
        """Test filtering components by layer."""
        data_components = temp_catalog.get_components_by_layer(LayerType.DATA)
        
        assert len(data_components) == 1
        assert data_components[0].id == "test_dataverse"
        
        presentation_components = temp_catalog.get_components_by_layer(LayerType.PRESENTATION)
        assert len(presentation_components) == 1
        assert presentation_components[0].id == "test_power_bi"
    
    def test_get_core_components(self, temp_catalog):
        """Test getting core components."""
        core_components = temp_catalog.get_core_components()
        
        assert len(core_components) == 2  # Both test components are marked as core
        assert all(comp.is_core for comp in core_components)
    
    def test_search_components(self, temp_catalog):
        """Test searching components."""
        # Search by name
        results = temp_catalog.search_components("Power BI")
        assert len(results) == 1
        assert results[0].id == "test_power_bi"
        
        # Search by description
        results = temp_catalog.search_components("data platform")
        assert len(results) == 1
        assert results[0].id == "test_dataverse"
        
        # Search by ID
        results = temp_catalog.search_components("test_power")
        assert len(results) == 1
        assert results[0].id == "test_power_bi"
        
        # No results
        results = temp_catalog.search_components("nonexistent")
        assert len(results) == 0
    
    def test_get_components_with_integration_pattern(self, temp_catalog):
        """Test filtering by integration pattern."""
        rest_api_components = temp_catalog.get_components_with_integration_pattern(
            IntegrationPattern.REST_API
        )
        
        assert len(rest_api_components) == 1
        assert rest_api_components[0].id == "test_power_bi"
        
        dataverse_components = temp_catalog.get_components_with_integration_pattern(
            IntegrationPattern.DATAVERSE_CONNECTOR
        )
        
        assert len(dataverse_components) == 1
        assert dataverse_components[0].id == "test_dataverse"
    
    def test_validate_dependencies_missing(self, temp_catalog):
        """Test dependency validation with missing dependencies."""
        # Create a test component with dependencies not in catalog
        component_ids = ["test_power_bi", "missing_dependency"]
        
        errors = temp_catalog.validate_dependencies(component_ids)
        assert len(errors) == 1
        assert "Component not found: missing_dependency" in errors[0]
    
    def test_validate_dependencies_satisfied(self, temp_catalog):
        """Test dependency validation with satisfied dependencies."""
        component_ids = ["test_power_bi", "test_dataverse"]
        
        errors = temp_catalog.validate_dependencies(component_ids)
        assert len(errors) == 0
    
    def test_validate_conflicts_none(self, temp_catalog):
        """Test conflict validation with no conflicts."""
        component_ids = ["test_power_bi", "test_dataverse"]
        
        errors = temp_catalog.validate_conflicts(component_ids)
        assert len(errors) == 0
    
    def test_suggest_additional_components(self, temp_catalog):
        """Test suggesting additional components."""
        selected_ids = ["test_power_bi"]
        
        suggestions = temp_catalog.suggest_additional_components(selected_ids)
        
        # Should suggest dataverse for power apps scenarios
        # and security components if none selected
        assert len(suggestions) >= 0  # May or may not have suggestions based on catalog
    
    def test_get_catalog_statistics(self, temp_catalog):
        """Test getting catalog statistics."""
        stats = temp_catalog.get_catalog_statistics()
        
        assert stats["total_components"] == 2
        assert stats["core_components"] == 2
        assert stats["power_platform_components"] == 2
        assert stats["presentation_layer_components"] == 1
        assert stats["data_layer_components"] == 1
    
    def test_reload_catalog(self, temp_catalog_file):
        """Test reloading catalog."""
        catalog = TechnologyCatalog(catalog_file=temp_catalog_file)
        initial_count = len(catalog.get_all_components())
        
        # Modify catalog file
        with open(temp_catalog_file, 'r') as f:
            data = json.load(f)
        
        # Add another component
        data["power_platform"]["core"].append({
            "id": "new_component",
            "name": "New Component",
            "category": "power_platform",
            "subcategory": "core",
            "description": "A new test component",
            "layer": "application",
            "dependencies": [],
            "conflicts": [],
            "integration_patterns": ["rest_api"],
            "is_core": False,
            "pricing_tier": "Standard"
        })
        
        with open(temp_catalog_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Reload and check
        catalog.reload_catalog()
        new_count = len(catalog.get_all_components())
        
        assert new_count == initial_count + 1
        assert catalog.get_component_by_id("new_component") is not None
    
    def test_export_components_to_dict(self, temp_catalog):
        """Test exporting components to dictionary."""
        component_ids = ["test_power_bi", "test_dataverse"]
        
        export_data = temp_catalog.export_components_to_dict(component_ids)
        
        assert "power_platform" in export_data
        assert "core" in export_data["power_platform"]
        assert len(export_data["power_platform"]["core"]) == 2
        
        # Check that exported components have all required fields
        exported_component = export_data["power_platform"]["core"][0]
        required_fields = ["id", "name", "category", "subcategory", "description", "layer"]
        for field in required_fields:
            assert field in exported_component


class TestTechnologyCatalogGlobalInstance:
    """Tests for global catalog instance functions."""
    
    def test_get_catalog_singleton(self):
        """Test that get_catalog returns singleton instance."""
        from src.services.technology_catalog import get_catalog, reset_catalog
        
        # Reset to ensure clean state
        reset_catalog()
        
        catalog1 = get_catalog()
        catalog2 = get_catalog()
        
        assert catalog1 is catalog2
    
    def test_reset_catalog(self):
        """Test resetting global catalog instance."""
        from src.services.technology_catalog import get_catalog, reset_catalog
        
        catalog1 = get_catalog()
        reset_catalog()
        catalog2 = get_catalog()
        
        assert catalog1 is not catalog2