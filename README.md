# agent-memory-os

Agent Memory OS is an open-source memory layer for AI agents — providing persistent, semantic + episodic memory that spans time, tools, and multi-agent systems.

# 🧠 Agent Memory OS

## Overview

Modern LLM agents are smart — but forgetful.

They can answer questions, write code, and simulate workflows, but as soon as the session ends, they forget everything. This creates brittle experiences, limits long-term learning, and makes it hard to scale AI assistants in real-world use cases.

**Agent Memory OS** solves this by offering a plug-and-play memory architecture that adds persistent, structured memory to your AI agents — across sessions, across tasks, and even across teams of agents.

---

## 🚧 The Problem

LLM agents today lack true long-term memory.

- ❌ Agents forget previous conversations or context unless manually re-fed.
- ❌ Developers have to rebuild memory pipelines from scratch for every app.
- ❌ No standard for sharing memory across agents or workflows.
- ❌ Vector search ≠ structured memory with episodic or semantic context.
- ❌ No temporal awareness — agents don't "remember what happened when."

This results in fragile systems and poor user experience.

---

## ✅ The Solution

**Agent Memory OS** is a developer-first memory framework for agentic systems.

- 🧩 Unified **episodic**, **semantic**, and **temporal** memory
- 🔁 Works across **LangChain**, **CrewAI**, **LangGraph**, and custom agents
- 🧠 Designed for **multi-agent collaboration** with shared context
- 📚 Easily plug into your LLM pipeline via a simple SDK or API
- ⏱️ Supports time-aware memory recall and timeline reconstruction

---

## 🛠️ Who It's For

- AI engineers building assistants, copilots, and autonomous workflows
- Teams using LangGraph, CrewAI, or LangChain
- Developers building apps that need persistent, evolving memory

---

## 📋 Implementation Status

### ✅ **Fully Implemented**

#### Core Memory System

- **MemoryManager** - Main interface for memory operations
- **MemoryEntry** - Data model for individual memories
- **MemoryType** - Enum for episodic, semantic, and temporal memory types
- **SQLiteStore** - Persistent storage backend with full CRUD operations
- **Basic embedding generation** - Hash-based embeddings for demo purposes

#### Memory Operations

- ✅ Add memories with metadata and timestamps
- ✅ Search memories by content (text-based LIKE search)
- ✅ Filter memories by type, agent_id, session_id
- ✅ Retrieve episodic memories for specific agents/sessions
- ✅ Get chronological timeline of memories
- ✅ Memory persistence across sessions

#### Utilities

- ✅ Time utilities for timestamp formatting and parsing
- ✅ Embedding utilities with cosine similarity calculations
- ✅ Memory serialization (to_dict/from_dict)

#### Testing & Examples

- ✅ Comprehensive unit tests (9/9 passing)
- ✅ Working demo with CrewAI integration example
- ✅ Memory persistence demonstration

### 🚧 **Partially Implemented**

#### Semantic Search

- ⚠️ Basic text-based search implemented
- ⚠️ Embedding generation exists but uses simple hash-based approach
- ⚠️ No vector similarity search yet (embeddings stored but not used for search)

### ❌ **Not Yet Implemented**

#### Advanced Features

- ❌ Vector similarity search using embeddings
- ❌ Integration with proper embedding models (OpenAI, sentence-transformers)
- ❌ Memory compression and summarization
- ❌ Memory importance scoring
- ❌ Automatic memory cleanup/archival
- ❌ Multi-agent memory sharing protocols

#### Integrations

- ❌ Direct LangChain integration
- ❌ Direct LangGraph integration
- ❌ Direct CrewAI integration (only example code provided)
- ❌ REST API for remote memory access
- ❌ Web UI for memory visualization

#### Storage Backends

- ❌ PostgreSQL backend
- ❌ Redis backend
- ❌ Vector databases (Pinecone, Weaviate, etc.)
- ❌ Cloud storage options

#### Advanced Memory Features

- ❌ Memory relationships and linking
- ❌ Memory versioning and history
- ❌ Memory privacy and access control
- ❌ Memory export/import functionality
- ❌ Memory analytics and insights

---

## 🔍 MVP Goal

Enable a basic CrewAI or LangGraph agent to:

- ✅ Remember key facts across sessions
- ✅ Recall specific past interactions (episodic)
- ⚠️ Retrieve semantically relevant info when prompted (basic text search)
- ✅ Track events across time

---

## 📦 Project Structure

```
agent-memory-os/
├── agent_memory_sdk/          # Core SDK
│   ├── __init__.py
│   ├── memory.py              # MemoryManager class
│   ├── models.py              # Data models (MemoryEntry, MemoryType)
│   ├── store/                 # Storage backends
│   │   ├── __init__.py
│   │   └── sqlite_store.py    # SQLite storage implementation
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── embedding_utils.py # Embedding generation and similarity
│       └── time_utils.py      # Time formatting utilities
├── examples/                  # Integration examples
│   └── crewai_memory_demo.py  # Working demo with memory persistence
├── tests/                     # Unit tests
│   ├── __init__.py
│   └── test_memory.py         # Comprehensive test suite
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Installation

```bash
git clone <repository>
cd agent-memory-os
pip install -r requirements.txt
```

### Basic Usage

```python
from agent_memory_sdk import MemoryManager, MemoryType

# Initialize memory manager
memory_manager = MemoryManager()

# Add memories
memory_manager.add_memory(
    content="User prefers Python programming",
    memory_type=MemoryType.SEMANTIC,
    agent_id="my_agent"
)

# Search memories
results = memory_manager.search_memory("Python")
```

### Run Demo

```bash
python examples/crewai_memory_demo.py
```

### Run Tests

```bash
python -m pytest tests/ -v
```

---

## 🔗 Status

🚧 **MVP Complete** — Core memory system is working with SQLite storage and basic functionality. Ready for integration with AI agent frameworks.

**Next Milestones:**

1. Implement vector similarity search
2. Add proper embedding model integration
3. Create direct framework integrations (LangChain, CrewAI, LangGraph)
4. Build REST API for remote access

---

## 📬 Stay in the Loop

Want to contribute or test it early? Reach out or open an issue!
