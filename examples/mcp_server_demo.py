"""
MCP Server Demo for Agent Memory OS

Demonstrates how to run the MCP server and connect it to Claude Desktop
or other MCP-compatible clients.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_memory_sdk.memory import MemoryManager
from agent_memory_sdk.models import MemoryType
from agent_memory_sdk.integrations.mcp import create_memory_mcp_server

async def main():
    print("🧠 Agent Memory OS - MCP Server Demo")
    print("=" * 50)
    # Initialize memory manager
    print("📦 Initializing memory manager...")
    memory_manager = MemoryManager(store_type="sqlite")
    
    # Add some sample memories
    print("📝 Adding sample memories...")
    memory_manager.add_memory(
        content="User prefers dark mode in applications",
        memory_type=MemoryType.SEMANTIC,
        agent_id="demo-agent",
        importance=8.0,
        tags=["preferences", "ui"]
    )
    memory_manager.add_memory(
        content="User asked about Python async programming",
        memory_type=MemoryType.EPISODIC,
        agent_id="demo-agent",
        importance=7.0,
        tags=["programming", "python"]
    )
    memory_manager.add_memory(
        content="User's birthday is March 15th",
        memory_type=MemoryType.SEMANTIC,
        agent_id="demo-agent",
        importance=9.0,
        tags=["personal", "birthday"]
    )
    print(f"✅ Added {len(memory_manager.get_all_memories())} sample memories")
    
    # Create MCP server
    print("🔧 Creating MCP server...")
    mcp_server = create_memory_mcp_server(memory_manager=memory_manager)
    
    # Run in stdio mode (for Claude Desktop and other MCP clients)
    print("🚀 Starting MCP server in stdio mode (for Claude Desktop)...")
    print("📋 To use with Claude Desktop, add this server to your config.")
    print("📋 Available tools:")
    print("   - search_memories: Search for memories using semantic search and filters")
    print("   - create_memory: Create new memory entries with metadata")
    print("   - get_memory_stats: Get statistics about stored memories")
    print("   - delete_memory: Delete specific memories by ID")
    print("   - update_memory: Update existing memory content and metadata")
    print()
    await mcp_server.run_stdio()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 MCP server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 