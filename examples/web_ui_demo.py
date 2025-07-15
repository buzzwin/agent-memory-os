#!/usr/bin/env python3
"""
Web UI Demo for Agent Memory OS

This demo:
1. Creates sample memories for demonstration
2. Launches the web UI server
3. Opens the browser to the web interface
"""

import time
import webbrowser
import subprocess
import sys
from pathlib import Path

from agent_memory_sdk import MemoryManager, MemoryType


def create_sample_data():
    """Create sample memories for the web UI demo"""
    print("🧠 Creating sample memory data...")
    
    memory_manager = MemoryManager()
    
    # Sample episodic memories
    episodic_memories = [
        {
            "content": "User asked about Python programming and showed interest in data science",
            "agent_id": "assistant_agent",
            "importance": 8.5,
            "tags": ["python", "data-science", "user-preference"]
        },
        {
            "content": "User created a new project called 'agent-memory-os' and started development",
            "agent_id": "assistant_agent", 
            "importance": 9.0,
            "tags": ["project", "development", "memory-system"]
        },
        {
            "content": "User requested help with LangChain integration and memory persistence",
            "agent_id": "assistant_agent",
            "importance": 7.5,
            "tags": ["langchain", "integration", "memory"]
        }
    ]
    
    # Sample semantic memories
    semantic_memories = [
        {
            "content": "User prefers dark mode interfaces and modern UI design",
            "agent_id": "assistant_agent",
            "importance": 6.0,
            "tags": ["ui", "preferences", "dark-mode"]
        },
        {
            "content": "User is experienced with Python, JavaScript, and web development",
            "agent_id": "assistant_agent",
            "importance": 8.0,
            "tags": ["skills", "programming", "web-dev"]
        },
        {
            "content": "User works on AI/ML projects and is interested in agent systems",
            "agent_id": "assistant_agent",
            "importance": 9.5,
            "tags": ["ai", "ml", "agents", "interests"]
        }
    ]
    
    # Sample temporal memories
    temporal_memories = [
        {
            "content": "Project started on 2024-01-15 with initial memory system implementation",
            "agent_id": "project_tracker",
            "importance": 7.0,
            "tags": ["timeline", "project-start", "milestone"]
        },
        {
            "content": "LangChain integration completed on 2024-01-20",
            "agent_id": "project_tracker",
            "importance": 8.5,
            "tags": ["timeline", "langchain", "integration"]
        },
        {
            "content": "REST API implementation finished on 2024-01-25",
            "agent_id": "project_tracker",
            "importance": 8.0,
            "tags": ["timeline", "api", "rest"]
        }
    ]
    
    # Create memories
    for memory in episodic_memories:
        memory_manager.add_memory(
            content=memory["content"],
            memory_type=MemoryType.EPISODIC,
            agent_id=memory["agent_id"],
            importance=memory["importance"],
            tags=memory["tags"]
        )
    
    for memory in semantic_memories:
        memory_manager.add_memory(
            content=memory["content"],
            memory_type=MemoryType.SEMANTIC,
            agent_id=memory["agent_id"],
            importance=memory["importance"],
            tags=memory["tags"]
        )
    
    for memory in temporal_memories:
        memory_manager.add_memory(
            content=memory["content"],
            memory_type=MemoryType.TEMPORAL,
            agent_id=memory["agent_id"],
            importance=memory["importance"],
            tags=memory["tags"]
        )
    
    # Add some memories from different agents
    other_agents = [
        ("research_agent", "Found relevant papers on memory systems for AI agents"),
        ("code_review_agent", "Reviewed memory persistence implementation and suggested improvements"),
        ("documentation_agent", "Updated README with new REST API and web UI features")
    ]
    
    for agent_id, content in other_agents:
        memory_manager.add_memory(
            content=content,
            memory_type=MemoryType.EPISODIC,
            agent_id=agent_id,
            importance=6.5,
            tags=["collaboration", "multi-agent"]
        )
    
    total_memories = len(episodic_memories) + len(semantic_memories) + len(temporal_memories) + len(other_agents)
    print(f"✅ Created {total_memories} sample memories")
    print(f"   - {len(episodic_memories)} episodic memories")
    print(f"   - {len(semantic_memories)} semantic memories") 
    print(f"   - {len(temporal_memories)} temporal memories")
    print(f"   - {len(other_agents)} other agent memories")


def launch_web_ui():
    """Launch the web UI server"""
    print("\n🚀 Launching Web UI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    print("\n💡 Features to try:")
    print("   - Browse and search memories")
    print("   - Filter by type, agent, and importance")
    print("   - Click on memories to see details")
    print("   - Create new memories using the + button")
    print("   - View statistics and agent breakdowns")
    print("\n⏳ Opening browser in 3 seconds...")
    
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:8000")
        print("✅ Browser opened successfully!")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually navigate to: http://localhost:8000")
    
    print("\n🔄 Server is running. Press Ctrl+C to stop.")
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "run_api.py", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web UI demo stopped.")


def main():
    """Main demo function"""
    print("🎨 Agent Memory OS - Web UI Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("run_api.py").exists():
        print("❌ Error: run_api.py not found!")
        print("   Please run this script from the project root directory.")
        return
    
    # Create sample data
    create_sample_data()
    
    # Launch web UI
    launch_web_ui()


if __name__ == "__main__":
    main() 