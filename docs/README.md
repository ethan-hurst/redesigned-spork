# Microsoft Dynamics & Power Platform Architecture Builder

A comprehensive CLI tool for generating professional architectural diagrams of Microsoft technology stacks, including Dynamics 365, Power Platform, Azure services, and security components.

## Overview

The Microsoft Dynamics & Power Platform Architecture Builder helps organizations visualize their technology architecture by:

- **Interactive Component Selection**: Choose from 40+ Microsoft technologies across Power Platform, Dynamics 365, Azure services, and security components
- **Automatic Dependency Resolution**: Identifies and suggests missing dependencies between components
- **Professional Diagram Generation**: Creates publication-quality architectural diagrams following Microsoft best practices
- **Multiple Export Formats**: Supports PNG, SVG, PDF, and JPG output formats
- **Validation & Best Practices**: Validates architecture completeness and suggests improvements

## Features

### Technology Catalog
- **Power Platform**: Power Apps, Power Automate, Power BI, Power Pages, Copilot Studio, Dataverse, AI Builder
- **Dynamics 365**: Sales, Marketing, Customer Service, Field Service, Business Central, Finance & Operations
- **Azure Services**: Logic Apps, Functions, Service Bus, Event Grid, Data Factory, API Management
- **Security & Operations**: Azure AD, Key Vault, Defender, Application Insights, Monitor, Log Analytics

### Architectural Layers
Components are automatically organized into architectural layers:
- **Presentation Layer**: User interfaces and interaction points
- **Application Layer**: Business logic and applications
- **Integration Layer**: Middleware and integration services
- **Data Layer**: Data storage and management
- **Security Layer**: Security and operational components

### Interactive Features
- **Guided Selection**: Category-based component browsing
- **Dependency Management**: Automatic detection and resolution
- **Conflict Detection**: Identifies incompatible component combinations
- **Integration Suggestions**: Recommends integration flows between components
- **Architecture Validation**: Ensures completeness and best practices

## Installation

### Prerequisites
- Python 3.9 or higher
- Graphviz (for diagram generation)

### Install Graphviz

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Windows:**
Download from https://graphviz.org/download/ or use chocolatey:
```bash
choco install graphviz
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Interactive Mode (Recommended)
Launch the interactive wizard:
```bash
python -m src.main interactive
```

This guided experience will:
1. Prompt for architecture name and description
2. Let you select technology categories
3. Choose specific components within each category
4. Automatically resolve dependencies
5. Suggest integration flows
6. Generate and export your diagram

### 2. Command Line Mode
Generate diagrams directly from the command line:

```bash
# Basic Power Platform stack
python -m src.main generate \
  --components "power_apps_canvas,dataverse,power_automate,power_bi" \
  --output "power_platform_arch.png" \
  --name "Power Platform Architecture"

# Enterprise integration scenario
python -m src.main generate \
  --components "dynamics_365_sales,dataverse,power_automate,azure_logic_apps,azure_ad" \
  --output "enterprise_arch.png" \
  --format "svg" \
  --name "Enterprise Sales Architecture"
```

### 3. Explore Available Components
```bash
# List all components
python -m src.main list-components

# Filter by category
python -m src.main list-components --category power_platform

# Search for specific components
python -m src.main list-components --search "dynamics 365"
```

## Usage Examples

### Example 1: Simple Power Platform Stack
**Components**: Power Apps, Dataverse, Power Automate, Power BI
**Use Case**: Basic low-code application with data visualization

```bash
python -m src.main generate \
  -c "power_apps_canvas,dataverse,power_automate,power_bi" \
  -o "simple_stack.png" \
  -n "Simple Power Platform Stack"
```

### Example 2: Customer Service Solution
**Components**: Dynamics 365 Customer Service, Teams integration, Power Automate
**Use Case**: Omnichannel customer service with automation

```bash
python -m src.main generate \
  -c "dynamics_365_customer_service,dataverse,power_automate,teams_channel,azure_ad" \
  -o "customer_service.png" \
  -n "Customer Service Architecture"
