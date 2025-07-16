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
- 🔁 Works across **LangChain**, **CrewAI**, **LangGraph**, **REST API**, and custom agents
- 🧠 Designed for **multi-agent collaboration** with shared context
- 📚 Easily plug into your LLM pipeline via a simple SDK, API, or HTTP
- ⏱️ Supports time-aware memory recall and timeline reconstruction

---

## 🛠️ Who It's For

- AI engineers building assistants, copilots, and autonomous workflows
- Teams using LangGraph, CrewAI, LangChain, or REST APIs
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

#### LangChain Integration ✅ **COMPLETE**

- ✅ **MemoryChain** - LangChain chain with automatic memory storage and retrieval
- ✅ **MemoryTool** - LangChain tool for agents to store facts and search memories
- ✅ **MemoryCallbackHandler** - Automatic memory storage during chain/agent execution
- ✅ **MemoryAwareAgent** - Wrapper for any LangChain agent with memory capabilities
- ✅ **Complete integration demo** - Working example with all components
- ✅ **Memory persistence** - Memories survive across sessions and agent restarts
- ✅ **Semantic search** - Basic text-based search for relevant memories
- ✅ **Timeline retrieval** - Get chronological history of agent activities

#### LangGraph Integration ✅ **NEW - COMPLETE**

- ✅ **MemoryGraph** - Complete memory-aware LangGraph workflow wrapper
- ✅ **MemoryState** - State class with memory capabilities for LangGraph
- ✅ **MemoryNode** - Node that provides memory operations in workflows
- ✅ **MemoryToolNode** - Tools that can be used in any LangGraph workflow
- ✅ **create_memory_tools** - Helper function to create memory tools
- ✅ **Complete integration demo** - 4 comprehensive demos showing different usage patterns
- ✅ **Memory persistence** - Memories survive across graph executions
- ✅ **Agent-specific memory isolation** - Each agent/workflow has isolated memory
- ✅ **ToolNode compatibility** - Works with latest LangGraph ToolNode API
- ✅ **Dict-based state management** - Maximum compatibility with LangGraph

#### REST API Integration ✅ **NEW - COMPLETE**

- ✅ **FastAPI-based REST API** for remote memory access
- ✅ **Full CRUD**: create, update, delete, search, and list memories
- ✅ **Agent-specific endpoints** and statistics
- ✅ **Health and status endpoints**
- ✅ **Python client library** (`MemoryAPIClient`, `AsyncMemoryAPIClient`)
- ✅ **Comprehensive demo** (`examples/api_demo.py`)
- ✅ **Interactive docs** at `/docs` and `/redoc`

#### Web UI Integration ✅ **NEW - COMPLETE**

- ✅ **Modern web interface** for memory visualization and management
- ✅ **Real-time statistics** and memory type breakdowns
- ✅ **Interactive search and filtering** by type, agent, and importance
- ✅ **Memory detail views** with full metadata
- ✅ **Create and delete memories** directly from the UI
- ✅ **Responsive design** that works on desktop and mobile
- ✅ **Auto-refresh** and live updates
- ✅ **Sample data demo** (`examples/web_ui_demo.py`)

### 🚧 **Partially Implemented**

#### Semantic Search

- ✅ **Vector similarity search** with Pinecone integration
- ✅ **Model-based embeddings** using `llama-text-embed-v2` (1024 dimensions)
- ✅ **High-quality semantic search** across all memory types
- ✅ **Fallback text search** for SQLite backend
- ✅ **Cosine similarity** calculations for relevance scoring

#### LangChain Integration

