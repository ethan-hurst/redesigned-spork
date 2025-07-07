"""
Helper utilities for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides common utility functions used throughout the application.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

logger = logging.getLogger(__name__)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return f"{s} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length with optional suffix.
    
    Args:
        text: The text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def snake_to_title(snake_str: str) -> str:
    """
    Convert snake_case string to Title Case.
    
    Args:
        snake_str: String in snake_case format
        
    Returns:
        String in Title Case
    """
    return snake_str.replace('_', ' ').title()


def title_to_snake(title_str: str) -> str:
    """
    Convert Title Case string to snake_case.
    
    Args:
        title_str: String in Title Case format
        
    Returns:
        String in snake_case
    """
    return title_str.replace(' ', '_').lower()


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object for the directory
        
    Raises:
        OSError: If directory cannot be created
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path where to save the file
        indent: JSON indentation level
        
    Raises:
        OSError: If file cannot be written
    """
    path = Path(file_path)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later dictionaries taking precedence.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def filter_dict_by_keys(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to only include specified keys.
    
    Args:
        data: Dictionary to filter
        allowed_keys: List of keys to keep
        
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in allowed_keys}


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)

    if not path.exists():
        return {"exists": False}

    stat = path.stat()

    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "is_file": path.is_file(),
        "is_directory": path.is_dir(),
        "extension": path.suffix,
        "name": path.name,
        "stem": path.stem
    }


def create_backup_filename(original_path: Union[str, Path]) -> Path:
    """
    Create a backup filename by adding timestamp.
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup file path
    """
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return path.parent / backup_name


def list_files_with_extension(directory: Union[str, Path], extension: str) -> List[Path]:
    """
    List all files with a specific extension in a directory.
    
    Args:
        directory: Directory to search
        extension: File extension (with or without dot)
        
    Returns:
        List of file paths
    """
    path = Path(directory)

    if not path.exists() or not path.is_dir():
        return []

    # Ensure extension starts with dot
    if not extension.startswith('.'):
        extension = f'.{extension}'

    return list(path.glob(f"*{extension}"))


def clean_temporary_files(directory: Union[str, Path], pattern: str = "temp_*", max_age_hours: int = 24) -> int:
    """
    Clean temporary files older than specified age.
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match
        max_age_hours: Maximum age in hours
        
    Returns:
        Number of files cleaned
    """
    path = Path(directory)

    if not path.exists() or not path.is_dir():
        return 0

    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned_count = 0

    for file_path in path.glob(pattern):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                cleaned_count += 1
                logger.debug(f"Cleaned temporary file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to clean temporary file {file_path}: {e}")

    return cleaned_count


def generate_unique_filename(base_path: Union[str, Path], extension: str = "") -> Path:
    """
    Generate a unique filename by adding a counter if file exists.
    
    Args:
        base_path: Base file path
        extension: File extension to add
        
    Returns:
        Unique file path
    """
    path = Path(base_path)

    if extension and not extension.startswith('.'):
        extension = f'.{extension}'

    if extension:
        path = path.with_suffix(extension)

    if not path.exists():
        return path

    counter = 1
    while True:
        new_name = f"{path.stem}_{counter}{path.suffix}"
        new_path = path.parent / new_name

        if not new_path.exists():
            return new_path

        counter += 1

        # Prevent infinite loop
        if counter > 1000:
            raise ValueError("Could not generate unique filename after 1000 attempts")


def validate_and_create_output_path(
    output_dir: Union[str, Path],
    filename: str,
    extension: str,
    overwrite: bool = False
) -> Tuple[Path, bool]:
    """
    Validate and create output path, handling conflicts.
    
    Args:
        output_dir: Output directory
        filename: Desired filename
        extension: File extension
        overwrite: Whether to overwrite existing files
        
    Returns:
        Tuple of (final_path, file_existed)
    """
    directory = ensure_directory_exists(output_dir)

    if not extension.startswith('.'):
        extension = f'.{extension}'

    desired_path = directory / f"{filename}{extension}"
    file_existed = desired_path.exists()

    if file_existed and not overwrite:
        final_path = generate_unique_filename(desired_path)
    else:
        final_path = desired_path

    return final_path, file_existed


def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys

    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": str(Path.cwd())
    }


def measure_execution_time(func):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function that logs execution time
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {format_duration(execution_time)}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} failed after {format_duration(execution_time)}: {e}")
            raise

    return wrapper


class ProgressTracker:
    """Simple progress tracker for long-running operations."""

    def __init__(self, total_steps: int, description: str = "Processing"):
        """
        Initialize progress tracker.
        
        Args:
            total_steps: Total number of steps
            description: Description of the operation
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()

    def update(self, step: int = 1, message: str = "") -> None:
        """
        Update progress.
        
        Args:
            step: Number of steps to advance
            message: Optional progress message
        """
        self.current_step = min(self.current_step + step, self.total_steps)
        percentage = (self.current_step / self.total_steps) * 100

        elapsed = time.time() - self.start_time
        if self.current_step > 0:
            estimated_total = elapsed * (self.total_steps / self.current_step)
            remaining = estimated_total - elapsed
        else:
            remaining = 0

        status = f"{self.description}: {self.current_step}/{self.total_steps} ({percentage:.1f}%)"
        if message:
            status += f" - {message}"
        if remaining > 0:
            status += f" - ETA: {format_duration(remaining)}"

        logger.info(status)

    def finish(self, message: str = "Complete") -> None:
        """
        Mark progress as finished.
        
        Args:
            message: Completion message
        """
        elapsed = time.time() - self.start_time
        logger.info(f"{self.description}: {message} in {format_duration(elapsed)}")


def create_error_report(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a structured error report.
    
    Args:
        error: The exception that occurred
        context: Additional context information
        
    Returns:
        Error report dictionary
    """
    import traceback

    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info()
    }
