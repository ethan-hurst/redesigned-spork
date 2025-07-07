"""
Icon management service for Microsoft Dynamics & Power Platform Architecture Builder.

This module handles downloading, caching, and managing Microsoft official icons
for use in architectural diagrams.
"""

import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class IconManagerError(Exception):
    """Custom exception for icon management operations."""

    pass


class IconManager:
    """
    Service class for managing Microsoft icons.

    This class handles downloading official Microsoft icons and managing
    local icon caches for use in diagram generation.
    """

    def __init__(self, icon_base_path: Optional[Path] = None):
        """
        Initialize the icon manager.

        Args:
            icon_base_path: Base path for storing icons (defaults to src/data/icons)
        """
        if icon_base_path is None:
            icon_base_path = Path(__file__).parent.parent / "data" / "icons"

        self.icon_base_path = icon_base_path
        self.microsoft_icons_path = icon_base_path / "microsoft"
        self.power_platform_icons_path = self.microsoft_icons_path / "power_platform"
        self.azure_icons_path = self.microsoft_icons_path / "azure"

        # Ensure directories exist
        self._create_directories()

        # Official Microsoft icon download URLs
        self.icon_sources = {
            "power_platform": "https://download.microsoft.com/download/e/f/4/ef434e60-8cdc-4dd1-9d9f-e58670e57ec1/Power_Platform_scalable.zip",
            # Azure icons need to be downloaded from the architecture center
            # This is a placeholder - actual download requires accepting terms
            "azure": "https://learn.microsoft.com/en-us/azure/architecture/icons/",
        }

    def _create_directories(self) -> None:
        """Create necessary directories for icon storage."""
        self.icon_base_path.mkdir(parents=True, exist_ok=True)
        self.microsoft_icons_path.mkdir(parents=True, exist_ok=True)
        self.power_platform_icons_path.mkdir(parents=True, exist_ok=True)
        self.azure_icons_path.mkdir(parents=True, exist_ok=True)

    def download_power_platform_icons(self) -> bool:
        """
        Download official Power Platform icons from Microsoft.

        Returns:
            True if download was successful, False otherwise
        """
        try:
            url = self.icon_sources["power_platform"]
            logger.info(f"Downloading Power Platform icons from {url}")

            # Download the zip file
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Save and extract the zip file
            zip_path = self.power_platform_icons_path / "power_platform_icons.zip"
            with open(zip_path, "wb") as f:
                f.write(response.content)

            # Extract the zip file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.power_platform_icons_path)

            # Remove the zip file
            zip_path.unlink()

            logger.info("Power Platform icons downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to download Power Platform icons: {e}")
            return False

    def get_component_icon_path(self, component_id: str) -> Optional[Path]:
        """
        Get the local path to an icon for a specific component.

        Args:
            component_id: The ID of the component

        Returns:
            Path to the icon file if it exists, None otherwise
        """
        # Define component ID to icon filename mapping
        icon_mappings = {
            # Power Platform
            "power_apps_canvas": "Power_Apps.svg",
            "power_apps_model_driven": "Power_Apps.svg",
            "power_automate": "Power_Automate.svg",
            "power_bi": "Power_BI.svg",
            "power_pages": "Power_Pages.svg",
            "dataverse": "Dataverse.svg",
            "ai_builder": "AI_Builder.svg",
            "copilot_studio": "Microsoft_Copilot_Studio.svg",
            "power_virtual_agents": "Power_Virtual_Agents.svg",
            "power_fx": "Power_Fx.svg",
            # Azure Services (these would need to be mapped to actual Azure icon names)
            "azure_functions": "azure-functions.svg",
            "azure_logic_apps": "azure-logic-apps.svg",
            "azure_service_bus": "azure-service-bus.svg",
            "azure_event_grid": "azure-event-grid.svg",
            "azure_ad": "azure-active-directory.svg",
            "azure_key_vault": "azure-key-vault.svg",
            "azure_application_insights": "azure-application-insights.svg",
        }

        icon_filename = icon_mappings.get(component_id)
        if not icon_filename:
            return None

        # Check Power Platform icons first
        power_platform_icon = self.power_platform_icons_path / icon_filename
        if power_platform_icon.exists():
            return power_platform_icon

        # Check Azure icons
        azure_icon = self.azure_icons_path / icon_filename
        if azure_icon.exists():
            return azure_icon

        return None

    def get_icon_mappings(self) -> Dict[str, str]:
        """
        Get a dictionary mapping component IDs to their icon file paths.

        Returns:
            Dictionary mapping component IDs to icon file paths
        """
        mappings = {}

        # Define all known component IDs
        component_ids = [
            "power_apps_canvas",
            "power_apps_model_driven",
            "power_automate",
            "power_bi",
            "power_pages",
            "dataverse",
            "ai_builder",
            "copilot_studio",
            "power_virtual_agents",
            "power_fx",
            "azure_functions",
            "azure_logic_apps",
            "azure_service_bus",
            "azure_event_grid",
            "azure_ad",
            "azure_key_vault",
            "azure_application_insights",
        ]

        for component_id in component_ids:
            icon_path = self.get_component_icon_path(component_id)
            if icon_path:
                mappings[component_id] = str(icon_path)

        return mappings

    def cache_icon_from_url(self, url: str, filename: str, category: str = "azure") -> Optional[Path]:
        """
        Download and cache an icon from a URL.

        Args:
            url: URL to download the icon from
            filename: Filename to save the icon as
            category: Category directory (azure, power_platform, etc.)

        Returns:
            Path to the cached icon file if successful, None otherwise
        """
        try:
            if category == "azure":
                target_dir = self.azure_icons_path
            elif category == "power_platform":
                target_dir = self.power_platform_icons_path
            else:
                target_dir = self.microsoft_icons_path / category

            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / filename

            # Skip if file already exists
            if target_path.exists():
                return target_path

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open(target_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Cached icon: {filename}")
            return target_path

        except Exception as e:
            logger.error(f"Failed to cache icon {filename} from {url}: {e}")
            return None

    def is_icons_available(self) -> bool:
        """
        Check if Microsoft icons are available locally.

        Returns:
            True if icons are available, False otherwise
        """
        # Check for key Power Platform icons
        key_icons = ["Power_Apps.svg", "Power_BI.svg", "Dataverse.svg"]
        for icon in key_icons:
            if (self.power_platform_icons_path / icon).exists():
                return True
        return False

    def list_available_icons(self) -> Dict[str, list[Path]]:
        """
        List all available icons by category.

        Returns:
            Dictionary mapping categories to lists of available icon paths
        """
        available = {}

        # Power Platform icons
        if self.power_platform_icons_path.exists():
            available["power_platform"] = [
                p for p in self.power_platform_icons_path.glob("*.svg")
            ]

        # Azure icons
        if self.azure_icons_path.exists():
            available["azure"] = [p for p in self.azure_icons_path.glob("*.svg")]

        return available


# Global icon manager instance
_icon_manager: Optional[IconManager] = None


def get_icon_manager() -> IconManager:
    """
    Get the global icon manager instance.

    Returns:
        Global IconManager instance
    """
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager


def reset_icon_manager() -> None:
    """Reset the global icon manager instance (useful for testing)."""
    global _icon_manager
    _icon_manager = None