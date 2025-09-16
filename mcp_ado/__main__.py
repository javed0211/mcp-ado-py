#!/usr/bin/env python3
"""
Azure DevOps MCP Server Entry Point

This module serves as the main entry point for the Azure DevOps MCP server.
It can be run directly with: python -m mcp_ado
"""

import asyncio
import sys
from .server import main

if __name__ == "__main__":
    asyncio.run(main())