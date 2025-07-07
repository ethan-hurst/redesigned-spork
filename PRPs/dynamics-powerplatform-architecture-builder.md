name: "Dynamics & Power Platform Architecture Builder"
description: |

## Purpose
To build a comprehensive toolset that prompts users for their Microsoft Dynamics 365 and Power Platform technology stack, then generates accurate and detailed architectural reference diagrams based on their selections.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Create an interactive toolset that allows users to select from Microsoft Azure, Dynamics 365, and Power Platform technologies to generate comprehensive architectural reference diagrams, in both image and visio formats.

## Why
- Reduce time spent creating architectural documentation from scratch
- Ensure architectural diagrams follow Microsoft best practices and patterns
- Provide standardized visual references for enterprise technology stacks
- Enable rapid prototyping and planning of Microsoft-based solutions

## What
A Python-based command-line tool that:
1. Presents categorized lists of Microsoft technologies (Azure, Dynamics 365, Power Platform)
2. Allows users to select components they're using or planning to use
3. Generates architectural diagrams showing component relationships and data flow
4. Exports diagrams in multiple formats (PNG, SVG, PDF)
5. Includes integration patterns and best practices documentation

### Success Criteria
- [ ] Interactive CLI tool with technology selection interface
- [ ] Comprehensive catalog of Microsoft technologies organized by category
- [ ] Architectural diagram generation with proper component relationships
- [ ] Multiple export formats supported
- [ ] Integration patterns and data flow documentation
- [ ] Validation of component compatibility and dependencies
- [ ] Professional-quality diagrams matching Microsoft architectural standards

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://learn.microsoft.com/en-us/power-platform/
  why: Official Power Platform documentation with architecture patterns
  
- url: https://learn.microsoft.com/en-us/dynamics365/
  why: Dynamics 365 documentation with integration patterns
  
- url: https://learn.microsoft.com/en-us/azure/architecture/solutions/power-platform-scenarios
  why: Azure architecture patterns for Power Platform integration
  
- url: https://learn.microsoft.com/en-us/power-platform/guidance/icons
  why: Official Microsoft Power Platform icons for diagrams
  
- url: https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/integrate-other-solutions-choose-design
  why: Integration design patterns for Dynamics 365
  
- url: https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview
  why: Azure Logic Apps integration patterns
  
- url: https://learn.microsoft.com/en-us/azure/azure-functions/functions-compare-logic-apps-ms-flow-webjobs
  why: Azure integration services comparison and selection guidance
  
- file: examples/CaseMgmt_Polished_v2.png
  why: Example architectural diagram showing Microsoft stack with proper layout, icons, and flow patterns
  
- file: CLAUDE.md
  why: Project guidelines for code structure, testing, and documentation requirements
```

### Current Codebase Tree
```bash
/workspaces/redesigned-spork
├── .claude/                    # Claude Code configuration
├── .git/                       # Git repository
├── PRPs/                       # Product Requirements Prompts
│   └── templates/
│       └── prp_base.md        # PRP template
├── examples/                   # Reference examples
│   └── CaseMgmt_Polished_v2.png  # Example architectural diagram
├── CLAUDE.md                   # Project guidelines
├── INITIAL.md                  # Feature requirements
├── README.md                   # Project documentation
└── LICENSE                     # License file
```

### Desired Codebase Tree
```bash
/workspaces/redesigned-spork
├── src/                        # Main source code
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── technology.py       # Technology definition models
│   │   ├── architecture.py     # Architecture model
│   │   └── diagram.py          # Diagram generation models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── technology_catalog.py  # Technology catalog management
│   │   ├── selection_service.py   # User selection logic
│   │   ├── architecture_generator.py  # Architecture generation
│   │   └── diagram_exporter.py     # Diagram export functionality
│   ├── cli/                    # CLI interface
│   │   ├── __init__.py
│   │   ├── commands.py         # CLI commands
│   │   └── prompts.py          # Interactive prompts
│   ├── data/                   # Static data
│   │   ├── __init__.py
│   │   ├── technologies.json   # Technology catalog
│   │   └── templates/          # Diagram templates
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── validators.py       # Input validation
│       └── helpers.py          # Common helpers
├── tests/                      # Test files
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_models/
│   ├── test_services/
│   ├── test_cli/
│   └── conftest.py            # Pytest configuration
├── docs/                      # Documentation
│   ├── README.md
│   └── architecture.md
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
└── setup.py                  # Package setup
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Diagram generation libraries
# Use 'diagrams' library (diagrams-python) for creating architecture diagrams
# Requires Graphviz to be installed on system: apt-get install graphviz
# Example: from diagrams import Diagram, Edge
# Example: from diagrams.azure.analytics import PowerBi

