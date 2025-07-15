"""
CrewAI Memory Demo

Demonstrates how to integrate Agent Memory OS with CrewAI agents
to provide persistent memory across sessions.
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our SDK
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_memory_sdk import MemoryManager, MemoryEntry, MemoryType


class MemoryAwareAgent:
    """Example agent class that uses Agent Memory OS"""
    
    def __init__(self, agent_id: str, memory_manager: MemoryManager):
        """
        Initialize agent with memory capabilities
        
        Args:
            agent_id: Unique identifier for this agent
            memory_manager: Memory manager instance
        """
        self.agent_id = agent_id
        self.memory_manager = memory_manager
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def process_task(self, task: str) -> str:
        """
        Process a task and store relevant memories
        
        Args:
            task: Task description or input
            
        Returns:
            Response to the task
        """
        # Store the task as episodic memory
        self.memory_manager.add_memory(
            content=f"Received task: {task}",
            memory_type=MemoryType.EPISODIC,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata={"task_type": "user_input"}
        )
        
        # Search for relevant past memories
        relevant_memories = self.memory_manager.search_memory(
            query=task,
            limit=5
        )
        
        # Build context from relevant memories
        context = self._build_context(relevant_memories)
        
        # Generate response (simplified for demo)
        response = self._generate_response(task, context)
        
        # Store the response as episodic memory
        self.memory_manager.add_memory(
            content=f"Generated response: {response}",
            memory_type=MemoryType.EPISODIC,
            agent_id=self.agent_id,
            session_id=self.session_id,
            metadata={"task_type": "response", "original_task": task}
        )
        
        return response
    
    def learn_fact(self, fact: str, category: str = "general"):
        """
        Learn and store a new fact as semantic memory
        
        Args:
            fact: Fact to learn
            category: Category of the fact
        """
        self.memory_manager.add_memory(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            agent_id=self.agent_id,
            metadata={"category": category, "learned_at": datetime.now().isoformat()}
        )
        print(f"Learned fact: {fact}")
    
    def get_timeline(self, hours: int = 24) -> list:
        """
        Get recent timeline of activities
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent memories
        """
        from datetime import timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        return self.memory_manager.get_timeline(
            agent_id=self.agent_id,
            start_time=start_time,
            end_time=end_time
        )
    
    def _build_context(self, memories: list) -> str:
        """Build context string from relevant memories"""
        if not memories:
            return "No relevant past context found."
        
        context_parts = ["Relevant past context:"]
        for memory in memories:
            context_parts.append(f"- {memory.content} ({memory.timestamp.strftime('%Y-%m-%d %H:%M')})")
        
        return "\n".join(context_parts)
    
    def _generate_response(self, task: str, context: str) -> str:
        """Generate response based on task and context"""
        # This is a simplified response generator
        # In a real implementation, this would use an LLM
        
        if "hello" in task.lower():
            return f"Hello! I'm agent {self.agent_id}. I have access to my memory and can help you with tasks."
        elif "remember" in task.lower():
            return f"I can remember things! Here's some context from my memory:\n{context}"
        elif "timeline" in task.lower():
            timeline = self.get_timeline()
            if timeline:
                return f"Here's my recent timeline:\n" + "\n".join([
                    f"- {m.content} ({m.timestamp.strftime('%H:%M')})" 
                    for m in timeline[:5]
                ])
            else:
                return "No recent activities in my timeline."
        else:
            return f"I processed your task: '{task}'. I have access to my memory and can learn from our interactions."


def demo_basic_memory():
    """Demonstrate basic memory functionality"""
    print("=== Agent Memory OS Demo ===\n")
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    
    # Create an agent with memory
    agent = MemoryAwareAgent("demo_agent", memory_manager)
    
    # Learn some facts
    print("Learning some facts...")
    agent.learn_fact("The user prefers to work in the morning", "preferences")
    agent.learn_fact("Python is the primary programming language used", "technical")
    agent.learn_fact("The project is called Agent Memory OS", "project")
    
    print("\n" + "="*50 + "\n")
    
    # Simulate some interactions
    print("Simulating agent interactions...")
    
    responses = [
        agent.process_task("Hello, can you help me?"),
        agent.process_task("What do you remember about me?"),
        agent.process_task("Show me your recent timeline"),
        agent.process_task("What programming language do I use?"),
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"Interaction {i}:")
        print(f"Response: {response}")
        print("-" * 30)
    
    print("\n" + "="*50 + "\n")
    
    # Demonstrate memory persistence across sessions
    print("Creating a new agent session to demonstrate memory persistence...")
    new_agent = MemoryAwareAgent("demo_agent", memory_manager)  # Same agent_id, different session
    
    response = new_agent.process_task("What do you know about the project?")
    print(f"New session response: {response}")


def demo_crewai_integration():
    """Demonstrate how this would integrate with CrewAI"""
    print("\n" + "="*50)
    print("CrewAI Integration Example")
    print("="*50)
    
    # This shows how you would integrate with CrewAI agents
    print("""
# Example CrewAI integration:

from crewai import Agent, Task, Crew
from agent_memory_sdk import MemoryManager

# Initialize memory manager
memory_manager = MemoryManager()

# Create agents with memory
researcher = Agent(
    role='Research Analyst',
    goal='Conduct thorough research on given topics',
    backstory='You are an expert researcher with access to persistent memory.',
    memory_manager=memory_manager,  # Pass memory manager to agent
    agent_id='researcher_001'
)

writer = Agent(
    role='Content Writer',
    goal='Write engaging content based on research',
    backstory='You are a skilled writer who remembers past writing styles.',
    memory_manager=memory_manager,  # Same memory manager for shared context
    agent_id='writer_001'
)

# Create tasks
research_task = Task(
    description='Research the latest AI trends',
    agent=researcher
)

writing_task = Task(
    description='Write a blog post about AI trends',
    agent=writer
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    memory_manager=memory_manager  # Crew-level memory management
)

# Execute with persistent memory
result = crew.kickoff()
    """)


if __name__ == "__main__":
    demo_basic_memory()
    demo_crewai_integration() 