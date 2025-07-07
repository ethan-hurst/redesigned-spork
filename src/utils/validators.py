"""
Validation utilities for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides validation functions for various inputs and configurations.
"""

import re
from pathlib import Path
from typing import Optional, Union


def validate_component_id(component_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate a component ID format.

    Args:
        component_id: The component ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not component_id:
        return False, "Component ID cannot be empty"

    if not isinstance(component_id, str):
        return False, "Component ID must be a string"

    # Check format: lowercase with underscores, no spaces
    if not re.match(r"^[a-z][a-z0-9_]*$", component_id):
        return (
            False,
            "Component ID must start with a letter and contain only lowercase letters, numbers, and underscores",
        )

    if len(component_id) > 50:
        return False, "Component ID must be 50 characters or less"

    return True, None


def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
    """
    Validate a filename for diagram output.

    Args:
        filename: The filename to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"

    if not isinstance(filename, str):
        return False, "Filename must be a string"

    # Check for invalid characters
    invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
    for char in invalid_chars:
        if char in filename:
            return False, f"Filename cannot contain '{char}'"

    # Check length
    if len(filename) > 100:
        return False, "Filename must be 100 characters or less"

    # Check for reserved names (Windows)
    reserved_names = (
        ["CON", "PRN", "AUX", "NUL"]
        + [f"COM{i}" for i in range(1, 10)]
        + [f"LPT{i}" for i in range(1, 10)]
    )
    if filename.upper() in reserved_names:
        return False, f"'{filename}' is a reserved filename"

    return True, None


def validate_directory_path(directory_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate a directory path.

    Args:
        directory_path: The directory path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not directory_path:
        return False, "Directory path cannot be empty"

    try:
        path = Path(directory_path)

        # Check if it's a valid path format
        path.resolve()

        # Check if we can create the directory
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                # Clean up test directory if it was created
                if not any(path.iterdir()):  # Only remove if empty
                    path.rmdir()
            except PermissionError:
                return (
                    False,
                    f"Permission denied: cannot create directory '{directory_path}'",
                )
            except OSError as e:
                return False, f"Invalid directory path: {e}"
        elif path.is_file():
            return False, f"Path '{directory_path}' is a file, not a directory"

        return True, None

    except (ValueError, OSError) as e:
        return False, f"Invalid directory path: {e}"


def validate_component_list(
    component_ids: Union[str, list[str]],
) -> tuple[bool, Optional[str], list[str]]:
    """
    Validate a list of component IDs.

    Args:
        component_ids: String of comma-separated IDs or list of IDs

    Returns:
        Tuple of (is_valid, error_message, cleaned_list)
    """
    if isinstance(component_ids, str):
        # Split comma-separated string
        id_list = [comp.strip() for comp in component_ids.split(",") if comp.strip()]
    elif isinstance(component_ids, list):
        id_list = [str(comp).strip() for comp in component_ids if str(comp).strip()]
    else:
        return False, "Component IDs must be a string or list", []

    if not id_list:
        return False, "At least one component ID is required", []

    # Validate each component ID
    errors = []
    valid_ids = []

    for comp_id in id_list:
        is_valid, error = validate_component_id(comp_id)
        if is_valid:
            valid_ids.append(comp_id)
        else:
            errors.append(f"'{comp_id}': {error}")

    if errors:
        return False, f"Invalid component IDs: {'; '.join(errors)}", valid_ids

    # Check for duplicates
    unique_ids = list(set(valid_ids))
    if len(unique_ids) != len(valid_ids):
        return False, "Duplicate component IDs found", unique_ids

    return True, None, unique_ids


def validate_image_dimensions(width: int, height: int) -> tuple[bool, Optional[str]]:
    """
    Validate image dimensions for diagram output.

    Args:
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return False, "Width and height must be integers"

    if width <= 0 or height <= 0:
        return False, "Width and height must be positive"

    if width < 200 or height < 150:
        return False, "Minimum dimensions are 200x150 pixels"

    if width > 5000 or height > 5000:
        return False, "Maximum dimensions are 5000x5000 pixels"

    # Check aspect ratio
    aspect_ratio = width / height
    if aspect_ratio < 0.3 or aspect_ratio > 5.0:
        return False, "Aspect ratio must be between 0.3 and 5.0"

    return True, None


def validate_dpi(dpi: int) -> tuple[bool, Optional[str]]:
    """
    Validate DPI setting for image output.

    Args:
        dpi: DPI value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(dpi, int):
        return False, "DPI must be an integer"

    if dpi < 72:
        return False, "Minimum DPI is 72"

    if dpi > 600:
        return False, "Maximum DPI is 600"

    return True, None


def validate_architecture_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate an architecture name.

    Args:
        name: The architecture name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Architecture name cannot be empty"

    if not isinstance(name, str):
        return False, "Architecture name must be a string"

    if len(name.strip()) == 0:
        return False, "Architecture name cannot be only whitespace"

    if len(name) > 100:
        return False, "Architecture name must be 100 characters or less"

    # Check for reasonable content
    if len(name.strip()) < 3:
        return False, "Architecture name must be at least 3 characters"

    return True, None


def validate_output_format(format_str: str) -> tuple[bool, Optional[str]]:
    """
    Validate output format.

    Args:
        format_str: The format string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not format_str:
        return False, "Output format cannot be empty"

    valid_formats = ["png", "svg", "pdf", "jpg", "jpeg"]

    if format_str.lower() not in valid_formats:
        return (
            False,
            f"Invalid format '{format_str}'. Valid formats: {', '.join(valid_formats)}",
        )

    return True, None


def validate_spacing_value(
    value: float, min_value: float = 0.1, max_value: float = 10.0
) -> tuple[bool, Optional[str]]:
    """
    Validate spacing values for diagram layout.

    Args:
        value: The spacing value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, "Spacing value must be a number"

    if value < min_value:
        return False, f"Spacing value must be at least {min_value}"

    if value > max_value:
        return False, f"Spacing value must be at most {max_value}"

    return True, None


def validate_color_hex(color: str) -> tuple[bool, Optional[str]]:
    """
    Validate a hex color code.

    Args:
        color: The hex color code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not color:
        return False, "Color cannot be empty"

    if not isinstance(color, str):
        return False, "Color must be a string"

    # Remove # if present
    color = color.lstrip("#")

    # Check format
    if not re.match(r"^[0-9A-Fa-f]{6}$", color):
        return False, "Color must be a valid 6-digit hex code (e.g., #FF0000 or FF0000)"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    if not filename:
        return "untitled"

    # Replace invalid characters with underscores
    invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(" .")

    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]

    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"

    return sanitized


def validate_json_structure(
    data: dict, required_keys: list[str]
) -> tuple[bool, Optional[str]]:
    """
    Validate JSON structure has required keys.

    Args:
        data: Dictionary to validate
        required_keys: List of required keys

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"

    return True, None
