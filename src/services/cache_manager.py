"""
Cache manager service for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides caching functionality for icons, diagrams, and other resources
to improve performance and reduce redundant operations.
"""

import hashlib
import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta

from models.architecture import Architecture, DiagramConfig

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Service class for managing various types of caches.
    
    Handles caching for:
    - Generated diagrams
    - Icon data
    - Technology catalog data
    - Architecture configurations
    """

    def __init__(self, cache_base_path: Optional[Path] = None):
        """
        Initialize the cache manager.

        Args:
            cache_base_path: Base path for cache storage (defaults to src/data/cache)
        """
        if cache_base_path is None:
            cache_base_path = Path(__file__).parent.parent / "data" / "cache"

        self.cache_base_path = cache_base_path
        self.diagram_cache_path = cache_base_path / "diagrams"
        self.icon_cache_path = cache_base_path / "icons"
        self.metadata_cache_path = cache_base_path / "metadata"
        
        # Cache settings
        self.default_ttl = timedelta(hours=24)  # 24 hour default TTL
        self.diagram_ttl = timedelta(hours=1)   # 1 hour for diagrams (config might change)
        self.icon_ttl = timedelta(days=7)       # 1 week for icons (rarely change)
        
        # Create cache directories
        self._create_directories()
        
        # In-memory caches for frequently accessed data
        self._memory_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._memory_cache_max_size = 100
        
    def _create_directories(self) -> None:
        """Create necessary directories for cache storage."""
        self.cache_base_path.mkdir(parents=True, exist_ok=True)
        self.diagram_cache_path.mkdir(parents=True, exist_ok=True)
        self.icon_cache_path.mkdir(parents=True, exist_ok=True)
        self.metadata_cache_path.mkdir(parents=True, exist_ok=True)

    def _generate_cache_key(self, data: Any) -> str:
        """
        Generate a unique cache key for given data.

        Args:
            data: Data to generate key for

        Returns:
            SHA256 hash of the data
        """
        if isinstance(data, (dict, list)):
            # For JSON-serializable data
            json_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(json_str.encode()).hexdigest()
        elif hasattr(data, 'dict'):
            # For Pydantic models
            json_str = json.dumps(data.dict(), sort_keys=True, default=str)
            return hashlib.sha256(json_str.encode()).hexdigest()
        else:
            # For other data types
            data_str = str(data)
            return hashlib.sha256(data_str.encode()).hexdigest()

    def _is_cache_valid(self, cache_file: Path, ttl: timedelta) -> bool:
        """
        Check if a cache file is still valid based on TTL.

        Args:
            cache_file: Path to cache file
            ttl: Time to live for the cache

        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_file.exists():
            return False
            
        try:
            file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            return datetime.now() - file_mtime < ttl
        except Exception:
            return False

    def cache_diagram(
        self, 
        architecture: Architecture, 
        config: DiagramConfig, 
        diagram_path: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Cache a generated diagram and its metadata.

        Args:
            architecture: The architecture that was diagrammed
            config: Diagram configuration used
            diagram_path: Path to the generated diagram file
            metadata: Diagram metadata

        Returns:
            True if caching was successful
        """
        try:
            # Generate cache key from architecture and config
            cache_data = {
                "architecture": architecture.dict(),
                "config": config.dict()
            }
            cache_key = self._generate_cache_key(cache_data)
            
            # Store metadata
            metadata_file = self.metadata_cache_path / f"{cache_key}.json"
            cache_metadata = {
                "diagram_path": diagram_path,
                "metadata": metadata,
                "cached_at": datetime.now().isoformat(),
                "architecture_name": architecture.name,
                "format": config.format.value
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(cache_metadata, f, indent=2, default=str)
            
            # Copy diagram file to cache if it exists and is not already in cache
            diagram_file = Path(diagram_path)
            if diagram_file.exists():
                cached_diagram = self.diagram_cache_path / f"{cache_key}.{config.format.value}"
                if not cached_diagram.exists():
                    import shutil
                    shutil.copy2(diagram_file, cached_diagram)
            
            logger.debug(f"Cached diagram with key: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache diagram: {e}")
            return False

    def get_cached_diagram(
        self, 
        architecture: Architecture, 
        config: DiagramConfig
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Retrieve a cached diagram if it exists and is valid.

        Args:
            architecture: The architecture to diagram
            config: Diagram configuration

        Returns:
            Tuple of (diagram_path, metadata) if cached diagram exists, None otherwise
        """
        try:
            # Generate cache key
            cache_data = {
                "architecture": architecture.dict(),
                "config": config.dict()
            }
            cache_key = self._generate_cache_key(cache_data)
            
            # Check if metadata exists and is valid
            metadata_file = self.metadata_cache_path / f"{cache_key}.json"
            if not self._is_cache_valid(metadata_file, self.diagram_ttl):
                return None
            
            # Check if diagram file exists and is valid
            cached_diagram = self.diagram_cache_path / f"{cache_key}.{config.format.value}"
            if not self._is_cache_valid(cached_diagram, self.diagram_ttl):
                return None
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                cache_metadata = json.load(f)
            
            logger.info(f"Found cached diagram: {cache_metadata.get('architecture_name')}")
            return str(cached_diagram), cache_metadata.get('metadata', {})
            
        except Exception as e:
            logger.debug(f"Cache miss or error retrieving cached diagram: {e}")
            return None

    def cache_in_memory(self, key: str, data: Any, ttl: Optional[timedelta] = None) -> None:
        """
        Cache data in memory for fast access.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live (defaults to default_ttl)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        # Clean up memory cache if it's getting too large
        if len(self._memory_cache) >= self._memory_cache_max_size:
            self._cleanup_memory_cache()
        
        expiry_time = datetime.now() + ttl
        self._memory_cache[key] = (data, expiry_time)

    def get_from_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve data from memory cache.

        Args:
            key: Cache key

        Returns:
            Cached data if valid, None otherwise
        """
        if key not in self._memory_cache:
            return None
            
        data, expiry_time = self._memory_cache[key]
        if datetime.now() > expiry_time:
            del self._memory_cache[key]
            return None
            
        return data

    def _cleanup_memory_cache(self) -> None:
        """Clean up expired entries from memory cache."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in self._memory_cache.items()
            if now > expiry
        ]
        
        for key in expired_keys:
            del self._memory_cache[key]
        
        # If still too large, remove oldest entries
        if len(self._memory_cache) >= self._memory_cache_max_size:
            # Sort by expiry time and remove oldest
            sorted_items = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1][1]  # Sort by expiry time
            )
            
            # Keep only the newest half
            keep_count = self._memory_cache_max_size // 2
            self._memory_cache = dict(sorted_items[-keep_count:])

    def cache_technology_catalog(self, catalog_data: Dict[str, Any]) -> bool:
        """
        Cache technology catalog data.

        Args:
            catalog_data: Technology catalog data to cache

        Returns:
            True if caching was successful
        """
        try:
            cache_file = self.metadata_cache_path / "technology_catalog.json"
            cache_data = {
                "data": catalog_data,
                "cached_at": datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            # Also cache in memory for fast access
            self.cache_in_memory("technology_catalog", catalog_data)
            
            logger.debug("Cached technology catalog")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache technology catalog: {e}")
            return False

    def get_cached_technology_catalog(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached technology catalog data.

        Returns:
            Cached catalog data if valid, None otherwise
        """
        # Try memory cache first
        memory_data = self.get_from_memory("technology_catalog")
        if memory_data is not None:
            return memory_data
        
        try:
            cache_file = self.metadata_cache_path / "technology_catalog.json"
            if not self._is_cache_valid(cache_file, self.default_ttl):
                return None
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            catalog_data = cache_data.get('data')
            if catalog_data:
                # Cache in memory for next time
                self.cache_in_memory("technology_catalog", catalog_data)
            
            return catalog_data
            
        except Exception as e:
            logger.debug(f"Cache miss or error retrieving technology catalog: {e}")
            return None

    def clear_cache(self, cache_type: Optional[str] = None) -> bool:
        """
        Clear cache data.

        Args:
            cache_type: Type of cache to clear ("diagrams", "icons", "metadata", "memory", or None for all)

        Returns:
            True if clearing was successful
        """
        try:
            if cache_type is None or cache_type == "all":
                # Clear all caches
                import shutil
                if self.cache_base_path.exists():
                    shutil.rmtree(self.cache_base_path)
                self._create_directories()
                self._memory_cache.clear()
                logger.info("Cleared all caches")
                
            elif cache_type == "diagrams":
                import shutil
                if self.diagram_cache_path.exists():
                    shutil.rmtree(self.diagram_cache_path)
                self.diagram_cache_path.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared diagram cache")
                
            elif cache_type == "icons":
                import shutil
                if self.icon_cache_path.exists():
                    shutil.rmtree(self.icon_cache_path)
                self.icon_cache_path.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared icon cache")
                
            elif cache_type == "metadata":
                import shutil
                if self.metadata_cache_path.exists():
                    shutil.rmtree(self.metadata_cache_path)
                self.metadata_cache_path.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared metadata cache")
                
            elif cache_type == "memory":
                self._memory_cache.clear()
                logger.info("Cleared memory cache")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = {
                "memory_cache_size": len(self._memory_cache),
                "diagram_cache_files": len(list(self.diagram_cache_path.glob("*"))) if self.diagram_cache_path.exists() else 0,
                "icon_cache_files": len(list(self.icon_cache_path.glob("*"))) if self.icon_cache_path.exists() else 0,
                "metadata_cache_files": len(list(self.metadata_cache_path.glob("*"))) if self.metadata_cache_path.exists() else 0,
            }
            
            # Calculate cache sizes
            def get_dir_size(path: Path) -> int:
                if not path.exists():
                    return 0
                return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            
            stats["cache_size_bytes"] = {
                "diagrams": get_dir_size(self.diagram_cache_path),
                "icons": get_dir_size(self.icon_cache_path),
                "metadata": get_dir_size(self.metadata_cache_path),
            }
            stats["total_cache_size_bytes"] = sum(stats["cache_size_bytes"].values())
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.

    Returns:
        Global CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def reset_cache_manager() -> None:
    """Reset the global cache manager instance (useful for testing)."""
    global _cache_manager
    _cache_manager = None