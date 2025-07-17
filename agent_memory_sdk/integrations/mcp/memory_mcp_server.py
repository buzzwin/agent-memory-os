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

    async def run(self, host: str = "localhost", port: int = 8001):
        await self.server.run(host=host, port=port)

    def run_stdio(self):
        asyncio.run(self.server.run_stdio())

def create_memory_mcp_server(memory_manager: Optional[MemoryManager] = None, **kwargs) -> MemoryMCPServer:
    return MemoryMCPServer(memory_manager=memory_manager, **kwargs) 