# CRITICAL: CLI Framework
# Use 'click' for command-line interface - provides rich interaction support
# Use 'rich' for beautiful console output and progress bars
# Use 'questionary' for interactive prompts and selections

# CRITICAL: Data validation
# Use pydantic v2 for data models and validation
# All models must inherit from BaseModel

# CRITICAL: File handling
# Use pathlib for path operations, not os.path
# Use python-dotenv for environment variables if needed

# CRITICAL: JSON handling
# Use json.dumps with indent=2 for pretty printing
# Use typing.Dict and typing.List for type hints
```

## Implementation Blueprint

### Data Models and Structure

Create comprehensive data models that represent the Microsoft technology ecosystem with proper categorization and relationships.

```python
# Technology definition model
class TechnologyComponent(BaseModel):
    id: str
    name: str
    category: str  # 'power_platform', 'dynamics_365', 'azure_services', 'security_ops'
    subcategory: str
    description: str
    icon_path: Optional[str] = None
    dependencies: List[str] = []
    conflicts: List[str] = []
    integration_patterns: List[str] = []

# Architecture model
class Architecture(BaseModel):
    name: str
    description: str
    selected_components: List[TechnologyComponent]
    integration_flows: List[IntegrationFlow]
    layers: Dict[str, List[TechnologyComponent]]
```

### Technology Catalog Structure

Based on research, organize technologies into these categories:

**Power Platform Core:**
- Power Apps (Canvas & Model-driven)
- Power Automate
- Power BI
- Power Pages
- Microsoft Copilot Studio
- Power Virtual Agents
- Dataverse
- AI Builder
- Power Fx

**Dynamics 365 Applications:**
- Dynamics 365 Sales
- Dynamics 365 Marketing (Customer Insights - Journeys)
- Dynamics 365 Customer Service
- Dynamics 365 Field Service
- Dynamics 365 Business Central
- Dynamics 365 Finance & Operations

**Azure Integration Services:**
- Azure Logic Apps
- Azure Functions
- Azure Service Bus
- Azure Event Grid
- Azure Data Factory
- Azure API Management
- Azure Data Lake Gen2
- Azure Synapse Analytics

**Security & Operations:**
- Azure Active Directory (Microsoft Entra ID)
- Azure Key Vault
- Microsoft Defender
- Azure Application Insights
- Azure Monitor
- Azure Log Analytics

### List of Tasks (Implementation Order)

```yaml
Task 1: Set up project structure and dependencies
CREATE pyproject.toml:
  - INCLUDE dependencies: click, rich, questionary, pydantic, diagrams, pillow
  - CONFIGURE black, ruff, mypy for code quality
  - SET python version requirement >= 3.9

CREATE requirements.txt:
  - MIRROR dependencies from pyproject.toml for compatibility

CREATE src/__init__.py and all module __init__.py files

Task 2: Create core data models
CREATE src/models/technology.py:
  - DEFINE TechnologyComponent model with all required fields
  - DEFINE IntegrationFlow model for component relationships
  - INCLUDE validation for component compatibility

CREATE src/models/architecture.py:
  - DEFINE Architecture model containing selected components
  - DEFINE layer organization (Presentation, Application, Integration, Data)
  - INCLUDE methods for component validation and conflict detection

Task 3: Build technology catalog
CREATE src/data/technologies.json:
  - POPULATE with comprehensive Microsoft technology catalog
  - ORGANIZE by categories (Power Platform, Dynamics 365, Azure, Security)
  - INCLUDE dependencies and integration patterns for each component

CREATE src/services/technology_catalog.py:
  - IMPLEMENT catalog loading and querying functionality
  - PROVIDE filtering by category and search capabilities
  - INCLUDE validation of technology definitions

Task 4: Implement CLI interface
CREATE src/cli/commands.py:
  - IMPLEMENT main command structure using click
  - CREATE interactive selection interface using questionary
  - PROVIDE technology browsing and selection functionality

CREATE src/cli/prompts.py:
  - IMPLEMENT multi-select prompts for technology selection
  - PROVIDE category-based navigation
  - INCLUDE confirmation and preview functionality

