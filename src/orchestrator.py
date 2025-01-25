import asyncio
from typing import List, Dict, Any
from .agents.math_agent import MathAgent
from .agents.consistency_agent import ConsistencyAgent
from .summarizer import Summarizer
from .config import settings

class Orchestrator:
    def __init__(self):
        """Initialize the orchestrator with agents."""
        self.agents = {
            "o1": MathAgent(model="o1"),      # GPT-4
            "gemini": MathAgent(model="gemini"),  # Gemini Pro
            "deepseek": MathAgent(model="deepseek") # Deepseek
        }
        self.consistency_agent = ConsistencyAgent()
        self.summarizer = Summarizer()
        self.runs_per_model = 3  # Number of times to run each model

    async def solve_problem(self, problem: str) -> Dict[str, Any]:
        """
        Distribute the problem to all agents, ensure consistency, and summarize results.
        
        Args:
            problem: The problem to solve
            
        Returns:
            Dictionary containing consistent agent responses and the summarized result
        """
        # Get multiple responses from each agent
        model_responses = {}
        for model, agent in self.agents.items():
            responses = []
            for _ in range(self.runs_per_model):
                try:
                    response = await agent.solve(problem)
                    if response:
                        response_dict = eval(response)
                        responses.append({
                            "model": model,
                            "raw_response": response_dict["solution"]
                        })
                except Exception as e:
                    print(f"Error from {model} run: {str(e)}")
                    continue
            
            if responses:
                # Analyze consistency and get best response
                best_response = self.consistency_agent.analyze_model_responses(responses)
                if best_response:
                    model_responses[model] = best_response
                else:
                    print(f"Warning: Inconsistent responses from {model}")
                    print("Responses received:")
                    for i, resp in enumerate(responses, 1):
                        print(f"\nRun {i}:")
                        print(resp["raw_response"])

        if not model_responses:
            error_msg = "No consistent responses received from any agent"
            print(f"\nError: {error_msg}")
            raise ValueError(error_msg)

        try:
            # Convert dictionary to list for summarizer
            valid_responses = list(model_responses.values())
            
            # Summarize results
            summary = await self.summarizer.analyze_responses(valid_responses)
            
            return {
                "problem": problem,
                "agent_responses": valid_responses,
                "summary": summary
            }
        except Exception as e:
            error_msg = str(e)
            print(f"\nError during analysis: {error_msg}")
            print("\nConsistent responses received:")
            for response in valid_responses:
                print(f"\n{response['model']}:")
                print(response['raw_response'])
            
            # Return partial results if summarization fails
            return {
                "problem": problem,
                "agent_responses": valid_responses,
                "summary": {
                    "status": "error",
                    "message": f"Error analyzing responses: {error_msg}",
                    "all_answers": {r["model"]: "Response received but analysis failed" for r in valid_responses}
                }
            }
