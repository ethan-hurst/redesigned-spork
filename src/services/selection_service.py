"""
Selection service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides functionality for managing user technology selections and validation.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..models.technology import IntegrationFlow, TechnologyComponent, TechnologyStack
from .technology_catalog import TechnologyCatalog, get_catalog

logger = logging.getLogger(__name__)


class SelectionError(Exception):
    """Custom exception for selection operations."""
    pass


class SelectionService:
    """
    Service class for managing technology component selections.
    
    This class handles the logic for selecting, validating, and organizing
    technology components into a coherent stack.
    """

    def __init__(self, catalog: Optional[TechnologyCatalog] = None):
        """
        Initialize the selection service.
        
        Args:
            catalog: Technology catalog to use. If None, uses the global catalog.
        """
        self.catalog = catalog or get_catalog()
        self.current_stack: Optional[TechnologyStack] = None

    def create_new_stack(self, name: str, description: str = "") -> TechnologyStack:
        """
        Create a new technology stack.
        
        Args:
            name: Name for the new stack
            description: Optional description
            
        Returns:
            The newly created technology stack
        """
        self.current_stack = TechnologyStack(
            name=name,
            description=description,
            components=[],
            integration_flows=[]
        )

        logger.info(f"Created new technology stack: {name}")
        return self.current_stack

    def load_stack(self, stack: TechnologyStack) -> None:
        """
        Load an existing technology stack.
        
        Args:
            stack: The technology stack to load
        """
        self.current_stack = stack
        logger.info(f"Loaded technology stack: {stack.name}")

    def add_component(self, component_id: str) -> Tuple[bool, str]:
        """
        Add a component to the current stack.
        
        Args:
            component_id: ID of the component to add
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_stack:
            return False, "No active technology stack. Create one first."

        component = self.catalog.get_component_by_id(component_id)
        if not component:
            return False, f"Component not found: {component_id}"

        try:
            success = self.current_stack.add_component(component)
            if success:
                logger.info(f"Added component {component.name} to stack {self.current_stack.name}")
                return True, f"Added {component.name}"
            else:
                return False, f"{component.name} is already in the stack"

        except ValueError as e:
            return False, str(e)

    def remove_component(self, component_id: str) -> Tuple[bool, str]:
        """
        Remove a component from the current stack.
        
        Args:
            component_id: ID of the component to remove
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_stack:
            return False, "No active technology stack."

        component = self.catalog.get_component_by_id(component_id)
        if not component:
            return False, f"Component not found: {component_id}"

        success = self.current_stack.remove_component(component_id)
        if success:
            logger.info(f"Removed component {component.name} from stack {self.current_stack.name}")
            return True, f"Removed {component.name}"
        else:
            return False, f"{component.name} was not in the stack"

    def add_multiple_components(self, component_ids: List[str]) -> Tuple[List[str], List[str]]:
        """
        Add multiple components to the current stack.
        
        Args:
            component_ids: List of component IDs to add
            
        Returns:
            Tuple of (successfully_added, failed_to_add)
        """
        successful = []
        failed = []

        for component_id in component_ids:
            success, message = self.add_component(component_id)
            if success:
                successful.append(component_id)
            else:
                failed.append(f"{component_id}: {message}")

        return successful, failed

    def validate_current_stack(self) -> Tuple[bool, List[str]]:
        """
        Validate the current technology stack.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not self.current_stack:
            return False, ["No active technology stack"]

        errors = []

        # Check dependencies
        dependency_errors = self.current_stack.validate_dependencies()
        errors.extend(dependency_errors)

        # Check conflicts using catalog
        component_ids = [c.id for c in self.current_stack.components]
        conflict_errors = self.catalog.validate_conflicts(component_ids)
        errors.extend(conflict_errors)

        return len(errors) == 0, errors

    def get_missing_dependencies(self) -> List[TechnologyComponent]:
        """
        Get components that are dependencies but not currently selected.
        
        Returns:
            List of missing dependency components
        """
        if not self.current_stack:
            return []

        selected_ids = {c.id for c in self.current_stack.components}
        missing_deps = []

        for component in self.current_stack.components:
            for dep_id in component.dependencies:
                if dep_id not in selected_ids:
                    dep_component = self.catalog.get_component_by_id(dep_id)
                    if dep_component and dep_component not in missing_deps:
                        missing_deps.append(dep_component)

        return missing_deps

    def get_suggestions(self) -> List[TechnologyComponent]:
        """
        Get suggested components based on current selections.
        
        Returns:
            List of suggested components
        """
        if not self.current_stack:
            return []

        selected_ids = [c.id for c in self.current_stack.components]
        return self.catalog.suggest_additional_components(selected_ids)

    def auto_resolve_dependencies(self) -> Tuple[int, List[str]]:
        """
        Automatically add missing dependencies to the stack.
        
        Returns:
            Tuple of (number_added, error_messages)
        """
        if not self.current_stack:
            return 0, ["No active technology stack"]

        missing_deps = self.get_missing_dependencies()
        added_count = 0
        errors = []

        for dep_component in missing_deps:
            success, message = self.add_component(dep_component.id)
            if success:
                added_count += 1
            else:
                errors.append(message)

        logger.info(f"Auto-resolved {added_count} dependencies")
        return added_count, errors

    def generate_integration_flows(self) -> List[IntegrationFlow]:
        """
        Generate suggested integration flows for the current stack.
        
        Returns:
            List of suggested integration flows
        """
        if not self.current_stack:
            return []

        return self.current_stack.get_suggested_integrations()

    def add_integration_flow(self, flow: IntegrationFlow) -> Tuple[bool, str]:
        """
        Add an integration flow to the current stack.
        
        Args:
            flow: The integration flow to add
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_stack:
            return False, "No active technology stack"

        # Validate that source and target components exist in the stack
        source_component = self.current_stack.get_component_by_id(flow.source_component_id)
        target_component = self.current_stack.get_component_by_id(flow.target_component_id)

        if not source_component:
            return False, f"Source component {flow.source_component_id} not in stack"

        if not target_component:
            return False, f"Target component {flow.target_component_id} not in stack"

        # Check if flow already exists
        existing_flow = next(
            (f for f in self.current_stack.integration_flows if f.id == flow.id),
            None
        )

        if existing_flow:
            return False, f"Integration flow {flow.id} already exists"

        self.current_stack.integration_flows.append(flow)
        logger.info(f"Added integration flow: {flow.name}")
        return True, f"Added integration flow: {flow.name}"

    def remove_integration_flow(self, flow_id: str) -> Tuple[bool, str]:
        """
        Remove an integration flow from the current stack.
        
        Args:
            flow_id: ID of the flow to remove
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_stack:
            return False, "No active technology stack"

        original_count = len(self.current_stack.integration_flows)
        self.current_stack.integration_flows = [
            f for f in self.current_stack.integration_flows if f.id != flow_id
        ]

        if len(self.current_stack.integration_flows) < original_count:
            logger.info(f"Removed integration flow: {flow_id}")
            return True, f"Removed integration flow: {flow_id}"
        else:
            return False, f"Integration flow not found: {flow_id}"

    def get_stack_summary(self) -> Dict:
        """
        Get a summary of the current technology stack.
        
        Returns:
            Dictionary with stack summary information
        """
        if not self.current_stack:
            return {"error": "No active technology stack"}

        summary = {
            "name": self.current_stack.name,
            "description": self.current_stack.description,
            "component_count": len(self.current_stack.components),
            "integration_flow_count": len(self.current_stack.integration_flows),
            "categories": {},
            "layers": {},
            "is_valid": False,
            "missing_dependencies": 0,
            "suggestions_available": 0
        }

        # Count by category
        for component in self.current_stack.components:
            category = component.category.value
            summary["categories"][category] = summary["categories"].get(category, 0) + 1

        # Count by layer
        for component in self.current_stack.components:
            layer = component.layer.value
            summary["layers"][layer] = summary["layers"].get(layer, 0) + 1

        # Validation status
        is_valid, _ = self.validate_current_stack()
        summary["is_valid"] = is_valid

        # Missing dependencies
        missing_deps = self.get_missing_dependencies()
        summary["missing_dependencies"] = len(missing_deps)

        # Available suggestions
        suggestions = self.get_suggestions()
        summary["suggestions_available"] = len(suggestions)

        return summary

    def export_stack_configuration(self) -> Optional[Dict]:
        """
        Export the current stack configuration as a dictionary.
        
        Returns:
            Dictionary representation of the stack, or None if no stack
        """
        if not self.current_stack:
            return None

        return {
            "name": self.current_stack.name,
            "description": self.current_stack.description,
            "components": [c.model_dump() for c in self.current_stack.components],
            "integration_flows": [f.model_dump() for f in self.current_stack.integration_flows],
            "exported_at": datetime.now().isoformat()
        }

    def clear_current_stack(self) -> None:
        """Clear the current technology stack."""
        if self.current_stack:
            logger.info(f"Cleared technology stack: {self.current_stack.name}")
        self.current_stack = None
