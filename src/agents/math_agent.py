from typing import Optional
from .base_agent import BaseAgent

class MathAgent(BaseAgent):
    async def solve(self, problem: str) -> Optional[str]:
        """
        Solve a math problem using the specified model.
        
        Args:
            problem: The math problem to solve
            
        Returns:
            Raw solution text or None if solving fails
        """
        try:
            prompt = self.client.create_math_prompt(problem)
            response = await self.client.generate_response(self.model, prompt)
            
            if not response:
                print(f"No response received from {self.model}")
                return None
                
            if len(response.strip()) == 0:
                print(f"Empty response received from {self.model}")
                return None
                
            return f'{{"model": "{self.model}", "solution": """{response}"""}}'
        except Exception as e:
            print(f"Error in {self.model} agent: {str(e)}")
            return None