```

### Example 3: Enterprise Integration
**Components**: Multiple Azure services with Power Platform
**Use Case**: Large-scale integration scenario

```bash
python -m src.main generate \
  -c "power_automate,azure_logic_apps,azure_service_bus,azure_functions,dataverse,azure_ad,azure_key_vault" \
  -o "enterprise_integration.png" \
  -f "pdf" \
  -n "Enterprise Integration Architecture"
```

## Command Reference

### Main Commands

#### `interactive`
Launch interactive mode for guided architecture building.

#### `generate`
Generate diagram from specified components.
- `--components, -c`: Comma-separated component IDs (required)
- `--output, -o`: Output file path (required)
- `--format, -f`: Output format (png, svg, pdf, jpg) [default: png]
- `--name, -n`: Architecture name [default: Generated Architecture]
- `--description, -d`: Architecture description

#### `list-components`
List available technology components.
- `--category, -c`: Filter by category
- `--search, -s`: Search by name or description

#### `stats`
Show technology catalog statistics.

#### `validate`
Validate system requirements and dependencies.

#### `examples`
Show usage examples and sample configurations.
- `--all`: Show all available examples

## Architecture Patterns

The tool follows Microsoft architectural best practices and patterns:

### Layered Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ Presentation Layer                                          │
│ Power Apps, Power Pages, Teams, Outlook Add-ins            │
├─────────────────────────────────────────────────────────────┤
│ Application Layer                                           │
│ Dynamics 365 Apps, Copilot Studio, AI Builder             │
├─────────────────────────────────────────────────────────────┤
│ Integration Layer                                           │
│ Power Automate, Logic Apps, Service Bus, Functions         │
├─────────────────────────────────────────────────────────────┤
│ Data Layer                                                  │
│ Dataverse, Data Lake, Synapse, Power BI                   │
├─────────────────────────────────────────────────────────────┤
│ Security & Operations Layer                                 │
│ Azure AD, Key Vault, Defender, Monitor, Insights          │
└─────────────────────────────────────────────────────────────┘
```

### Integration Patterns
- **Dataverse Connector**: Native Power Platform integration
- **REST API**: Standard HTTP-based integration
- **OData**: Open data protocol for data services
- **Service Bus**: Reliable messaging for enterprise scenarios
- **Event Grid**: Event-driven reactive programming
- **Logic Apps**: Advanced workflow orchestration

## Configuration

### Output Formats
- **PNG**: Raster format, good for web and presentations
- **SVG**: Vector format, scalable and editable
- **PDF**: Print-ready format with high quality
- **JPG**: Compressed raster format

### Diagram Customization
The tool automatically:
- Organizes components by architectural layer
- Uses Microsoft brand colors and styling
- Shows integration flows between components
- Includes component descriptions when requested
- Follows Microsoft architectural diagram conventions

## Troubleshooting

### Common Issues

#### Graphviz Not Found
```
Error: Graphviz not installed
```
**Solution**: Install Graphviz using your system package manager.

#### Component Not Found
```
Error: Component not found: invalid_component
```
**Solution**: Use `list-components` to see available component IDs.

#### Dependency Errors
```
Warning: Component X requires Y which is not selected
```
**Solution**: Add the missing dependency or use interactive mode for automatic resolution.

#### Permission Errors
```
Error: Permission denied: cannot create directory
```
**Solution**: Ensure you have write permissions to the output directory.

### Validation Commands
```bash
# Check system requirements
python -m src.main validate

# Run tests
python -m pytest tests/ -v

# Check code quality
ruff check src/
mypy src/
```

## Architecture Components Reference

