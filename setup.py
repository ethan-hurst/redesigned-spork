#!/usr/bin/env python3
"""
Setup script for Microsoft Dynamics & Power Platform Architecture Builder.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements.txt
requirements_path = this_directory / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="dynamics-powerplatform-architecture-builder",
    version="0.1.0",
    author="Microsoft Architecture Builder",
    author_email="noreply@example.com",
    description="Generate architectural diagrams for Microsoft Dynamics & Power Platform stacks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/dynamics-powerplatform-architecture-builder",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": ["data/*.json", "data/templates/*"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Documentation",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dynamics-arch-builder=main:cli",
            "dynamics-powerplatform-builder=main:cli",
        ],
    },
    keywords="microsoft dynamics power-platform architecture diagrams azure",
    project_urls={
        "Documentation": "https://github.com/example/dynamics-powerplatform-architecture-builder/blob/main/README.md",
        "Source": "https://github.com/example/dynamics-powerplatform-architecture-builder",
        "Tracker": "https://github.com/example/dynamics-powerplatform-architecture-builder/issues",
    },
)