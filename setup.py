#!/usr/bin/env python3
"""
Setup script for Agent Memory OS

A comprehensive memory layer for AI agents providing persistent, semantic + episodic memory
that spans time, tools, and multi-agent systems.
"""

import os
import sys
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    requirements = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

# Core dependencies
install_requires = read_requirements('requirements.txt')

# Optional dependencies for different integrations
extras_require = {
    'langchain': [
        'langchain>=0.1.0',
        'langchain-community>=0.0.10',
        'langchain-core>=0.1.0',
    ],
    'langgraph': [
        'langgraph>=0.0.20',
    ],
    'pinecone': [
        'pinecone>=7.0.0',
    ],
    'postgresql': [
        'psycopg2-binary>=2.9.0',
    ],
    'api': [
        'fastapi>=0.100.0',
        'uvicorn[standard]>=0.20.0',
        'httpx>=0.24.0',
    ],
    'mcp': [
        'mcp>=1.0.0',
    ],
    'dev': [
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'black>=23.0.0',
        'flake8>=6.0.0',
        'mypy>=1.0.0',
    ],
    'all': [
        'langchain>=0.1.0',
        'langchain-community>=0.0.10',
        'langchain-core>=0.1.0',
        'langgraph>=0.0.20',
        'pinecone>=7.0.0',
        'psycopg2-binary>=2.9.0',
        'fastapi>=0.100.0',
        'uvicorn[standard]>=0.20.0',
        'httpx>=0.24.0',
        'mcp>=1.0.0',
    ]
}

# Development dependencies
extras_require['dev'].extend(extras_require['all'])

setup(
    name="agent-memory-os",
    version="0.1.0",
    author="Agent Memory OS Contributors",
    author_email="contributors@agent-memory-os.dev",
    description="A comprehensive memory layer for AI agents providing persistent, semantic + episodic memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/agent-memory-os",
    project_urls={
        "Bug Tracker": "https://github.com/your-org/agent-memory-os/issues",
        "Documentation": "https://github.com/your-org/agent-memory-os#readme",
        "Source Code": "https://github.com/your-org/agent-memory-os",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Framework :: FastAPI",
        "Framework :: LangChain",
        "Framework :: LangGraph",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    package_data={
        "agent_memory_sdk": [
            "api/static/*",
            "api/static/*/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-memory-api=agent_memory_sdk.api.server:main",
            "agent-memory-mcp=agent_memory_sdk.integrations.mcp.memory_mcp_server:main",
            "agent-memory-test=run_tests:main",
        ],
    },
    keywords=[
        "ai",
        "agents",
        "memory",
        "langchain",
        "langgraph",
        "pinecone",
        "postgresql",
        "vector-search",
        "semantic-memory",
        "episodic-memory",
        "machine-learning",
        "artificial-intelligence",
    ],
    platforms=["any"],
    zip_safe=False,
) 