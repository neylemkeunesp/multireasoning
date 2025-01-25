import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock
from src.agents.math_agent import MathAgent
from src.orchestrator import Orchestrator
from src.summarizer import Summarizer

# Mock response for successful API call
MOCK_API_RESPONSE = {
    "choices": [{
        "message": {
            "content": """All Agent Answers:
o1: The given triangle sides 3, 4, and 5 form a right triangle. However, without additional information about the angles or height, I cannot provide a definitive numerical answer. The area calculation requires either the height or an angle in addition to the sides.

gemini: This appears to be a 3-4-5 right triangle. Using base × height:
Area = (3 × 4)/2 = 6 square units

deepseek: Cannot determine the area with certainty. While these measurements could form a right triangle, we need to verify if these sides actually create a valid triangle before calculating the area."""
        }
    }]
}

@pytest.mark.asyncio
async def test_math_agent():
    """Test individual math agent functionality."""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_post.return_value = mock_response

        agent = MathAgent(model="o1")
        problem = "What is the area of a triangle with sides 3, 4, and 5?"
        
        # Test raw response
        response = await agent.solve(problem)
        print("\nMath Agent Raw Response:")
        print(response)
        
        assert response is not None, "Agent should return a response"
        response_dict = eval(response)
        assert "model" in response_dict, "Response should contain model info"
        assert "solution" in response_dict, "Response should contain solution"
        assert len(response_dict["solution"]) > 0, "Solution should not be empty"

@pytest.mark.asyncio
async def test_orchestrator():
    """Test orchestrator functionality."""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_post.return_value = mock_response

        orchestrator = Orchestrator()
        problem = "What is the area of a triangle with sides 3, 4, and 5?"
        
        # Test orchestrated response
        result = await orchestrator.solve_problem(problem)
        print("\nOrchestrator Result:")
        print(json.dumps(result, indent=2))
        
        assert "problem" in result, "Result should contain the problem"
        assert "agent_responses" in result, "Result should contain agent responses"
        assert len(result["agent_responses"]) > 0, "Should have at least one agent response"
        assert "summary" in result, "Result should contain summary"

@pytest.mark.asyncio
async def test_summarizer_numeric():
    """Test summarizer functionality with numeric answers."""
    summarizer = Summarizer()
    responses = [
        {
            "model": "test_model",
            "raw_response": """
1. First, understand what is being asked
   The problem asks for the area of a triangle with sides 3, 4, and 5 units.

2. Break down the problem into steps
   We can use Heron's formula since we know all three sides.

3. Solve each step showing your work
   s = (a + b + c)/2 = (3 + 4 + 5)/2 = 6
   Area = √(s(s-a)(s-b)(s-c))
   Area = √(6(6-3)(6-4)(6-5))
   Area = √(6 × 3 × 2 × 1)
   Area = √36
   Area = 6

4. Verify your answer
   This matches the expected area for a 3-4-5 right triangle
   Area = (base × height)/2 = (3 × 4)/2 = 6

5. Final answer: 6 square units
"""
        }
    ]
    
    # Test analysis
    result = await summarizer.analyze_responses(responses)
    print("\nSummarizer Numeric Result:")
    print(json.dumps(result, indent=2))
    
    assert result is not None, "Should return analysis result"
    assert "status" in result, "Result should have status"
    assert "best_answer" in result, "Result should have best answer"
    assert "all_answers" in result, "Result should have all answers"
    assert "6 square units" in result["best_answer"], "Best answer should contain the numeric value with units"

