from abc import ABC, abstractmethod
from typing import Optional
from ..models.openrouter import OpenRouterClient

class BaseAgent(ABC):
    def __init__(self, model: str):
        """
        Initialize a base agent.
        
        Args:
            model: The model identifier to use for this agent
        """
        self.model = model
        self.client = OpenRouterClient()

    @abstractmethod
    async def solve(self, problem: str) -> Optional[str]:
        """
        Solve the given problem.
        
        Args:
            problem: The problem to solve
            
        Returns:
            The solution or None if unable to solve
        """
        pass
