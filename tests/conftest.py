"""
Pytest configuration and shared fixtures for Microsoft Dynamics & Power Platform Architecture Builder tests.
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

from src.models.technology import TechnologyComponent, TechnologyCategory, LayerType, IntegrationPattern, TechnologyStack
from src.models.architecture import Architecture, DiagramConfig
from src.services.technology_catalog import TechnologyCatalog


@pytest.fixture
def sample_component_data() -> Dict[str, Any]:
    """Sample component data for testing."""
    return {
        "id": "test_component",
        "name": "Test Component",
        "category": "power_platform",
        "subcategory": "core",
        "description": "A test component for unit testing",
        "layer": "application",
        "dependencies": [],
        "conflicts": [],
        "integration_patterns": ["rest_api"],
        "is_core": True,
        "pricing_tier": "Standard"
    }


@pytest.fixture
def sample_component(sample_component_data) -> TechnologyComponent:
    """Sample TechnologyComponent instance for testing."""
    return TechnologyComponent(**sample_component_data)


@pytest.fixture
def sample_power_bi_component() -> TechnologyComponent:
    """Sample Power BI component for testing."""
    return TechnologyComponent(
        id="power_bi",
        name="Power BI",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="Business intelligence and data visualization",
        layer=LayerType.PRESENTATION,
        dependencies=[],
        conflicts=[],
        integration_patterns=[IntegrationPattern.REST_API, IntegrationPattern.ODATA],
        is_core=True,
        pricing_tier="Pro"
    )


@pytest.fixture
def sample_dataverse_component() -> TechnologyComponent:
    """Sample Dataverse component for testing."""
    return TechnologyComponent(
        id="dataverse",
        name="Microsoft Dataverse",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="Cloud-based data platform",
        layer=LayerType.DATA,
        dependencies=[],
        conflicts=[],
        integration_patterns=[IntegrationPattern.DATAVERSE_CONNECTOR, IntegrationPattern.WEB_API],
        is_core=True,
        pricing_tier="Standard"
    )


@pytest.fixture
def sample_power_apps_component() -> TechnologyComponent:
    """Sample Power Apps component for testing."""
    return TechnologyComponent(
        id="power_apps_canvas",
        name="Power Apps (Canvas)",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="Custom app development platform",
        layer=LayerType.PRESENTATION,
        dependencies=["dataverse"],
        conflicts=[],
        integration_patterns=[IntegrationPattern.DATAVERSE_CONNECTOR, IntegrationPattern.CUSTOM_CONNECTOR],
        is_core=True,
        pricing_tier="Premium"
    )


@pytest.fixture
def sample_technology_stack(sample_power_bi_component, sample_dataverse_component) -> TechnologyStack:
    """Sample TechnologyStack for testing."""
    stack = TechnologyStack(
        name="Test Stack",
        description="A test technology stack",
        components=[],
        integration_flows=[]
    )
    stack.add_component(sample_power_bi_component)
    stack.add_component(sample_dataverse_component)
    return stack


@pytest.fixture
def sample_architecture(sample_technology_stack) -> Architecture:
    """Sample Architecture for testing."""
    return Architecture(
        name="Test Architecture",
        description="A test architecture",
        technology_stack=sample_technology_stack
    )


@pytest.fixture
def sample_diagram_config() -> DiagramConfig:
    """Sample DiagramConfig for testing."""
    return DiagramConfig(
        format="png",
        filename="test_diagram",
        output_directory="test_output",
        width=800,
        height=600
    )


@pytest.fixture
def temp_catalog_file():
    """Temporary catalog file for testing."""
    catalog_data = {
        "power_platform": {
            "core": [
                {
                    "id": "test_power_bi",
                    "name": "Test Power BI",
                    "category": "power_platform",
                    "subcategory": "core",
                    "description": "Test BI component",
                    "layer": "presentation",
                    "dependencies": [],
                    "conflicts": [],
                    "integration_patterns": ["rest_api"],
                    "is_core": True,
                    "pricing_tier": "Pro"
                },
                {
                    "id": "test_dataverse",
                    "name": "Test Dataverse",
                    "category": "power_platform",
                    "subcategory": "core",
                    "description": "Test data platform",
                    "layer": "data",
                    "dependencies": [],
                    "conflicts": [],
                    "integration_patterns": ["dataverse_connector"],
                    "is_core": True,
                    "pricing_tier": "Standard"
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(catalog_data, f, indent=2)
        temp_file = Path(f.name)
    
    yield temp_file
    
    # Cleanup
    temp_file.unlink()


@pytest.fixture
def temp_catalog(temp_catalog_file) -> TechnologyCatalog:
    """Temporary TechnologyCatalog for testing."""
    return TechnologyCatalog(catalog_file=temp_catalog_file)


@pytest.fixture
def temp_output_dir():
    """Temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_components_with_dependencies():
    """Mock components with dependency relationships for testing."""
    # Create components with dependency chain: app -> dataverse -> security
    security = TechnologyComponent(
        id="azure_ad",
        name="Azure AD",
        category=TechnologyCategory.SECURITY_OPS,
        subcategory="identity",
        description="Identity and access management",
        layer=LayerType.SECURITY,
        dependencies=[],
        conflicts=[],
        integration_patterns=[IntegrationPattern.REST_API],
        is_core=True
    )
    
    dataverse = TechnologyComponent(
        id="dataverse",
        name="Dataverse",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="Data platform",
        layer=LayerType.DATA,
        dependencies=["azure_ad"],
        conflicts=[],
        integration_patterns=[IntegrationPattern.DATAVERSE_CONNECTOR],
        is_core=True
    )
    
    power_app = TechnologyComponent(
        id="power_app",
        name="Power App",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="Custom application",
        layer=LayerType.PRESENTATION,
        dependencies=["dataverse"],
        conflicts=[],
        integration_patterns=[IntegrationPattern.DATAVERSE_CONNECTOR],
        is_core=True
    )
    
    return [power_app, dataverse, security]


@pytest.fixture
def mock_components_with_conflicts():
    """Mock components with conflicts for testing."""
    copilot_studio = TechnologyComponent(
        id="copilot_studio",
        name="Copilot Studio",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="AI chatbot platform",
        layer=LayerType.APPLICATION,
        dependencies=[],
        conflicts=["power_virtual_agents"],
        integration_patterns=[IntegrationPattern.CUSTOM_CONNECTOR],
        is_core=False
    )
    
    power_virtual_agents = TechnologyComponent(
        id="power_virtual_agents",
        name="Power Virtual Agents",
        category=TechnologyCategory.POWER_PLATFORM,
        subcategory="core",
        description="Legacy chatbot platform",
        layer=LayerType.APPLICATION,
        dependencies=[],
        conflicts=["copilot_studio"],
        integration_patterns=[IntegrationPattern.CUSTOM_CONNECTOR],
        is_core=False
    )
    
    return [copilot_studio, power_virtual_agents]