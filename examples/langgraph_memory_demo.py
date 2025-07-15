#!/usr/bin/env python3
"""
LangGraph Memory Integration Demo

This demo showcases the integration of Agent Memory OS with LangGraph,
demonstrating how to create memory-aware workflows and state machines.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path to import the SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_memory_sdk import (
    MemoryManager,
    MemoryGraph,
    MemoryState,
    MemoryToolNode,
    create_memory_tools,
    LANGGRAPH_AVAILABLE,
    MemoryType
)

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid


def demo_basic_memory_graph():
    """Demo 1: Basic memory graph with simple state management."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Memory Graph")
    print("="*60)
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create memory graph
    memory_graph = MemoryGraph(
        memory_manager=memory_manager,
        agent_id="demo_agent_1",
        session_id="session_1"
    )
    
    # Create a simple graph
    graph = memory_graph.create_graph()
    
    # Add a simple node that processes input
    def process_input(state):
        """Process input and store it as memory."""
        input_text = getattr(state, "input", "")
        
        # Store the input as memory
        memory_graph.memory_manager.add_memory(
            content=f"Processed input: {input_text}",
            memory_type=MemoryType.EPISODIC,
            agent_id=memory_graph.agent_id,
            session_id=memory_graph.session_id
        )
        
        # Return a dict of updated fields
        return {"output": f"Processed: {input_text}"}
    
    # Add the processing node
    graph.add_node("process", process_input)
    
    # Set up the workflow
    graph.set_entry_point("process")
    graph.add_edge("process", END)
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    # Run the graph
    print("Running basic memory graph...")
    result = compiled_graph.invoke({"input": "Hello, this is my first memory!"})
    print(f"Result: {result}")
    
    # Check memory
    memories = memory_graph.search_memories("first memory")
    print(f"Found memories: {memories}")
    
    # Get memory stats
    stats = memory_graph.get_memory_stats()
    print(f"Memory stats: {stats}")


def demo_memory_tools():
    """Demo 2: Using memory tools in a LangGraph workflow."""
    print("\n" + "="*60)
    print("DEMO 2: Memory Tools Integration")
    print("="*60)
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create memory tools
    memory_tools = create_memory_tools(
        memory_manager=memory_manager,
        agent_id="demo_agent_2",
        session_id="session_2"
    )
    
    # Create a tool node
    tool_node = ToolNode(memory_tools)
    
    # Create a simple graph
    graph = StateGraph(dict)
    
    # Add the tool node
    graph.add_node("tools", tool_node)
    
    # Set up the workflow
    graph.set_entry_point("tools")
    graph.add_edge("tools", END)
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    # Prepare a tool call for store_memory
    tool_call_id = str(uuid.uuid4())
    tool_call = {
        "name": "store_memory",
        "args": {
            "content": "I learned that Python is a great programming language",
            "memory_type": "semantic",
            "metadata": '{"category": "programming"}'
        },
        "id": tool_call_id,
        "type": "tool_call"
    }
    
    # Run the tool node with the correct message format
    print("Storing a memory...")
    state = {
        "messages": [
            HumanMessage(content="Store a memory about Python programming."),
            AIMessage(content="", tool_calls=[tool_call])
        ]
    }
    result1 = compiled_graph.invoke(state)
    print(f"Store result: {result1}")
    
    # Prepare a tool call for search_memories
    tool_call_id2 = str(uuid.uuid4())
    tool_call2 = {
        "name": "search_memories",
        "args": {
            "query": "Python programming",
            "limit": 3
        },
        "id": tool_call_id2,
        "type": "tool_call"
    }
    print("\nSearching memories...")
    state2 = {
        "messages": [
            HumanMessage(content="Search for memories about Python programming."),
            AIMessage(content="", tool_calls=[tool_call2])
        ]
    }
    result2 = compiled_graph.invoke(state2)
    print(f"Search result: {result2}")
    
    # Prepare a tool call for get_memory_stats
    tool_call_id3 = str(uuid.uuid4())
    tool_call3 = {
        "name": "get_memory_stats",
        "args": {},
        "id": tool_call_id3,
        "type": "tool_call"
    }
    print("\nGetting memory stats...")
    state3 = {
        "messages": [
            HumanMessage(content="Get memory stats."),
            AIMessage(content="", tool_calls=[tool_call3])
        ]
    }
    result3 = compiled_graph.invoke(state3)
    print(f"Stats result: {result3}")