### Power Platform Core
| Component | ID | Description | Layer |
|-----------|----|-----------| ------|
| Power Apps (Canvas) | `power_apps_canvas` | Custom UI development | Presentation |
| Power Apps (Model-driven) | `power_apps_model_driven` | Data-driven applications | Presentation |
| Power Automate | `power_automate` | Workflow automation | Integration |
| Power BI | `power_bi` | Business intelligence | Presentation |
| Power Pages | `power_pages` | External websites | Presentation |
| Copilot Studio | `copilot_studio` | AI chatbots | Application |
| Dataverse | `dataverse` | Data platform | Data |
| AI Builder | `ai_builder` | AI capabilities | Application |

### Dynamics 365 Applications
| Component | ID | Description | Layer |
|-----------|----|-----------| ------|
| Dynamics 365 Sales | `dynamics_365_sales` | Sales management | Application |
| Dynamics 365 Marketing | `dynamics_365_marketing` | Marketing automation | Application |
| Dynamics 365 Customer Service | `dynamics_365_customer_service` | Customer support | Application |
| Dynamics 365 Field Service | `dynamics_365_field_service` | Field operations | Application |
| Dynamics 365 Business Central | `dynamics_365_business_central` | ERP for SMB | Application |
| Dynamics 365 Finance & Operations | `dynamics_365_finance_operations` | Enterprise ERP | Application |

### Azure Services
| Component | ID | Description | Layer |
|-----------|----|-----------| ------|
| Azure Logic Apps | `azure_logic_apps` | Enterprise workflows | Integration |
| Azure Functions | `azure_functions` | Serverless compute | Integration |
| Azure Service Bus | `azure_service_bus` | Messaging service | Integration |
| Azure Event Grid | `azure_event_grid` | Event routing | Integration |
| Azure Data Factory | `azure_data_factory` | Data integration | Integration |
| Azure API Management | `azure_api_management` | API gateway | Integration |
| Azure Data Lake Gen2 | `azure_data_lake_gen2` | Data lake storage | Data |
| Azure Synapse Analytics | `azure_synapse_analytics` | Analytics platform | Data |

### Security & Operations
| Component | ID | Description | Layer |
|-----------|----|-----------| ------|
| Azure Active Directory | `azure_ad` | Identity management | Security |
| Azure Key Vault | `azure_key_vault` | Secrets management | Security |
| Microsoft Defender | `microsoft_defender` | Security protection | Security |
| Azure Application Insights | `azure_application_insights` | Application monitoring | Security |
| Azure Monitor | `azure_monitor` | Resource monitoring | Security |
| Azure Log Analytics | `azure_log_analytics` | Log analysis | Security |

## Best Practices

### Component Selection
1. **Start with Core Components**: Begin with foundational elements like Dataverse or Azure AD
2. **Consider Dependencies**: The tool will suggest missing dependencies
3. **Think in Layers**: Ensure representation across architectural layers
4. **Security First**: Always include identity and security components

### Architecture Design
1. **Follow Microsoft Patterns**: Use established architectural patterns
2. **Minimize Complexity**: Start simple and add complexity as needed
3. **Document Integration Flows**: Clearly show how components interact
4. **Validate Regularly**: Use the built-in validation features

### Diagram Generation
1. **Choose Appropriate Format**: SVG for editing, PNG for sharing, PDF for printing
2. **Include Descriptions**: Add component descriptions for stakeholder clarity
3. **Use Consistent Naming**: Follow organizational naming conventions
4. **Version Control**: Save diagram configurations for future updates

## Contributing

This tool is part of a context engineering approach for AI-assisted development. The architecture and patterns are designed to be extensible and maintainable.

### Adding New Components
1. Update `src/data/technologies.json` with new component definitions
2. Ensure proper categorization and layer assignment
3. Define dependencies and integration patterns
4. Add appropriate tests

### Extending Functionality
1. Follow the existing service architecture patterns
2. Use Pydantic for data validation
3. Add comprehensive tests for new features
4. Update documentation and examples

## License

MIT License - see LICENSE file for details.