Task 5: Create architecture generation service
CREATE src/services/architecture_generator.py:
  - IMPLEMENT architecture validation (dependencies, conflicts)
  - ORGANIZE components into appropriate layers
  - GENERATE integration flow recommendations

CREATE src/services/selection_service.py:
  - IMPLEMENT user selection persistence
  - PROVIDE selection validation and suggestions
  - INCLUDE compatibility checking

Task 6: Build diagram generation system
CREATE src/services/diagram_exporter.py:
  - IMPLEMENT diagram generation using diagrams library
  - MIRROR layout patterns from examples/CaseMgmt_Polished_v2.png
  - SUPPORT multiple export formats (PNG, SVG, PDF)
  - INCLUDE proper Microsoft icons and styling

Task 7: Create main CLI application
CREATE src/main.py:
  - IMPLEMENT main entry point using click
  - COORDINATE all services and CLI components
  - PROVIDE help and usage information

Task 8: Add comprehensive testing
CREATE tests/test_models/:
  - TEST data model validation and serialization
  - TEST component compatibility and conflict detection

CREATE tests/test_services/:
  - TEST technology catalog operations
  - TEST architecture generation logic
  - TEST diagram export functionality

CREATE tests/test_cli/:
  - TEST CLI command functionality
  - TEST interactive prompts (using pytest-mock)

Task 9: Create documentation
CREATE docs/README.md:
  - PROVIDE installation and usage instructions
  - INCLUDE examples and screenshots
  - DOCUMENT architecture patterns and best practices

Task 10: Package and finalize
CREATE setup.py:
  - CONFIGURE package installation
  - INCLUDE console script entry point
  - SET proper metadata and dependencies
```

### Per Task Pseudocode

```python
# Task 1: Project Setup
# pyproject.toml structure
[tool.poetry]
name = "dynamics-powerplatform-architecture-builder"
version = "0.1.0"
description = "Generate architectural diagrams for Microsoft Dynamics & Power Platform stacks"

[tool.poetry.dependencies]
python = "^3.9"
click = "^8.1.0"
rich = "^13.0.0"
questionary = "^2.0.0"
pydantic = "^2.0.0"
diagrams = "^0.23.0"
pillow = "^10.0.0"

# Task 3: Technology Catalog Structure
technologies = {
    "power_platform": {
        "core": [
            {
                "id": "power_apps_canvas",
                "name": "Power Apps (Canvas)",
                "category": "power_platform",
                "subcategory": "core",
                "description": "Create custom apps with complete control over UI",
                "dependencies": ["dataverse"],
                "integration_patterns": ["dataverse_connector", "custom_connector"]
            }
        ]
    }
}

# Task 4: CLI Interface Pattern
@click.command()
@click.option('--output', '-o', default='architecture.png', help='Output file path')
def generate_architecture(output):
    """Generate Microsoft technology architecture diagram"""
    # Use questionary for interactive selection
    selected_categories = questionary.checkbox(
        "Select technology categories:",
        choices=["Power Platform", "Dynamics 365", "Azure Services", "Security & Ops"]
    ).ask()
    
    # Continue with component selection within categories
    for category in selected_categories:
        components = get_category_components(category)
        selected = questionary.checkbox(
            f"Select {category} components:",
            choices=[comp.name for comp in components]
        ).ask()

# Task 6: Diagram Generation Pattern
from diagrams import Diagram, Edge
from diagrams.azure.analytics import PowerBi
from diagrams.azure.integration import LogicApps

def generate_diagram(architecture: Architecture, output_path: str):
    """Generate architectural diagram matching Microsoft patterns"""
    
    with Diagram("Microsoft Technology Architecture", filename=output_path, show=False):
        # Create layers like in the example
        presentation_layer = []
        application_layer = []
        integration_layer = []
        data_layer = []
        
        # Organize components by layer
        for component in architecture.selected_components:
            if component.category == "presentation":
                presentation_layer.append(create_component_node(component))
            elif component.category == "application":
                application_layer.append(create_component_node(component))
            # ... etc
        
        # Connect components based on integration patterns
        for flow in architecture.integration_flows:
            source_node >> Edge(label=flow.type) >> target_node
```

### Integration Points
```yaml
DEPENDENCIES:
  - system: "apt-get install graphviz"  # Required for diagrams library
  - python: ">=3.9"
  - libraries: "click, rich, questionary, pydantic, diagrams, pillow"

