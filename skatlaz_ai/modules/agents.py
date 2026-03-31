"""
Agents Module - Swarm of specialized agents for different tasks
"""

import threading
import queue
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class Agent:
    """Base agent class"""
    
    def __init__(self, name: str, specialty: str, function: Callable):
        self.name = name
        self.specialty = specialty
        self.function = function
        self.task_count = 0
        self.success_rate = 1.0
        
    def execute(self, task: str) -> str:
        """Execute agent task"""
        self.task_count += 1
        try:
            result = self.function(task)
            return f"[{self.name}] {result}"
        except Exception as e:
            return f"[{self.name}] Error: {str(e)}"

class AgentSwarm:
    """Multi-agent system with task distribution"""
    
    def __init__(self):
        self.agents = []
        self.task_queue = queue.Queue()
        self.results = []
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize specialized agents"""
        # Research Agent
        self.agents.append(Agent(
            "Researcher",
            "research",
            lambda task: f"Researching: {task[:50]}... (simulated research results)"
        ))
        
        # Code Agent
        self.agents.append(Agent(
            "Coder",
            "programming",
            lambda task: f"Generating code for: {task[:50]}...\n\n```python\n# Generated code\ndef solution():\n    pass\n```"
        ))
        
        # Writer Agent
        self.agents.append(Agent(
            "Writer",
            "writing",
            lambda task: f"Writing content about: {task[:50]}...\n\nThis is a generated story based on your request."
        ))
        
        # Analyst Agent
        self.agents.append(Agent(
            "Analyst",
            "analysis",
            lambda task: f"Analyzing: {task[:50]}...\n\nKey insights and patterns identified."
        ))
        
        # Translator Agent
        self.agents.append(Agent(
            "Translator",
            "translation",
            lambda task: f"Translating: {task[:50]}...\n\n[Translated content would appear here]"
        ))
        
        # Search Agent
        self.agents.append(Agent(
            "Searcher",
            "search",
            lambda task: f"Searching for: {task[:50]}...\n\nTop results from web search would appear here."
        ))
        
        # Memory Agent
        self.agents.append(Agent(
            "Memory Keeper",
            "memory",
            lambda task: f"Accessing memory about: {task[:50]}...\n\nRelevant memories retrieved."
        ))
        
    def process(self, task: str, strategy: str = "parallel") -> str:
        """Process task with agent swarm"""
        
        # Determine which agents to use
        task_lower = task.lower()
        selected_agents = []
        
        # Smart agent selection
        if any(word in task_lower for word in ['code', 'program', 'script', 'function']):
            selected_agents.append(self.agents[1])  # Coder
            
        if any(word in task_lower for word in ['write', 'story', 'article', 'content']):
            selected_agents.append(self.agents[2])  # Writer
            
        if any(word in task_lower for word in ['analyze', 'analyze', 'insight', 'pattern']):
            selected_agents.append(self.agents[3])  # Analyst
            
        if any(word in task_lower for word in ['translate', 'language', 'idioma']):
            selected_agents.append(self.agents[4])  # Translator
            
        if any(word in task_lower for word in ['search', 'find', 'look', 'google']):
            selected_agents.append(self.agents[5])  # Searcher
            
        if any(word in task_lower for word in ['remember', 'recall', 'memory', 'recall']):
            selected_agents.append(self.agents[6])  # Memory Keeper
            
        # Always include researcher for complex tasks
        if len(selected_agents) > 1 or any(word in task_lower for word in ['research', 'investigate', 'deep']):
            selected_agents.insert(0, self.agents[0])
            
        if not selected_agents:
            selected_agents = [self.agents[0]]  # Default to researcher
        
        # Process with selected agents
        if strategy == "parallel":
            return self._parallel_process(task, selected_agents)
        else:
            return self._sequential_process(task, selected_agents)
    
    def _parallel_process(self, task: str, agents: List[Agent]) -> str:
        """Process with parallel execution"""
        results = []
        
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {executor.submit(agent.execute, task): agent for agent in agents}
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    results.append(f"Agent failed: {e}")
        
        response = "🤖 **Agent Swarm Results:**\n\n"
        for result in results:
            response += f"{result}\n\n"
            
        return response
    
    def _sequential_process(self, task: str, agents: List[Agent]) -> str:
        """Process with sequential execution"""
        response = "🤖 **Agent Swarm Results (Sequential):**\n\n"
        
        for agent in agents:
            result = agent.execute(task)
            response += f"{result}\n\n"
            time.sleep(0.5)  # Small delay between agents
            
        return response
    
    def add_agent(self, name: str, specialty: str, function: Callable):
        """Add custom agent"""
        self.agents.append(Agent(name, specialty, function))
