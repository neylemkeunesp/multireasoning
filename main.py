import asyncio
import argparse
from src.main import solve_math_problem, format_output

async def main():
    parser = argparse.ArgumentParser(description='Multi-agent math problem solver')
    parser.add_argument('problem', type=str, nargs='+', help='The math problem to solve')
    parser.add_argument('--api-key', type=str, help='OpenRouter API key')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output including agent responses')
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        import os
        os.environ['OPENROUTER_API_KEY'] = args.api_key
    
    # Combine problem words into a single string
    problem = ' '.join(args.problem)
    
    try:
        result = await solve_math_problem(problem)
        
        # Check if we got any valid responses
        if not result.get("agent_responses"):
            print("Error: No valid responses received from any agent")
            return
        
        # Check if summary analysis succeeded
        if result.get("summary", {}).get("status") == "error":
            print("Warning: Error analyzing responses")
            print(result["summary"]["message"])
            print("\nIndividual agent responses:")
            for response in result["agent_responses"]:
                print(f"\n{response['model']} response received")
                if args.verbose:
                    print(response["raw_response"])
        else:
            print(format_output(result))
            
    except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            
            if args.verbose:
                print("\nDetailed error information:")
                import traceback
                print(traceback.format_exc())
                print("\nTry checking:")
                print("1. OpenRouter API key is set correctly")
                print("2. Internet connection is stable")
                print("3. All models are available on OpenRouter")
            else:
                print("\nTry running with --verbose flag for more details")

if __name__ == "__main__":
    asyncio.run(main())
