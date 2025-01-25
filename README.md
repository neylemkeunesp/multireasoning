# Multi-Agent Math Problem Solver

A Python-based system that uses multiple LLM agents to solve math problems collaboratively. The system leverages different models through OpenRouter API to provide diverse perspectives and ensures accurate solutions through consensus or intelligent selection.

## Features

- Multiple agent collaboration using different LLM models:
  - o1-preview
  - gemini-2.0-flash-thinking
  - Deepseek-R1
- Structured problem-solving approach with step-by-step solutions
- Consensus-based answer selection
- Detailed explanation of reasoning and steps
- Confidence scoring for solutions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multireasoning.git
cd multireasoning
```

2. Install dependencies:

Option 1: Using pip with requirements.txt:
```bash
pip install -r requirements.txt
```

Option 2: Installing the package:
```bash
pip install .
```

## Configuration

1. Get an API key from [OpenRouter](https://openrouter.ai/)

2. Create a `.env` file in the project root:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

Alternatively, you can provide the API key via command line when running the program.

## Usage

You can use the system in two ways:

### 1. Command Line Interface

1. Command line interface:
```bash
# Using environment variable for API key
python main.py "What is the area of a triangle with sides 3, 4, and 5?"

# Or providing API key directly
python main.py --api-key your_api_key "What is the area of a triangle with sides 3, 4, and 5?"
```

2. As a Python module:
```python
import asyncio
from src.main import solve_math_problem

async def example():
    problem = "What is the area of a triangle with sides 3, 4, and 5?"
    result = await solve_math_problem(problem)
    print(result)

asyncio.run(example())
```

## Output Format

The system provides detailed output including:

1. Individual agent responses with:
   - Problem understanding
   - Solution steps
   - Final answer

2. Summary analysis:
   - Agreement status between agents
   - Best answer selection
   - Confidence level
   - Reasoning for selection (in case of disagreement)

Example output:
```
Problem: What is the area of a triangle with sides 3, 4, and 5?

Agent Responses:
o1 Solution:
Understanding: This is a triangle where we know all three sides (3, 4, and 5 units).
Solution Steps:
1. We can use Heron's formula to find the area
2. Calculate semi-perimeter s = (a + b + c)/2
3. Area = √(s(s-a)(s-b)(s-c))
Final Answer: 6 square units

[Additional agent responses...]

Summary:
Status: agreement
Message: All agents agree on the answer
Best Answer: 6 square units
Confidence: high
```

## How It Works

1. The system distributes the math problem to multiple agents, each powered by a different LLM model.
2. Each agent:
   - Analyzes and understands the problem
   - Breaks it down into steps
   - Provides a detailed solution
   - Gives a final answer

3. The summarizer then:
   - Compares all responses
   - Checks for agreement
   - Selects the best answer based on:
     - Agreement between agents
     - Completeness of explanation
     - Solution detail level

4. Finally, it provides a comprehensive output with all solutions and analysis.

### 2. Python Module
```python
import asyncio
from src.main import solve_math_problem

async def example():
    problem = "What is the area of a triangle with sides 3, 4, and 5?"
    result = await solve_math_problem(problem)
    print(result)

asyncio.run(example())
```

## Testing

The project includes a comprehensive test suite to verify functionality:

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Run the tests:
```bash
# Run all tests
pytest

# Run tests with detailed output
pytest -v

# Run a specific test file
pytest tests/test_math_solver.py

# Run tests and show print statements
pytest -s
```

The test suite includes:
- Individual agent testing
- Orchestrator integration testing
- Summarizer functionality testing
- End-to-end solution testing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Before submitting:
1. Ensure all tests pass
2. Add tests for new functionality
3. Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.