- ⚠️ **MemoryAwareAgent callback compatibility** - Minor callback handler issue with LLMChain (cosmetic, doesn't affect core functionality)
- ⚠️ **Deprecation warnings** - Some LangChain APIs are deprecated but still functional

### ❌ **Not Yet Implemented**

#### Advanced Features

- ❌ Vector similarity search using embeddings
- ❌ Integration with proper embedding models (OpenAI, sentence-transformers)
- ❌ Memory compression and summarization
- ❌ Memory importance scoring
- ❌ Automatic memory cleanup/archival
- ❌ Multi-agent memory sharing protocols

#### Integrations

- ❌ Direct CrewAI integration (only example code provided)

#### Storage Backends

- ✅ **Pinecone Integration** - Vector database with semantic search
  - ✅ Model-based embeddings with `llama-text-embed-v2`
  - ✅ 1024-dimensional vectors for high-quality semantic search
  - ✅ Automatic index creation and management
  - ✅ Cross-session memory persistence
  - ✅ Full CRUD operations with metadata
- ✅ **Store Factory** - Adapter pattern for multiple backends
- ✅ **Auto-detection** - Automatically chooses SQLite or Pinecone
- ❌ PostgreSQL backend
- ❌ Redis backend
- ❌ Other vector databases (Weaviate, Qdrant, etc.)clear
- ❌ Cloud storage options

#### Advanced Memory Features

- ❌ Memory relationships and linking
- ❌ Memory versioning and history
- ❌ Memory privacy and access control
- ❌ Memory export/import functionality
- ❌ Memory analytics and insights

---

## 🔍 MVP Goal

Enable a basic CrewAI, LangChain, LangGraph, or REST API agent to:

- ✅ Remember key facts across sessions
- ✅ Recall specific past interactions (episodic)
- ✅ Retrieve semantically relevant info when prompted (basic text search)
- ✅ Track events across time
- ✅ Access and manage memory remotely via HTTP or Python client

**✅ MVP COMPLETED** - All core memory functionality is working with LangChain, LangGraph, and REST API integrations!

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
│   │   ├── base_store.py      # Abstract base class
│   │   ├── sqlite_store.py    # SQLite storage implementation
│   │   ├── pinecone_store.py  # Pinecone vector storage
│   │   └── store_factory.py   # Store factory for backend selection
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── embedding_utils.py # Embedding generation and similarity
│   │   └── time_utils.py      # Time formatting utilities
│   ├── api/                   # REST API (FastAPI server, client, models)
│   │   ├── __init__.py
│   │   ├── server.py          # FastAPI app and endpoints
│   │   ├── models.py          # Pydantic models for API
│   │   ├── client.py          # Python/async client for API
│   │   └── static/            # Web UI static files
│   │       ├── index.html     # Main web UI page
│   │       ├── styles.css     # Web UI styles
│   │       └── app.js         # Web UI JavaScript
│   └── integrations/          # Framework integrations
│       ├── __init__.py
│       ├── langchain/         # LangChain integration
│       │   ├── __init__.py
│       │   ├── memory_chain.py        # MemoryChain class
│       │   ├── memory_tool.py         # MemoryTool class
│       │   ├── memory_callback.py     # MemoryCallbackHandler
│       │   └── memory_agent.py        # MemoryAwareAgent wrapper
│       └── langgraph/         # LangGraph integration
│           ├── __init__.py
│           ├── memory_graph.py        # MemoryGraph class
│           ├── memory_state.py        # MemoryState class
│           ├── memory_node.py         # MemoryNode class
│           └── memory_tool_node.py    # MemoryToolNode class
├── examples/                  # Integration examples
│   ├── crewai_memory_demo.py  # CrewAI integration demo
│   ├── langchain_memory_demo.py # LangChain integration demo
│   ├── langgraph_memory_demo.py # LangGraph integration demo
│   ├── api_demo.py            # REST API demo (HTTP, client, async)
│   └── web_ui_demo.py         # Web UI demo with sample data
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

### Run the REST API Server

```bash
# Run from the project root directory
python run_api.py --host 127.0.0.1 --port 8000
```

**API Endpoints:**

- 📚 **Docs**: http://127.0.0.1:8000/docs (Interactive API documentation)
- 🔍 **ReDoc**: http://127.0.0.1:8000/redoc (Alternative API docs)
- ❤️ **Health**: http://127.0.0.1:8000/health (Server status)
- 🎨 **Web UI**: http://127.0.0.1:8000 (Interactive web interface)

**Features:**

- Full CRUD operations for memories
- Semantic search and filtering
- Agent-specific endpoints
- Real-time statistics and health monitoring

### Use the Python Client

```python
from agent_memory_sdk.api import MemoryAPIClient
from agent_memory_sdk.api.models import MemoryCreateRequest
from agent_memory_sdk.models import MemoryType

with MemoryAPIClient("http://localhost:8000") as client:
    req = MemoryCreateRequest(content="Hello", memory_type=MemoryType.SEMANTIC)
    memory = client.create_memory(req)
    print(memory)
```

### Use the Async Python Client

```python
import asyncio
from agent_memory_sdk.api import AsyncMemoryAPIClient
from agent_memory_sdk.api.models import MemoryCreateRequest
from agent_memory_sdk.models import MemoryType

async def main():
    async with AsyncMemoryAPIClient("http://localhost:8000") as client:
        req = MemoryCreateRequest(content="Async hello", memory_type=MemoryType.EPISODIC)
        memory = await client.create_memory(req)
        print(memory)

asyncio.run(main())
```

### Try the REST API Demo

```bash
python examples/api_demo.py
```

### Try the Web UI Demo

```bash
# Run from any directory - the script will automatically find the project root
python examples/web_ui_demo.py
```

This will:

1. **Create sample memory data** with various types and agents
2. **Launch the web UI server** at http://localhost:8000
3. **Open your browser** automatically to the web interface
4. **Show interactive features** like search, filtering, and memory management

**Web UI Features:**

- 📊 Real-time memory statistics and breakdowns
- 🔍 Interactive search and filtering by type, agent, and importance
- 📝 Create and delete memories directly from the interface
- 📱 Responsive design for desktop and mobile
- 🔄 Auto-refresh and live updates

### Basic Usage (SDK)

```python
from agent_memory_sdk import MemoryManager, MemoryType

# Initialize memory manager (auto-detects SQLite or Pinecone)
memory_manager = MemoryManager()

# Add memories
memory_manager.add_memory(
    content="User prefers Python programming",
    memory_type=MemoryType.SEMANTIC,
    agent_id="my_agent",
    importance=8.0,
    tags=["preference", "programming"]
)

# Search memories (semantic search with Pinecone, text search with SQLite)
results = memory_manager.search_memory("Python")
```

### Storage Backends

The system supports multiple storage backends:

#### SQLite (Default - Local)

```python
# Local SQLite storage
memory_manager = MemoryManager(store_type="sqlite", db_path="memories.db")
```

#### Pinecone (Cloud - Vector Search)

```bash
# Set environment variables
export PINECONE_API_KEY="your-api-key"
export PINECONE_ENVIRONMENT="your-environment"
```

```python
# Pinecone vector storage with semantic search
memory_manager = MemoryManager(store_type="pinecone", index_name="my-memories")
```

### Try the Pinecone Demo

```bash
# Set your Pinecone credentials
export PINECONE_API_KEY="your-api-key"
export PINECONE_ENVIRONMENT="your-environment"

# Run the demo
python examples/pinecone_memory_demo.py
```

**Features demonstrated:**

- Model-based embeddings with `llama-text-embed-v2`
- High-quality semantic search
- Memory persistence across sessions
- Comparison between SQLite and Pinecone backends

### LangChain Integration

```python
from agent_memory_sdk import MemoryChain, MemoryManager
from langchain_community.llms import OpenAI

# Initialize memory manager
memory_manager = MemoryManager()

# Create memory-aware chain
memory_chain = MemoryChain(
    memory_manager=memory_manager,
    llm=OpenAI(),
    agent_id="my_agent"
)

# Use with memory persistence
result = memory_chain.invoke({"input": "What do you remember about me?"})
print(result["output"])
```

### LangGraph Integration

```python
from agent_memory_sdk import MemoryGraph, MemoryManager
from langgraph.graph import StateGraph, END

# Initialize memory manager
memory_manager = MemoryManager()

# Create memory-aware graph
memory_graph = MemoryGraph(
    memory_manager=memory_manager,
    agent_id="my_agent",
    session_id="session_1"
)

# Create a simple graph
graph = memory_graph.create_graph()

# Add a processing node
def process_input(state):
    input_text = state.get("input", "")
    memory_graph.memory_manager.add_memory(
        content=f"Processed: {input_text}",
        memory_type=MemoryType.EPISODIC,
        agent_id=memory_graph.agent_id,
        session_id=memory_graph.session_id
    )
    return {"output": f"Processed: {input_text}"}

graph.add_node("process", process_input)
graph.set_entry_point("process")
graph.add_edge("process", END)

# Compile and run
compiled_graph = graph.compile()
result = compiled_graph.invoke({"input": "Hello, this is my first memory!"})
```

### Memory Tools in LangGraph

```python
from agent_memory_sdk import create_memory_tools, MemoryManager
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# Create memory tools
memory_tools = create_memory_tools(
    memory_manager=MemoryManager(),
    agent_id="my_agent"
)

# Create tool node
tool_node = ToolNode(memory_tools)

# Use with proper message format
tool_call = {
    "name": "store_memory",
    "args": {"content": "I learned something new", "memory_type": "semantic"},
    "id": str(uuid.uuid4()),
    "type": "tool_call"
}

state = {
    "messages": [
        HumanMessage(content="Store a memory"),
        AIMessage(content="", tool_calls=[tool_call])
    ]
}

result = tool_node.invoke(state)
```

### Run Demos

```bash
# All demos can be run from any directory - they'll automatically find the project root

# Core memory demo (SQLite backend)
python examples/crewai_memory_demo.py

# LangChain integration demo
python examples/langchain_memory_demo.py

# LangGraph integration demo
python examples/langgraph_memory_demo.py

# REST API demo (tests HTTP client and async client)
python examples/api_demo.py

# Web UI demo (creates sample data and launches web interface)
python examples/web_ui_demo.py

# Pinecone integration demo (requires Pinecone credentials)
python examples/pinecone_memory_demo.py
```

**Demo Features:**

- 🧠 **Core Demo**: Basic memory operations with SQLite
- 🔗 **LangChain Demo**: Memory-aware chains, tools, and agents
- 📊 **LangGraph Demo**: Memory integration with workflows and state
- 🌐 **API Demo**: HTTP client, async client, and REST endpoints
- 🎨 **Web UI Demo**: Interactive web interface with sample data
- 🌲 **Pinecone Demo**: Vector search with semantic embeddings

### Debug and Maintenance Tools

```bash
# Debug Pinecone configuration
python debug_pinecone.py

# Debug Pinecone search functionality
python debug_pinecone_search.py

# Clean up old Pinecone indexes
python cleanup_pinecone.py
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Troubleshooting

**Common Issues:**

1. **"run_api.py not found" error**

   - ✅ **Fixed**: All demo scripts now automatically find the project root
   - Run demos from any directory: `python examples/web_ui_demo.py`

2. **Pinecone connection errors**

   - Set environment variables: `export PINECONE_API_KEY="your-key"`
   - Use supported environment: `export PINECONE_ENVIRONMENT="gcp-starter"`
   - Run debug script: `python debug_pinecone.py`

3. **API server startup errors**

   - ✅ **Fixed**: MemoryManager initialization now properly handles store types
   - Ensure you're in the project root: `python run_api.py --host 127.0.0.1 --port 8000`

4. **Memory search returning 0 results**
   - Check if memories were saved successfully
   - Run debug script: `python debug_pinecone_search.py`
   - Clean up old indexes: `python cleanup_pinecone.py`

---

## 🔗 Status

🚀 **MVP Complete + Full Framework Integration + Vector Search** — Core memory system is working with SQLite and Pinecone storage, comprehensive LangChain, LangGraph, and REST API integrations, persistent memory across sessions, and high-quality semantic search capabilities.

**Current Capabilities:**

- ✅ Persistent memory storage and retrieval
- ✅ LangChain integration with chains, tools, and agents
- ✅ LangGraph integration with workflows, state management, and tools
- ✅ REST API for remote memory access (HTTP, Python, async)
- ✅ Web UI for memory visualization and management
- ✅ Memory-aware responses with context
- ✅ Timeline and semantic search
- ✅ Cross-session memory persistence
- ✅ Agent-specific memory isolation
- ✅ **Vector similarity search** with Pinecone integration
- ✅ **Model-based embeddings** for high-quality semantic search
- ✅ **Robust demo scripts** that work from any directory
- ✅ **Comprehensive debugging tools** for troubleshooting

**Next Milestones:**

1. Add CrewAI integration
2. Implement memory compression and summarization
3. Add memory importance scoring

---

## 📬 Stay in the Loop

Want to contribute or test it early? Reach out or open an issue!
