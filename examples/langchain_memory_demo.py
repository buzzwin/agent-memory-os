"""
LangChain Memory Integration Demo

Demonstrates how to integrate Agent Memory OS with LangChain agents,
chains, and tools for persistent memory capabilities.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our SDK
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_memory_sdk import MemoryManager, MemoryType, LANGCHAIN_AVAILABLE

if not LANGCHAIN_AVAILABLE:
    print("LangChain integration not available. Please install langchain: pip install langchain")
    sys.exit(1)

from agent_memory_sdk import (
    MemoryChain,
    MemoryTool,
    MemoryCallbackHandler,
    MemoryAwareAgent
)


def demo_memory_chain():
    """Demonstrate MemoryChain integration"""
    print("=== MemoryChain Demo ===\n")
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create a simple LLM (you can replace this with any LangChain LLM)
    from langchain_community.llms.fake import FakeListLLM
    
    llm = FakeListLLM(responses=[
        "Hello! I remember you prefer Python programming.",
        "Based on our previous conversations, I know you're working on Agent Memory OS.",
        "I recall you asked about memory persistence earlier.",
        "Yes, I can help you with that! I remember you're interested in AI agents."
    ])
    
    # Create memory chain
    memory_chain = MemoryChain(
        memory_manager=memory_manager,
        llm=llm,
        agent_id="demo_chain",
        retrieve_memories=True,
        memory_limit=3
    )
    
    # Learn some facts first
    print("Learning some facts...")
    memory_chain.learn_fact("The user prefers Python programming", "preferences")
    memory_chain.learn_fact("The user is working on Agent Memory OS project", "project")
    memory_chain.learn_fact("The user is interested in AI agents and memory systems", "interests")
    
    print("\n" + "="*50 + "\n")
    
    # Test the chain with different inputs
    test_inputs = [
        "Hello, can you help me?",
        "What do you know about my project?",
        "Do you remember our previous conversation?",
        "What programming language do I use?"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i}: {user_input}")
        result = memory_chain.invoke({"input": user_input})
        print(f"Output: {result['output']}")
        print(f"Memories used: {len(result['memories_used'])}")
        print("-" * 30)
    
    print("\n" + "="*50 + "\n")
    
    # Show timeline
    print("Recent timeline:")
    timeline = memory_chain.get_timeline(hours=1)
    for memory in timeline[:5]:
        print(f"- {memory}")


def demo_memory_tool():
    """Demonstrate MemoryTool integration"""
    print("\n=== MemoryTool Demo ===\n")
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create memory tool
    memory_tool = MemoryTool(
        memory_manager=memory_manager,
        agent_id="demo_tool"
    )
    
    # Test different tool operations
    operations = [
        "learn_fact: The user is testing memory tools | testing",
        "learn_fact: Memory tools are useful for agents",
        "search_memories: testing",
        "get_timeline: 1",
        "store_memory: User tested memory tool functionality"
    ]
    
    for operation in operations:
        print(f"Operation: {operation}")
        result = memory_tool.run(operation)
        print(f"Result: {result}")
        print("-" * 30)


def demo_memory_callback():
    """Demonstrate MemoryCallbackHandler integration"""
    print("\n=== MemoryCallbackHandler Demo ===\n")
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create memory callback handler
    memory_callback = MemoryCallbackHandler(
        memory_manager=memory_manager,
        agent_id="demo_callback",
        store_llm_inputs=True,
        store_llm_outputs=True,
        store_agent_actions=True
    )
    
    # Create a simple chain to demonstrate callbacks
    from langchain.chains import LLMChain
    from langchain_core.prompts import PromptTemplate
    from langchain_community.llms.fake import FakeListLLM
    
    llm = FakeListLLM(responses=["I'm a helpful AI assistant!"])
    
    template = "You are a helpful assistant. User says: {input}"
    prompt = PromptTemplate(template=template, input_variables=["input"])
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        callbacks=[memory_callback]
    )
    
    # Run the chain
    print("Running chain with memory callbacks...")
    result = chain.run("Hello, how are you?")
    print(f"Chain result: {result}")
    
    # Show what was stored in memory
    print("\nMemories stored by callback handler:")
    timeline = memory_manager.get_timeline(agent_id="demo_callback")
    for memory in timeline:
        print(f"- {memory.content} ({memory.metadata.get('event_type', 'unknown')})")


def demo_memory_aware_agent():
    """Demonstrate MemoryAwareAgent integration with a simpler LLMChain approach"""
    print("\n=== MemoryAwareAgent Demo (Simple LLMChain Pattern) ===\n")
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create a simple LLM
    from langchain_community.llms.fake import FakeListLLM
    
    llm = FakeListLLM(responses=[
        "I remember you asked about this before!",
        "Based on our previous conversation, I can help you with that.",
        "Yes, I recall discussing this topic earlier.",
        "I remember you prefer Python programming."
    ])
    
    # Create a simple prompt template
    from langchain_core.prompts import PromptTemplate
    
    prompt = PromptTemplate(
        input_variables=["input", "memory_context"],
        template="""You are a helpful AI assistant with access to memory.

