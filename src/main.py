import asyncio
import json
from typing import Dict, Any
from .orchestrator import Orchestrator

async def solve_math_problem(problem: str) -> Dict[str, Any]:
    """
    Solve a math problem using multiple agents and return a consolidated result.
    
    Args:
        problem: The math problem to solve
        
    Returns:
        Dictionary containing agent responses and analysis
    """
    orchestrator = Orchestrator()
    result = await orchestrator.solve_problem(problem)
    return result

def format_output(result: Dict[str, Any]) -> str:
    """
    Format the result into a readable string.
    
    Args:
        result: The solution result dictionary
        
    Returns:
        Formatted string representation of the result
    """
    output = []
    output.append(f"Problem: {result['problem']}\n")
    
    # Add individual agent responses
    output.append("Agent Responses:")
    for response in result['agent_responses']:
        output.append(f"\n{response['model']} Solution:")
        output.append(response['raw_response'])
    
    # Add summary
    output.append("\nSummary:")
    summary = result['summary']
    output.append(f"Status: {summary['status']}")
    output.append(f"Message: {summary['message']}")
    
    if summary.get('best_answer'):
        output.append(f"Best Answer: {summary['best_answer']}")
    
    if summary.get('confidence'):
        output.append(f"Confidence: {summary['confidence']}")
    
    if summary.get('selected_from'):
        output.append(f"Selected from model: {summary['selected_from']}")
    
    if summary.get('reasoning'):
        output.append(f"\nReasoning: {summary['reasoning']}")
    
    # Always show all answers
    output.append("\nAll Agent Answers:")
    for model, answer in summary.get('all_answers', {}).items():
        output.append(f"{model}: {answer}")
    
    return "\n".join(output)

async def main():
    """Example usage of the math problem solver."""
    # Example math problem
    problem = "If a triangle has sides of length 3, 4, and 5, what is its area?"
    
    try:
        result = await solve_math_problem(problem)
        print(format_output(result))
    except Exception as e:
        print(f"Error solving problem: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
