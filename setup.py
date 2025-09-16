#!/usr/bin/env python3
"""
Setup script for Azure DevOps MCP Server
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-ado-py",
    version="1.0.0",
    author="Azure DevOps MCP Team",
    description="Azure DevOps Model Context Protocol Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "mcp-ado=mcp_ado.__main__:main",
        ],
    },
)