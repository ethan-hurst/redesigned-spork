"""
Architecture generator service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides functionality for generating complete architecture models from technology stacks.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..models.architecture import Architecture, DiagramLayout
from ..models.technology import LayerType, TechnologyStack
from .selection_service import SelectionService
from .technology_catalog import TechnologyCatalog, get_catalog

logger = logging.getLogger(__name__)


class ArchitectureGeneratorError(Exception):
    """Custom exception for architecture generation operations."""
    pass


class ArchitectureGenerator:
    """
    Service class for generating complete architecture models.
    
    This class handles the conversion of technology stacks into complete
    architectural models with proper organization and validation.
    """

    def __init__(self, catalog: Optional[TechnologyCatalog] = None):
        """
        Initialize the architecture generator.
        
        Args:
            catalog: Technology catalog to use. If None, uses the global catalog.
        """
        self.catalog = catalog or get_catalog()
        self.selection_service = SelectionService(self.catalog)

    def generate_architecture(
        self,
        technology_stack: TechnologyStack,
        layout: DiagramLayout = DiagramLayout.LAYERED
    ) -> Architecture:
        """
        Generate a complete architecture from a technology stack.
        
        Args:
            technology_stack: The technology stack to generate architecture for
            layout: The diagram layout style to use
            
        Returns:
            Complete architecture model
            
        Raises:
            ArchitectureGeneratorError: If architecture generation fails
        """
        try:
            # Validate the technology stack
            self.selection_service.load_stack(technology_stack)
            is_valid, errors = self.selection_service.validate_current_stack()

            if not is_valid:
                logger.warning(f"Generating architecture with validation errors: {errors}")

            # Create the architecture
            architecture = Architecture(
                name=technology_stack.name,
                description=technology_stack.description,
                technology_stack=technology_stack,
                layout=layout
            )

            # Generate missing integration flows if needed
            suggested_flows = technology_stack.get_suggested_integrations()
            for flow in suggested_flows:
                if not any(f.id == flow.id for f in technology_stack.integration_flows):
                    technology_stack.integration_flows.append(flow)
                    logger.info(f"Added suggested integration flow: {flow.name}")

            # Validate the final architecture
            arch_errors = architecture.validate_architecture()
            if arch_errors:
                logger.warning(f"Architecture validation warnings: {arch_errors}")

            logger.info(f"Generated architecture '{architecture.name}' with {len(technology_stack.components)} components")
            return architecture

        except Exception as e:
            raise ArchitectureGeneratorError(f"Failed to generate architecture: {e}")

    def enhance_architecture_with_best_practices(self, architecture: Architecture) -> List[str]:
        """
        Enhance an architecture by suggesting best practices and missing components.
        
        Args:
            architecture: The architecture to enhance
            
        Returns:
            List of enhancement suggestions
        """
        suggestions = []
        components = architecture.technology_stack.components
        component_ids = {c.id for c in components}

        # Check for security layer presence
        has_security = any(c.layer == LayerType.SECURITY for c in components)
        if not has_security:
            suggestions.append("Consider adding Azure Active Directory for identity management")

        # Check for monitoring components
        has_monitoring = any('monitor' in c.id or 'insights' in c.id for c in components)
        if not has_monitoring:
            suggestions.append("Consider adding Azure Application Insights for monitoring")

        # Check for data layer
        has_data_layer = any(c.layer == LayerType.DATA for c in components)
        if not has_data_layer:
            suggestions.append("Consider adding a data storage component like Dataverse")

        # Power Platform specific recommendations
        has_power_apps = any('power_apps' in c.id for c in components)
        has_power_automate = any('power_automate' in c.id for c in components)
        has_dataverse = 'dataverse' in component_ids

        if has_power_apps and not has_dataverse:
            suggestions.append("Power Apps works best with Dataverse for data storage")

        if has_power_apps and not has_power_automate:
            suggestions.append("Consider Power Automate for workflow automation with Power Apps")

        # Dynamics 365 specific recommendations
        dynamics_components = [c for c in components if c.category.value == 'dynamics_365']
        if dynamics_components and not has_dataverse:
            suggestions.append("Dynamics 365 applications require Dataverse for data storage")

        # Integration layer recommendations
        has_integration = any(c.layer == LayerType.INTEGRATION for c in components)
        if len(components) > 3 and not has_integration:
            suggestions.append("Consider adding integration services like Azure Logic Apps or Power Automate")

        return suggestions

    def optimize_component_placement(self, architecture: Architecture) -> Architecture:
        """
        Optimize the placement of components in architectural layers.
        
        Args:
            architecture: The architecture to optimize
            
        Returns:
            Optimized architecture
        """
        # This method could implement logic to automatically reorganize components
        # based on best practices, but for now we'll just validate current placement

        layer_organization = {}

        for component in architecture.technology_stack.components:
            layer = component.layer
            if layer not in layer_organization:
                layer_organization[layer] = []
            layer_organization[layer].append(component.id)

        architecture.layer_organization = layer_organization
        architecture.updated_at = datetime.now()

        return architecture

    def generate_layer_recommendations(self, architecture: Architecture) -> Dict[LayerType, List[str]]:
        """
        Generate recommendations for each architectural layer.
        
        Args:
            architecture: The architecture to analyze
            
        Returns:
            Dictionary mapping layers to recommendation lists
        """
        recommendations = {}
        layer_matrix = architecture.generate_layer_matrix()

        for layer, components in layer_matrix.items():
            layer_recommendations = []

            if layer == LayerType.PRESENTATION:
                if not components:
                    layer_recommendations.append("Add user interface components like Power Apps or Power Pages")
                elif len(components) == 1:
                    layer_recommendations.append("Consider multiple channels for better user experience")

            elif layer == LayerType.APPLICATION:
                if not components:
                    layer_recommendations.append("Add business logic components like Dynamics 365 applications")
                else:
                    # Check for AI/Copilot components
                    has_ai = any('copilot' in c.name.lower() or 'ai' in c.name.lower() for c in components)
                    if not has_ai:
                        layer_recommendations.append("Consider adding AI Builder or Copilot Studio for intelligent features")

            elif layer == LayerType.INTEGRATION:
                if len(architecture.technology_stack.components) > 2 and not components:
                    layer_recommendations.append("Add integration services like Power Automate or Azure Logic Apps")
                elif components:
                    # Check for API management
                    has_api_mgmt = any('api' in c.name.lower() for c in components)
                    if len(components) > 2 and not has_api_mgmt:
                        layer_recommendations.append("Consider Azure API Management for enterprise scenarios")

            elif layer == LayerType.DATA:
                if not components:
                    layer_recommendations.append("Add data storage components like Dataverse or Azure Data Lake")
                else:
                    # Check for analytics
                    has_analytics = any('synapse' in c.id or 'power_bi' in c.id for c in components)
                    if not has_analytics and len(components) > 1:
                        layer_recommendations.append("Consider Power BI or Azure Synapse for analytics")

            elif layer == LayerType.SECURITY:
                if not components:
                    layer_recommendations.append("Add security components like Azure AD and Key Vault")
                else:
                    # Check for monitoring
                    has_monitoring = any('monitor' in c.id or 'insights' in c.id for c in components)
                    if not has_monitoring:
                        layer_recommendations.append("Consider Azure Monitor for operational insights")

            recommendations[layer] = layer_recommendations

        return recommendations

    def calculate_architecture_score(self, architecture: Architecture) -> Dict[str, int]:
        """
        Calculate a comprehensive score for the architecture.
        
        Args:
            architecture: The architecture to score
            
        Returns:
            Dictionary with various score metrics
        """
        scores = {}
        components = architecture.technology_stack.components
        flows = architecture.technology_stack.integration_flows

        # Completeness score (0-10)
        layer_coverage = len(architecture.layer_organization)
        max_layers = len(LayerType)
        scores['completeness'] = min(10, int((layer_coverage / max_layers) * 10))

        # Integration score (0-10)
        if len(components) <= 1:
            scores['integration'] = 10
        else:
            expected_flows = len(components) - 1  # Minimum for connectivity
            actual_flows = len(flows)
            scores['integration'] = min(10, int((actual_flows / expected_flows) * 10))

        # Security score (0-10)
        has_security = any(c.layer == LayerType.SECURITY for c in components)
        has_identity = any('azure_ad' in c.id for c in components)
        security_score = 0
        if has_security:
            security_score += 5
        if has_identity:
            security_score += 5
        scores['security'] = security_score

        # Best practices score (0-10)
        suggestions = self.enhance_architecture_with_best_practices(architecture)
        max_suggestions = 10  # Arbitrary baseline
        practices_score = max(0, 10 - len(suggestions))
        scores['best_practices'] = practices_score

        # Overall score
        scores['overall'] = int(sum(scores.values()) / len(scores))

        return scores

    def generate_architecture_report(self, architecture: Architecture) -> Dict:
        """
        Generate a comprehensive report for an architecture.
        
        Args:
            architecture: The architecture to report on
            
        Returns:
            Dictionary with comprehensive architecture analysis
        """
        report = {
            'name': architecture.name,
            'description': architecture.description,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'component_count': len(architecture.technology_stack.components),
                'integration_count': len(architecture.technology_stack.integration_flows),
                'layer_count': len(architecture.layer_organization),
                'complexity_score': architecture.get_integration_complexity_score()
            },
            'layer_analysis': {},
            'recommendations': {},
            'scores': {},
            'validation': {
                'is_valid': True,
                'errors': []
            }
        }

        # Layer analysis
        layer_matrix = architecture.generate_layer_matrix()
        for layer, components in layer_matrix.items():
            report['layer_analysis'][layer.value] = {
                'component_count': len(components),
                'components': [c.name for c in components]
            }

        # Recommendations
        report['recommendations']['enhancements'] = self.enhance_architecture_with_best_practices(architecture)
        report['recommendations']['by_layer'] = {
            layer.value: recs for layer, recs in self.generate_layer_recommendations(architecture).items()
        }

        # Scoring
        report['scores'] = self.calculate_architecture_score(architecture)

        # Validation
        validation_errors = architecture.validate_architecture()
        report['validation']['is_valid'] = len(validation_errors) == 0
        report['validation']['errors'] = validation_errors

        return report