def demo_agent_with_memory():
    """Demo 3: Creating an agent with memory capabilities."""
    print("\n" + "="*60)
    print("DEMO 3: Agent with Memory")
    print("="*60)
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create memory tools
    memory_tools = create_memory_tools(
        memory_manager=memory_manager,
        agent_id="demo_agent_3",
        session_id="session_3"
    )
    
    # Check for OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY is not set. Please set it to run this demo.")
        return
    
    # Use actual OpenAI LLM
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant with memory capabilities.
        
        You have access to memory tools that allow you to:
        - Store memories (episodic and semantic)
        - Search for relevant past information
        - Get timeline of recent activities
        - Learn and store facts
        
        Use these tools when appropriate to provide better, more contextual responses.
        Always try to learn from interactions and store useful information."""),
        ("human", "{input}")
    ])
    
    # Create a chain
    chain = prompt | llm
    
    # Create a graph
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("agent", chain)
    graph.add_node("tools", ToolNode(memory_tools))
    
    # Set up the workflow
    graph.set_entry_point("agent")
    graph.add_edge("agent", "tools")
    graph.add_edge("tools", END)
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    # Run the agent
    print("Running agent with memory...")
    
    # First interaction
    result1 = compiled_graph.invoke({
        "input": "Hello! Can you remember my name? I'm Alice."
    })
    print(f"Agent response: {result1}")
    
    # Second interaction
    result2 = compiled_graph.invoke({
        "input": "What's my name?"
    })
    print(f"Agent response: {result2}")
    
    # Check what was stored in memory
    memories = memory_manager.search_memory(
        query="Alice",
        agent_id="demo_agent_3"
    )
    print(f"\nMemories about Alice: {[m.content for m in memories]}")


def demo_memory_state():
    """Demo 4: Using memory state in complex workflows (dict-based state)."""
    print("\n" + "="*60)
    print("DEMO 4: Memory State in Workflows")
    print("="*60)
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    agent_id = "demo_agent_4"
    session_id = "session_4"
    
    # Create a graph with dict-based state
    graph = StateGraph(dict)
    
    # Add nodes
    def process_message(state: dict) -> dict:
        """Process a message and store it in memory."""
        message = state.get("message", "")
        conversation_history = state.get("conversation_history", [])
        user_preferences = state.get("user_preferences", {})
        
        # Store the message
        memory_manager.add_memory(
            content=f"User said: {message}",
            memory_type=MemoryType.EPISODIC,
            agent_id=agent_id,
            session_id=session_id
        )
        
        # Add to conversation history
        conversation_history.append(message)
        
        # Generate response (simplified)
        response = f"I heard you say: {message}"
        
        # Store the response
        memory_manager.add_memory(
            content=f"Assistant responded: {response}",
            memory_type=MemoryType.EPISODIC,
            agent_id=agent_id,
            session_id=session_id
        )
        
        return {
            "response": response,
            "conversation_history": conversation_history,
            "user_preferences": user_preferences
        }
    
    def analyze_preferences(state: dict) -> dict:
        """Analyze user preferences from conversation history."""
        conversation_history = state.get("conversation_history", [])
        user_preferences = state.get("user_preferences", {})
        
        # Search for preference-related memories
        preferences = memory_manager.search_memory(
            query="prefer like want need",
            limit=5
        )
        # Filter to only include memories for this agent
        preference_contents = [m.content for m in preferences if m.agent_id == agent_id]
        if preference_contents:
            user_preferences["extracted"] = preference_contents
            memory_manager.add_memory(
                content=f"User preferences extracted: {', '.join(preference_contents)}",
                memory_type=MemoryType.SEMANTIC,
                agent_id=agent_id,
                session_id=session_id,
                metadata={"category": "user_preferences"}
            )
        return {
            "user_preferences": user_preferences
        }
    
    # Add nodes to graph
    graph.add_node("process", process_message)
    graph.add_node("analyze", analyze_preferences)
    
    # Set up workflow
    graph.set_entry_point("process")
    graph.add_edge("process", "analyze")
    graph.add_edge("analyze", END)
    
    # Compile graph
    compiled_graph = graph.compile()
    
    # Run the workflow
    print("Running conversation workflow...")
    
    # First message
    result1 = compiled_graph.invoke({
        "message": "I prefer dark chocolate over milk chocolate",
        "conversation_history": [],
        "user_preferences": {}
    })
    print(f"Response: {result1.get('response')}")
    
    # Second message
    result2 = compiled_graph.invoke({
        "message": "I also like coffee in the morning",
        "conversation_history": result1.get("conversation_history", []),
        "user_preferences": result1.get("user_preferences", {})
    })
    print(f"Response: {result2.get('response')}")
    
    # Check preferences
    print(f"Extracted preferences: {result2.get('user_preferences')}")
    
    # Get memory stats
    stats = memory_manager.get_episodic_memories(agent_id=agent_id, limit=1000)
    print(f"Memory stats: {{'episodic_memories': {len(stats)}}}")


def main():
    """Run all demos."""
    if not LANGGRAPH_AVAILABLE:
        print("LangGraph is not available. Please install it with: pip install langgraph")
        return
    
    print("Agent Memory OS - LangGraph Integration Demo")
    print("="*60)
    
    try:
        # Run all demos
        demo_basic_memory_graph()
        demo_memory_tools()
        demo_agent_with_memory()
        demo_memory_state()
        
        print("\n" + "="*60)
        print("All demos completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 