@pytest.mark.asyncio
async def test_agent_consistency():
    """Test consistency of agent responses."""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Configure mock for consistent responses
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """Let's analyze the convergence of this power tower sequence:

1. First, let's understand what we're looking at:
   a₁ = x
   a₂ = x^x
   a₃ = x^(x^x)

2. For this sequence to converge:
   - The values must remain finite
   - Each term must approach a specific value

3. Key observations:
   - For x < 0, the sequence is undefined due to complex numbers
   - For x = 0, the sequence is undefined after a₁
   - For 0 < x < 1/e, the sequence converges
   - For x > 1/e, the sequence diverges to infinity

Therefore, the sequence converges when x is in the interval (0, 1/e), where e is Euler's number."""
                }
            }]
        }
        mock_post.return_value = mock_response

        # Define multiple test problems with their expected answers
        test_problems = [
            {
                "prompt": """Essa questão trata de uma sequência de "torres de potências" de base x, onde cada elemento da sequência é definido recursivamente como:
$$ a_1 = x $$
$$ a_2 = x^x $$
$$ a_3 = x^{(x^x)} $$
Para quais valores de x a sequência converge?""",
                "expected_answer": "(0, 1/e)",
                "mock_response": """Let's analyze the convergence of this power tower sequence:
1. Key observations:
   - For x < 0, sequence undefined (complex numbers)
   - For x = 0, sequence undefined after a₁
   - For 0 < x < 1/e, sequence converges
   - For x > 1/e, sequence diverges

Therefore, the sequence converges when x is in the interval (0, 1/e)."""
            },
            {
                "prompt": "What is the area of a triangle with sides 3, 4, and 5?",
                "expected_answer": "6 square units",
                "mock_response": """Let's solve this step by step:

1. For a triangle with sides 3, 4, and 5:
   - This is a right triangle (3-4-5 triangle)
   - We can use the formula: Area = (base × height)/2

2. Using the shortest side as base (3):
   - Height is 4 (perpendicular side)
   - Area = (3 × 4)/2 = 6

Therefore, the area is 6 square units."""
            },
            {
                "prompt": "Solve the equation: x² + 5x + 6 = 0",
                "expected_answer": "x = -2 or x = -3",
                "mock_response": """Let's solve this quadratic equation:

1. Using factoring method:
   x² + 5x + 6 = 0
   (x + 2)(x + 3) = 0

2. Using zero product property:
   x + 2 = 0 or x + 3 = 0
   x = -2 or x = -3

Therefore, x = -2 or x = -3"""
            }
        ]

        agents = ["o1", "gemini", "deepseek"]
        summarizer = Summarizer()
        
        for agent_model in agents:
            print(f"\nTesting consistency for {agent_model}...")
            agent = MathAgent(model=agent_model)
            
            # Test each problem
            for problem in test_problems:
                print(f"\nTesting problem: {problem['prompt'][:50]}...")
                
                # Configure mock for this problem
                mock_response.json.return_value = {
                    "choices": [{
                        "message": {
                            "content": problem["mock_response"]
                        }
                    }]
                }
                mock_post.return_value = mock_response
                
                # Get multiple responses from the same agent for this problem
                responses = []
                for i in range(3):  # Test 3 times per problem
                    response = await agent.solve(problem["prompt"])
                    response_dict = eval(response)
                    responses.append({
                        "model": agent_model,
                        "raw_response": response_dict["solution"]
                    })
                
                # Analyze consistency using summarizer
                result = await summarizer.analyze_responses(responses)
                print(f"{agent_model} Consistency Result for Problem {test_problems.index(problem) + 1}:")
                print(json.dumps(result, indent=2))
                
                # Verify consistency
                assert result["status"] == "agreement", \
                    f"{agent_model} should provide consistent answers for problem {test_problems.index(problem) + 1}"
                assert problem["expected_answer"] in result["best_answer"], \
                    f"{agent_model} should consistently provide correct answer for problem {test_problems.index(problem) + 1}"
                assert all(problem["expected_answer"] in answer for answer in result["all_answers"].values()), \
                    f"All responses from {agent_model} should contain the expected answer for problem {test_problems.index(problem) + 1}"

@pytest.mark.asyncio
async def test_cross_agent_agreement():
    """Test agreement between different agents."""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Configure mock for different but mathematically equivalent responses
        responses = {
            "o1": """Let's analyze the convergence of this power tower sequence:
1. Key observations:
   - For x < 0, sequence undefined (complex numbers)
   - For x = 0, sequence undefined after a₁
   - For 0 < x < 1/e, sequence converges
   - For x > 1/e, sequence diverges

Therefore, the sequence converges when x is in the interval (0, 1/e).""",
            
            "gemini": """Analyzing the power tower sequence:
1. Analysis:
   - x must be positive for sequence to be defined
   - Convergence occurs in interval (0, 1/e)
   - Diverges for x > 1/e
   - Undefined for x ≤ 0

Thus, convergence happens for x in (0, 1/e).""",
            
            "deepseek": """The power tower sequence:
1. Conditions:
   - Sequence undefined for x ≤ 0
   - Converges for 0 < x < 1/e
   - Diverges for x > 1/e

Final Answer: The sequence converges in the interval (0, 1/e)."""
        }

        def mock_response(model):
            return {
                "choices": [{
                    "message": {
                        "content": responses[model]
                    }
                }]
            }

        mock_post.side_effect = lambda *args, **kwargs: MagicMock(
            json=lambda: mock_response(json.loads(kwargs["json"])["model"])
        )

        problem = """Essa questão trata de uma sequência de "torres de potências" de base x, onde cada elemento da sequência é definido recursivamente como:
$$ a_1 = x $$
$$ a_2 = x^x $$
$$ a_3 = x^{(x^x)} $$
Para quais valores de x a sequência converge?"""

        # Get responses from all agents
        agent_responses = []
        for model in ["o1", "gemini", "deepseek"]:
            agent = MathAgent(model=model)
            response = await agent.solve(problem)
            response_dict = eval(response)
            agent_responses.append({
                "model": model,
                "raw_response": response_dict["solution"]
            })

        # Analyze agreement between agents
        summarizer = Summarizer()
        result = await summarizer.analyze_responses(agent_responses)
        print("\nCross-Agent Agreement Result:")
        print(json.dumps(result, indent=2))

        # Verify agreement
        assert result["status"] == "agreement", "All agents should agree on the convergence interval"
        assert "(0, 1/e)" in result["best_answer"], "Best answer should contain the correct interval"
        assert result["confidence"] == "high", "Confidence should be high when all agents agree"
        assert all("(0, 1/e)" in answer for answer in result["all_answers"].values()), \
            "All agents should identify the same convergence interval"

def run_tests():
    """Run all tests."""
    print("Running tests...")
    asyncio.run(test_math_agent())
    asyncio.run(test_orchestrator())
    asyncio.run(test_summarizer_numeric())
    asyncio.run(test_agent_consistency())
    asyncio.run(test_cross_agent_agreement())
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_tests()
