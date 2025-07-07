"""
Technology catalog service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides functionality to load, query, and manage the Microsoft technology catalog.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from models.technology import (
    IntegrationPattern,
    LayerType,
    TechnologyCategory,
    TechnologyComponent,
)
from services.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class TechnologyCatalogError(Exception):
    """Custom exception for technology catalog operations."""

    pass


class TechnologyCatalog:
    """
    Service class for managing the Microsoft technology catalog.

    This class handles loading, querying, and validation of technology components
    from the JSON catalog file.
    """

    def __init__(self, catalog_file: Optional[Path] = None):
        """
        Initialize the technology catalog with lazy loading support.

        Args:
            catalog_file: Path to the catalog JSON file. If None, uses default location.
        """
        self._components: Optional[dict[str, TechnologyComponent]] = None
        self._catalog_file = catalog_file or self._get_default_catalog_path()
        self._cache_manager = get_cache_manager()
        self._catalog_loaded = False

    def _get_default_catalog_path(self) -> Path:
        """
        Get the default path to the technology catalog file.

        Returns:
            Path to the default catalog file
        """
        current_dir = Path(__file__).parent
        return current_dir.parent / "data" / "technologies.json"

    def _ensure_catalog_loaded(self) -> None:
        """
        Ensure the catalog is loaded using lazy loading with caching.
        """
        if self._catalog_loaded:
            return
            
        # Try to load from cache first
        cached_catalog = self._cache_manager.get_cached_technology_catalog()
        if cached_catalog:
            try:
                self._parse_catalog_data(cached_catalog)
                self._catalog_loaded = True
                logger.debug("Loaded technology catalog from cache")
                return
            except Exception as e:
                logger.debug(f"Failed to load from cache, loading from file: {e}")

        # Load from file
        self._load_catalog_from_file()

    def _load_catalog_from_file(self) -> None:
        """
        Load the technology catalog from the JSON file.

        Raises:
            TechnologyCatalogError: If the catalog file cannot be loaded or parsed
        """
        try:
            if not self._catalog_file.exists():
                raise TechnologyCatalogError(
                    f"Catalog file not found: {self._catalog_file}"
                )

            with open(self._catalog_file, encoding="utf-8") as f:
                catalog_data = json.load(f)

            self._parse_catalog_data(catalog_data)
            
            # Cache the loaded data
            self._cache_manager.cache_technology_catalog(catalog_data)
            self._catalog_loaded = True

            logger.info(
                f"Loaded {len(self._components)} technology components from catalog"
            )

        except json.JSONDecodeError as e:
            raise TechnologyCatalogError(f"Invalid JSON in catalog file: {e}")
        except Exception as e:
            raise TechnologyCatalogError(f"Failed to load catalog: {e}")

    def _parse_catalog_data(self, catalog_data: dict) -> None:
        """
        Parse the catalog data and create TechnologyComponent objects.

        Args:
            catalog_data: The loaded JSON catalog data

        Raises:
            TechnologyCatalogError: If component data is invalid
        """
        if self._components is None:
            self._components = {}
        else:
            self._components.clear()

        for _category, subcategories in catalog_data.items():
            for _subcategory, components in subcategories.items():
                for component_data in components:
                    try:
                        component = TechnologyComponent(**component_data)
                        self._components[component.id] = component

                    except ValidationError as e:
                        logger.warning(
                            f"Invalid component data for {component_data.get('id', 'unknown')}: {e}"
                        )
                        continue
                    except Exception as e:
                        logger.warning(
                            f"Failed to parse component {component_data.get('id', 'unknown')}: {e}"
                        )
                        continue

    def get_all_components(self) -> list[TechnologyComponent]:
        """
        Get all technology components in the catalog.

        Returns:
            List of all technology components
        """
        self._ensure_catalog_loaded()
        return list(self._components.values())

    def get_component_by_id(self, component_id: str) -> Optional[TechnologyComponent]:
        """
        Get a specific component by its ID.

        Args:
            component_id: The ID of the component to retrieve

        Returns:
            The component if found, None otherwise
        """
        self._ensure_catalog_loaded()
        return self._components.get(component_id)

    def get_component_ids(self) -> set[str]:
        """
        Get all component IDs in the catalog.

        Returns:
            Set of all component IDs
        """
        self._ensure_catalog_loaded()
        return set(self._components.keys())

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
        self._ensure_catalog_loaded()
        return [comp for comp in self._components.values() if comp.category == category]

    def get_components_by_subcategory(
        self, category: TechnologyCategory, subcategory: str
    ) -> list[TechnologyComponent]:
        """
        Get all components in a specific subcategory.

        Args:
            category: The main category
            subcategory: The subcategory to filter by

        Returns:
            List of components in the specified subcategory
        """
        self._ensure_catalog_loaded()
        return [
            comp
            for comp in self._components.values()
            if comp.category == category and comp.subcategory == subcategory
        ]

    def get_components_by_layer(self, layer: LayerType) -> list[TechnologyComponent]:
        """
        Get all components in a specific architectural layer.

        Args:
            layer: The layer to filter by

        Returns:
            List of components in the specified layer
        """
        self._ensure_catalog_loaded()
        return [comp for comp in self._components.values() if comp.layer == layer]

    def get_core_components(self) -> list[TechnologyComponent]:
        """
        Get all core/foundational components.

        Returns:
            List of core components
        """
        self._ensure_catalog_loaded()
        return [comp for comp in self._components.values() if comp.is_core]

    def search_components(self, query: str) -> list[TechnologyComponent]:
        """
        Search for components by name or description.

        Args:
            query: The search query

        Returns:
            List of components matching the search query
        """
        self._ensure_catalog_loaded()
        query_lower = query.lower()
        results = []

        for component in self._components.values():
            if (
                query_lower in component.name.lower()
                or query_lower in component.description.lower()
                or query_lower in component.id.lower()
            ):
                results.append(component)

        return results

    def get_components_with_integration_pattern(
        self, pattern: IntegrationPattern
    ) -> list[TechnologyComponent]:
        """
        Get all components that support a specific integration pattern.

        Args:
            pattern: The integration pattern to filter by

        Returns:
            List of components supporting the specified pattern
        """
        self._ensure_catalog_loaded()
        return [
            comp
            for comp in self._components.values()
            if pattern in comp.integration_patterns
        ]

    def validate_dependencies(self, component_ids: list[str]) -> list[str]:
        """
        Validate that all dependencies for the given components are satisfied.

        Args:
            component_ids: List of component IDs to validate

        Returns:
            List of missing dependency error messages
        """
        errors = []
        selected_ids = set(component_ids)

        for component_id in component_ids:
            component = self.get_component_by_id(component_id)
            if not component:
                errors.append(f"Component not found: {component_id}")
                continue

            for dependency in component.dependencies:
                if dependency not in selected_ids:
                    dep_component = self.get_component_by_id(dependency)
                    dep_name = dep_component.name if dep_component else dependency
                    errors.append(f"{component.name} requires {dep_name}")

        return errors

    def validate_conflicts(self, component_ids: list[str]) -> list[str]:
        """
        Validate that there are no conflicts between the selected components.

        Args:
            component_ids: List of component IDs to validate

        Returns:
            List of conflict error messages
        """
        errors = []
        selected_ids = set(component_ids)

        for component_id in component_ids:
            component = self.get_component_by_id(component_id)
            if not component:
                continue

            for conflict in component.conflicts:
                if conflict in selected_ids:
                    conflict_component = self.get_component_by_id(conflict)
                    conflict_name = (
                        conflict_component.name if conflict_component else conflict
                    )
                    errors.append(f"{component.name} conflicts with {conflict_name}")

        return errors

    def suggest_additional_components(
        self, selected_ids: list[str]
    ) -> list[TechnologyComponent]:
        """
        Suggest additional components based on the current selection.

        Args:
            selected_ids: List of currently selected component IDs

        Returns:
            List of suggested components
        """
        suggestions = []
        selected_set = set(selected_ids)

        # Get all selected components
        selected_components = [
            self.get_component_by_id(comp_id)
            for comp_id in selected_ids
            if self.get_component_by_id(comp_id)
        ]

        # Check for missing dependencies
        for component in selected_components:
            for dependency in component.dependencies:
                if dependency not in selected_set:
                    dep_component = self.get_component_by_id(dependency)
                    if dep_component and dep_component not in suggestions:
                        suggestions.append(dep_component)

        # Suggest commonly used components based on patterns
        has_power_apps = any("power_apps" in comp_id for comp_id in selected_ids)
        has_dataverse = any("dataverse" in comp_id for comp_id in selected_ids)
        has_security = any(
            self.get_component_by_id(comp_id).layer == LayerType.SECURITY
            for comp_id in selected_ids
            if self.get_component_by_id(comp_id)
        )

        # If Power Apps is selected but Dataverse isn't, suggest it
        if has_power_apps and not has_dataverse:
            dataverse = self.get_component_by_id("dataverse")
            if dataverse and dataverse not in suggestions:
                suggestions.append(dataverse)

        # If no security components, suggest Azure AD
        if not has_security:
            azure_ad = self.get_component_by_id("azure_ad")
            if azure_ad and azure_ad not in suggestions:
                suggestions.append(azure_ad)

        return suggestions

    def get_catalog_statistics(self) -> dict[str, int]:
        """
        Get statistics about the technology catalog.

        Returns:
            Dictionary with catalog statistics
        """
        self._ensure_catalog_loaded()
        stats = {
            "total_components": len(self._components),
            "core_components": len(self.get_core_components()),
        }

        # Count by category
        for category in TechnologyCategory:
            stats[f"{category.value}_components"] = len(
                self.get_components_by_category(category)
            )

        # Count by layer
        for layer in LayerType:
            stats[f"{layer.value}_layer_components"] = len(
                self.get_components_by_layer(layer)
            )

        return stats

    def reload_catalog(self) -> None:
        """
        Reload the catalog from the file.

        This method can be used to refresh the catalog if the file has been updated.
        """
        self._catalog_loaded = False
        self._cache_manager.clear_cache("metadata")  # Clear cached catalog
        self._ensure_catalog_loaded()

    def export_components_to_dict(self, component_ids: list[str]) -> dict:
        """
        Export selected components to a dictionary format.

        Args:
            component_ids: List of component IDs to export

        Returns:
            Dictionary representation of the selected components
        """
        export_data = {}

        for component_id in component_ids:
            component = self.get_component_by_id(component_id)
            if component:
                category = component.category.value
                subcategory = component.subcategory

                if category not in export_data:
                    export_data[category] = {}
                if subcategory not in export_data[category]:
                    export_data[category][subcategory] = []

                export_data[category][subcategory].append(component.model_dump())

        return export_data


# Global catalog instance
_catalog_instance: Optional[TechnologyCatalog] = None


def get_catalog() -> TechnologyCatalog:
    """
    Get the global technology catalog instance.

    Returns:
        The global TechnologyCatalog instance
    """
    global _catalog_instance
    if _catalog_instance is None:
        _catalog_instance = TechnologyCatalog()
    return _catalog_instance


def reset_catalog() -> None:
    """Reset the global catalog instance (mainly for testing)."""
    global _catalog_instance
    _catalog_instance = None