Previous relevant context:
{memory_context}

User question: {input}

Please provide a helpful response that takes into account the memory context when relevant."""
    )
    
    # Create a simple chain
    from langchain.chains import LLMChain
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Create memory-aware agent wrapper (using the chain as the "agent")
    memory_agent = MemoryAwareAgent(
        agent=chain,
        memory_manager=memory_manager,
        agent_id="demo_agent_simple",
        include_memory_tool=False,  # Disable memory tool for simplicity
        enable_memory_callbacks=True
    )
    
    # Learn some facts
    print("Teaching the agent some facts...")
    memory_agent.learn_fact("The user is testing simple memory-aware agents", "testing")
    memory_agent.learn_fact("The user prefers Python over JavaScript", "preferences")
    
    print("\n" + "="*50 + "\n")
    
    # Test the agent with simple queries
    test_queries = [
        "What do you remember about me?",
        "What programming language do I prefer?",
        "Can you tell me about our previous conversation?",
        "What facts have you learned about me?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        try:
            result = memory_agent.run(query)
            print(f"Output: {result['output']}")
            print(f"Memories used: {len(result['memories_used'])}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 30)
    
    # Show memory stats
    print("\nMemory statistics:")
    stats = memory_agent.get_memory_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


def demo_integration_workflow():
    """Demonstrate a complete workflow using all integration components"""
    print("\n=== Complete Integration Workflow Demo ===\n")
    
    # Initialize shared memory manager
    memory_manager = MemoryManager()
    
    # Create a simple LLM
    from langchain_community.llms.fake import FakeListLLM
    
    llm = FakeListLLM(responses=[
        "I can help you with that! I remember you're working on memory systems.",
        "Based on our previous conversations, I know you're interested in AI agents.",
        "Yes, I recall discussing this. Let me help you with that.",
        "I remember you asked about this before. Here's what I can tell you."
    ])
    
    # Create memory chain
    memory_chain = MemoryChain(
        memory_manager=memory_manager,
        llm=llm,
        agent_id="workflow_agent",
        retrieve_memories=True
    )
    
    # Learn initial facts
    print("Setting up initial knowledge...")
    memory_chain.learn_fact("The user is building an AI memory system", "project")
    memory_chain.learn_fact("The user prefers Python for development", "preferences")
    memory_chain.learn_fact("The user is interested in LangChain integration", "interests")
    
    print("\n" + "="*50 + "\n")
    
    # Simulate a conversation workflow
    conversation = [
        "What project am I working on?",
        "What programming language do I prefer?",
        "Can you help me with LangChain integration?",
        "What do you remember about our conversation so far?"
    ]
    
    print("Simulating conversation with memory...")
    for i, message in enumerate(conversation, 1):
        print(f"\nUser {i}: {message}")
        result = memory_chain.invoke({"input": message})
        print(f"Assistant: {result['output']}")
        
        if result['memories_used']:
            print(f"Memories used: {len(result['memories_used'])}")
    
    print("\n" + "="*50 + "\n")
    
    # Show final timeline
    print("Complete conversation timeline:")
    timeline = memory_chain.get_timeline(hours=1)
    for memory in timeline:
        print(f"- {memory}")


if __name__ == "__main__":
    print("LangChain Memory Integration Demo")
    print("=" * 50)
    
    try:
        # Run all demos
        demo_memory_chain()
        demo_memory_tool()
        demo_memory_callback()
        demo_memory_aware_agent()
        demo_integration_workflow()
        
        print("\n" + "="*50)
        print("All demos completed successfully!")
        print("The LangChain integration is working properly.")
        
    except Exception as e:
        print(f"Error running demo: {e}")
        print("Make sure you have LangChain installed: pip install langchain") 