CONFIG:
  - add to: src/config/settings.py
  - pattern: "OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'output'))"
  - pattern: "TEMPLATE_DIR = Path(__file__).parent / 'data' / 'templates'"

CLI:
  - entry point: "dynamics-arch-builder"
  - command pattern: "dynamics-arch-builder generate --interactive"
  - help: "dynamics-arch-builder --help"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check src/ --fix           # Auto-fix what's possible
ruff format src/                # Format code
mypy src/                       # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE comprehensive test suite
def test_technology_catalog_loading():
    """Technology catalog loads correctly"""
    catalog = TechnologyCatalog()
    assert len(catalog.get_all_technologies()) > 0
    assert "power_apps_canvas" in catalog.get_component_ids()

def test_architecture_validation():
    """Architecture validation works correctly"""
    arch = Architecture(selected_components=[power_apps, dataverse])
    assert arch.validate_dependencies() == True
    
def test_diagram_generation():
    """Diagram generation creates valid output"""
    arch = Architecture(selected_components=[power_apps, power_bi])
    output_path = "test_diagram.png"
    generate_diagram(arch, output_path)
    assert Path(output_path).exists()

def test_cli_integration():
    """CLI commands work correctly"""
    result = runner.invoke(main, ['generate', '--help'])
    assert result.exit_code == 0
    assert "Generate Microsoft technology architecture" in result.output
```

```bash
# Run and iterate until passing:
pytest tests/ -v --cov=src/
# Expected: All tests pass with >90% coverage
```

### Level 3: Integration Test
```bash
# Install the package in development mode
pip install -e .

# Test basic functionality
dynamics-arch-builder --help
# Expected: Help text displays correctly

# Test interactive generation
dynamics-arch-builder generate --interactive
# Expected: Interactive prompts appear and diagram is generated

# Test with specific selections
dynamics-arch-builder generate --components power_apps,power_bi,dataverse --output test_arch.png
# Expected: Diagram file created at test_arch.png
```

## Final Validation Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linting errors: `ruff check src/`
- [ ] No type errors: `mypy src/`
- [ ] CLI help works: `dynamics-arch-builder --help`
- [ ] Interactive mode works: `dynamics-arch-builder generate --interactive`
- [ ] Diagram generation works: Output files created and valid
- [ ] Technology catalog complete: All major Microsoft technologies included
- [ ] Architecture validation works: Dependencies and conflicts detected
- [ ] Export formats supported: PNG, SVG, PDF all working
- [ ] Documentation complete: README and usage examples provided

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode technology lists - use JSON catalog for flexibility
- ❌ Don't skip dependency validation - components must be compatible
- ❌ Don't ignore the example diagram layout - follow Microsoft patterns
- ❌ Don't use sync operations for file I/O - use async where beneficial
- ❌ Don't create overly complex CLI - keep it simple and intuitive
- ❌ Don't skip error handling - provide helpful error messages
- ❌ Don't forget to install system dependencies (graphviz)
- ❌ Don't mix different diagramming libraries - stick to 'diagrams'
- ❌ Don't ignore component relationships - show proper integration flows
- ❌ Don't create static diagrams - make them configurable and dynamic

## Architecture Patterns to Follow
- ✅ Layer-based organization (Presentation, Application, Integration, Data)
- ✅ Component-based architecture with clear interfaces
- ✅ Dependency injection for services
- ✅ Validation at model level using Pydantic
- ✅ Rich CLI experience with interactive prompts
- ✅ Comprehensive testing with fixtures
- ✅ Configuration-driven behavior
- ✅ Proper error handling and logging
- ✅ Extensible technology catalog
- ✅ Multiple export formats for flexibility

## PRP Quality Assessment

### Confidence Score: 8/10

**Rationale for Score:**
- ✅ **Comprehensive Context** (9/10): Extensive research on Microsoft ecosystem with official documentation URLs
- ✅ **Clear Implementation Path** (9/10): 10 well-defined tasks in logical order with pseudocode examples
- ✅ **Validation Strategy** (9/10): Multi-level validation with executable commands and comprehensive test cases
- ✅ **Technical Depth** (8/10): Proper understanding of required libraries and system dependencies
- ⚠️ **Diagram Generation Complexity** (7/10): Layout matching and icon management may require iteration
- ⚠️ **Technology Catalog Scope** (7/10): Vast Microsoft ecosystem - potential for missing components

**Expected Implementation Success**: High confidence for one-pass implementation with possible minor iterations on diagram generation and layout precision.