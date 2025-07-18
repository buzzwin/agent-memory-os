"""
MCP (Model Context Protocol) Server for Agent Memory OS

Implements the Model Context Protocol to expose memory capabilities
to MCP-compatible clients like Claude Desktop and other AI assistants.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        CallToolRequest,
        CallToolResult,
        ListResourcesRequest,
        ListResourcesResult,
        ReadResourceRequest,
        ReadResourceResult,
        ListToolsRequest,
        ListToolsResult,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ Warning: MCP SDK not available. Install with: pip install mcp>=1.0")

from ...memory import MemoryManager
from ...models import MemoryType

class MemoryMCPServer:
    """
    MCP server that exposes Agent Memory OS capabilities through the Model Context Protocol.
    """
    def __init__(self, memory_manager: Optional[MemoryManager] = None, server_name: str = "agent-memory-os", server_version: str = "1.0.0", **memory_kwargs):
        if not MCP_AVAILABLE:
            raise ImportError("MCP SDK not available. Install with: pip install mcp>=1.0")
        self.memory_manager = memory_manager or MemoryManager(**memory_kwargs)
        self.server = Server(server_name, server_version)
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_resources()
        async def handle_list_resources(request: ListResourcesRequest) -> ListResourcesResult:
            resources = []
            memories = self.memory_manager.get_all_memories()
            for memory in memories:
                resource = Resource(
                    uri=f"memory://{memory.id}",
                    name=f"Memory: {memory.content[:40]}...",
                    description=f"{memory.memory_type.value} memory from {memory.agent_id or 'unknown'}",
                    mimeType="text/plain",
                    metadata={
                        "memory_type": memory.memory_type.value,
                        "agent_id": memory.agent_id,
                        "importance": memory.importance,
                        "tags": memory.tags,
                        "created_at": memory.timestamp.isoformat(),
                    }
                )
                resources.append(resource)
            # Add a summary resource
            stats = self.memory_manager.get_memory_stats()
            summary_resource = Resource(
                uri="memory://summary",
                name="Memory Summary",
                description="Overview of all stored memories",
                mimeType="application/json",
                metadata={"type": "summary"}
            )
            resources.append(summary_resource)
            return ListResourcesResult(resources=resources)

        @self.server.read_resource()
        async def handle_read_resource(request: ReadResourceRequest) -> ReadResourceResult:
            uri = request.uri
            if uri == "memory://summary":
                stats = self.memory_manager.get_memory_stats()
                content = TextContent(type="text", text=json.dumps(stats, indent=2))
                return ReadResourceResult(contents=[content])
            elif uri.startswith("memory://"):
                memory_id = uri.replace("memory://", "")
                memory = self.memory_manager.get_memory(memory_id)
                if not memory:
                    raise ValueError(f"Memory not found: {memory_id}")
                memory_data = memory.to_dict()
                content = TextContent(type="text", text=json.dumps(memory_data, indent=2))
                return ReadResourceResult(contents=[content])
            else:
                raise ValueError(f"Unsupported resource URI: {uri}")

        @self.server.list_tools()
        async def handle_list_tools(request: ListToolsRequest) -> ListToolsResult:
            tools = [
                Tool(
                    name="search_memories",
                    description="Search for memories using semantic search and filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for semantic search"},
                            "memory_type": {"type": "string", "enum": ["episodic", "semantic", "temporal"], "description": "Filter by memory type"},
                            "agent_id": {"type": "string", "description": "Filter by agent ID"},
                            "limit": {"type": "integer", "description": "Maximum number of results (default: 10)"},
                            "min_importance": {"type": "number", "description": "Minimum importance score (0-10)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        },
                    },
                ),
                Tool(
                    name="create_memory",
                    description="Create a new memory entry",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Memory content"},
                            "memory_type": {"type": "string", "enum": ["episodic", "semantic", "temporal"], "description": "Type of memory"},
                            "agent_id": {"type": "string", "description": "Agent ID associated with this memory"},
                            "importance": {"type": "number", "description": "Importance score (0-10)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorization"},
                            "metadata": {"type": "object", "description": "Additional metadata"},
                        },
                        "required": ["content", "memory_type"]
                    },
                ),
                Tool(
                    name="get_memory_stats",
                    description="Get statistics about stored memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_type": {"type": "string", "enum": ["episodic", "semantic", "temporal"], "description": "Filter by memory type"},
                            "agent_id": {"type": "string", "description": "Filter by agent ID"},
                        },
                    },
                ),
                Tool(
                    name="delete_memory",
                    description="Delete a specific memory by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "ID of the memory to delete"},
                        },
                        "required": ["memory_id"]
                    },
                ),
                Tool(
                    name="update_memory",
                    description="Update an existing memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "ID of the memory to update"},
                            "content": {"type": "string", "description": "New memory content"},
                            "importance": {"type": "number", "description": "New importance score (0-10)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags"},
                            "metadata": {"type": "object", "description": "New metadata"},
                        },
                        "required": ["memory_id"]
                    },
                ),
            ]
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            tool_name = request.name
            arguments = request.arguments or {}
            try:
                if tool_name == "search_memories":
                    result = await self._search_memories(arguments)
                elif tool_name == "create_memory":
                    result = await self._create_memory(arguments)
                elif tool_name == "get_memory_stats":
                    result = await self._get_memory_stats(arguments)
                elif tool_name == "delete_memory":
                    result = await self._delete_memory(arguments)
                elif tool_name == "update_memory":
                    result = await self._update_memory(arguments)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
            except Exception as e:
                return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")], isError=True)

    async def _search_memories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query", "")
        memory_type = args.get("memory_type")
        agent_id = args.get("agent_id")
        limit = args.get("limit", 10)
        min_importance = args.get("min_importance")
        tags = args.get("tags", [])
        memory_type_enum = None
        if memory_type:
            memory_type_enum = MemoryType(memory_type)
        memories = self.memory_manager.search_memory(
            query=query,
            memory_type=memory_type_enum,
            agent_id=agent_id,
            limit=limit,
            min_importance=min_importance,
        )
        if tags:
            memories = [m for m in memories if m.tags and any(tag in m.tags for tag in tags)]
        return {
            "memories": [m.to_dict() for m in memories],
            "total_count": len(memories),
            "query": query,
            "filters": {
                "memory_type": memory_type,
                "agent_id": agent_id,
                "min_importance": min_importance,
                "tags": tags,
            },
        }

    async def _create_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        content = args["content"]
        memory_type = MemoryType(args["memory_type"])
        agent_id = args.get("agent_id")
        importance = args.get("importance", 5.0)
        tags = args.get("tags", [])
        metadata = args.get("metadata", {})
        memory = self.memory_manager.add_memory(
            content=content,
            memory_type=memory_type,
            agent_id=agent_id,
            importance=importance,
            tags=tags,
            metadata=metadata,
        )
        return {
            "success": True,
            "memory": memory.to_dict(),
            "message": "Memory created successfully"
        }

    async def _get_memory_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        memory_type = args.get("memory_type")
        agent_id = args.get("agent_id")
        memory_type_enum = None
        if memory_type:
            memory_type_enum = MemoryType(memory_type)
        
        stats = self.memory_manager.get_memory_stats()
        
        # Filter stats if needed
        if memory_type_enum or agent_id:
            memories = self.memory_manager.get_all_memories()
            if memory_type_enum:
                memories = [m for m in memories if m.memory_type == memory_type_enum]
            if agent_id:
                memories = [m for m in memories if m.agent_id == agent_id]
            
            stats = {
                "total_memories": len(memories),
                "memory_types": {},
                "agents": {},
                "importance_distribution": {"low": 0, "medium": 0, "high": 0},
                "recent_activity": {}
            }
            
            for memory in memories:
                # Count by memory type
                mem_type = memory.memory_type.value
                stats["memory_types"][mem_type] = stats["memory_types"].get(mem_type, 0) + 1
                
                # Count by agent
                agent = memory.agent_id or "unknown"
                stats["agents"][agent] = stats["agents"].get(agent, 0) + 1
                
                # Count by importance
                if memory.importance < 3:
                    stats["importance_distribution"]["low"] += 1
                elif memory.importance < 7:
                    stats["importance_distribution"]["medium"] += 1
                else:
                    stats["importance_distribution"]["high"] += 1
        
        return {
            "stats": stats,
            "filters": {
                "memory_type": memory_type,
                "agent_id": agent_id,
            }
        }

    async def _delete_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = args["memory_id"]
        success = self.memory_manager.delete_memory(memory_id)
        if success:
            return {
                "success": True,
                "message": f"Memory {memory_id} deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Memory {memory_id} not found or could not be deleted"
            }

    async def _update_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = args["memory_id"]
        content = args.get("content")
        importance = args.get("importance")
        tags = args.get("tags")
        metadata = args.get("metadata")
        
        # Get existing memory
        memory = self.memory_manager.get_memory(memory_id)
        if not memory:
            return {
                "success": False,
                "message": f"Memory {memory_id} not found"
            }
        
        # Update fields if provided
        if content is not None:
            memory.content = content
        if importance is not None:
            memory.importance = importance
        if tags is not None:
            memory.tags = tags
        if metadata is not None:
            memory.metadata = metadata
        
        # Save the updated memory
        success = self.memory_manager.update_memory(memory)
        if success:
            return {
                "success": True,
                "memory": memory.to_dict(),
                "message": f"Memory {memory_id} updated successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update memory {memory_id}"
            }

    async def run(self, host: str = "localhost", port: int = 8001):
        """Run the MCP server as an HTTP server (not supported in current MCP SDK)"""
        raise NotImplementedError("HTTP mode not yet supported. Use stdio mode for MCP clients.")

    async def run_stdio(self):
        """Run the MCP server in stdio mode (for Claude Desktop and other MCP clients)"""
        from mcp import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, {})

def create_memory_mcp_server(memory_manager: Optional[MemoryManager] = None, **kwargs) -> MemoryMCPServer:
    return MemoryMCPServer(memory_manager=memory_manager, **kwargs)

def main():
    """CLI entry point for the MCP server"""
    import argparse
    import sys
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Agent Memory OS MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run in stdio mode (for Claude Desktop) - this is the default and only mode")
    parser.add_argument("--store-type", default="sqlite", choices=["sqlite", "pinecone", "postgresql"], 
                       help="Storage backend type (default: sqlite)")
    parser.add_argument("--db-path", default="agent_memory.db", help="SQLite database path (default: agent_memory.db)")
    parser.add_argument("--api-key", help="Pinecone API key (for Pinecone store)")
    parser.add_argument("--environment", help="Pinecone environment (for Pinecone store)")
    parser.add_argument("--index-name", default="agent-memory-os", help="Pinecone index name (default: agent-memory-os)")
    parser.add_argument("--connection-string", help="PostgreSQL connection string")
    
    args = parser.parse_args()
    
    try:
        # Initialize memory manager with specified configuration
        memory_kwargs = {"store_type": args.store_type}
        
        if args.store_type == "sqlite":
            memory_kwargs["db_path"] = args.db_path
        elif args.store_type == "pinecone":
            memory_kwargs["api_key"] = args.api_key
            memory_kwargs["environment"] = args.environment
            memory_kwargs["index_name"] = args.index_name
        elif args.store_type == "postgresql":
            memory_kwargs["connection_string"] = args.connection_string
        
        # Create MCP server
        mcp_server = create_memory_mcp_server(**memory_kwargs)
        
        print("🚀 Starting Agent Memory OS MCP Server in stdio mode...", file=sys.stderr)
        asyncio.run(mcp_server.run_stdio())
            
    except KeyboardInterrupt:
        print("\n👋 MCP server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 