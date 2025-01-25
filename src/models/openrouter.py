from typing import Optional, Dict, Any
import httpx
import uuid
from ..config import settings

class OpenRouterClient:
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key is not set")
            
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://daselva.com",
            "X-Title": "Multi-Agent Math Solver",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        
        # Validate API key format
        if not settings.OPENROUTER_API_KEY.startswith("sk-"):
            print("Warning: OpenRouter API key format may be invalid. Should start with 'sk-'")

    async def generate_response(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate a response from the specified model using OpenRouter API.
        
        Args:
            model: The model identifier (e.g., 'o1', 'gemini', 'deepseek')
            prompt: The input prompt for the model
            temperature: Controls randomness in the response
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated response text or None if the request fails
        """
        model_id = settings.MODELS.get(model)
        if not model_id:
            raise ValueError(f"Unknown model: {model}")

        # Use consistent configuration for all models
        config = {
            "max_tokens": 10000,
            "temperature": 0.3
        }
        
        # Build payload with model-specific configuration
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "stream": False,
            "cache": False,
            "request_id": str(uuid.uuid4()),
        }
        
        # Add model-specific parameters
        if "top_p" in config:
            payload["top_p"] = config["top_p"]

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.post(
                            f"{self.base_url}/chat/completions",
                            headers=self.headers,
                            json=payload,
                            timeout=30.0
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        if 'error' in data:
                            raise ValueError(f"API Error: {data['error'].get('message', str(data['error']))}")
                            
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 401:
                            raise ValueError("Invalid API key. Please check your OpenRouter API key.")
                        elif e.response.status_code == 404:
                            raise ValueError("API endpoint not found. Please check the OpenRouter base URL.")
                        elif e.response.status_code == 429:
                            raise ValueError("Rate limit exceeded. Please try again later.")
                        else:
                            raise ValueError(f"HTTP Error {e.response.status_code}: {str(e)}")
                    
                    # Get the response content
                    content = None
                    if "choices" in data and data["choices"]:
                        message = data["choices"][0].get("message", {})
                        content = message.get("content")
                        if content is None:
                            print(f"Warning: No content in response: {data}")
                    elif "response" in data:  # For Gemini model
                        content = data["response"]
                        if content is None:
                            print(f"Warning: No response content: {data}")
                    
                    # Check if we got a valid response
                    if content and len(content.strip()) > 0:
                        return content
                    
                    # If response is empty and we have retries left, continue
                    if attempt < max_retries - 1:
                        print(f"Empty response from {model}, attempt {attempt + 1}/{max_retries}. Response data: {data}")
                        print("Retrying with new request ID...")
                        # Generate new request ID for retry
                        payload["request_id"] = str(uuid.uuid4())
                        continue
                    
                    raise ValueError(f"Empty response from {model} after {max_retries} attempts. Last response data: {data}")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error from {model}, attempt {attempt + 1}/{max_retries}: {str(e)}. Retrying...")
                    # Generate new request ID for retry
                    payload["request_id"] = str(uuid.uuid4())
                    continue
                print(f"Error generating response from {model} after {max_retries} attempts: {str(e)}")
                return None

    @staticmethod
    def create_math_prompt(problem: str) -> str:
        """
        Create a structured prompt for math problem solving.
        
        Args:
            problem: The math problem to solve
            
        Returns:
            A formatted prompt string
        """
        return f"""You are a mathematical expert. Focus ONLY on solving this specific math problem step by step, showing all your work clearly. Do not reference or use information from any previous problems:

Problem: {problem}

Follow this EXACT format in your solution:
1. First, understand what is being asked
   - Clearly state what the problem is asking for
   - Identify the given information
   - Note any relevant mathematical concepts needed

2. Break down the problem into steps
   - List the specific steps needed to solve this problem
   - Identify the formulas or methods you'll use

3. Solve each step showing your work
   - Show ALL calculations clearly
   - Include units in your calculations
   - Explain each step briefly

4. Verify your answer
   - Check if your answer makes sense
   - Verify using an alternative method if possible
   - Confirm the units are correct

5. Final answer: [IMPORTANT: State ONLY the final result ]

Important: 
- Focus ONLY on this specific problem
- Follow the numbered format exactly
- Show all calculations clearly
- Do not include explanations in the final answer line
- Do not reference any previous problems or solutions

Your solution:"""
