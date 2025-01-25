from typing import List, Dict, Any, Optional
import re
from .base_agent import BaseAgent

class ConsistencyAgent:
    """Agent that analyzes multiple responses from the same model for consistency."""
    
    def analyze_model_responses(self, responses: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Analyze multiple responses from the same model and select the best one.
        
        Args:
            responses: List of responses from the same model, each containing:
                - model: Model name
                - raw_response: The response text
                
        Returns:
            The best response if responses are consistent, None if inconsistent
        """
        if not responses or len(responses) < 2:
            return None
            
        # Extract final answers from each response
        final_answers = []
        for response in responses:
            answer = self._extract_final_answer(response["raw_response"])
            if answer:
                final_answers.append((response, answer))
                
        if not final_answers:
            return None
            
        # Check for exact text match agreement
        first_answer = final_answers[0][1]
        exact_matches = [
            response for response, answer in final_answers
            if answer == first_answer
        ]
        
        # If we have exact matches for all responses, select the most detailed one
        if len(exact_matches) == len(responses):
            return max(exact_matches, key=lambda r: len(r["raw_response"]))
            
        # Try numerical comparison for numeric answers
        numerical_values = []
        for response, answer in final_answers:
            match = re.search(r'(\d+(?:\.\d+)?)', answer)
            if match:
                numerical_values.append((response, float(match.group(1))))
                
        # If all answers are numeric, check for numerical agreement
        if len(numerical_values) == len(final_answers):
            first_value = numerical_values[0][1]
            matching_responses = [
                response for response, value in numerical_values
                if abs(value - first_value) <= 0.01
            ]
            
            # If we have numerical agreement, select the most detailed response
            if len(matching_responses) == len(responses):
                return max(matching_responses, key=lambda r: len(r["raw_response"]))
                
        # If no consistent agreement found, return None
        return None
        
    def _extract_final_answer(self, text: str) -> Optional[str]:
        """Extract final answer from response text."""
        patterns = [
            r'Final [Aa]nswer:?\s*([^\.]+(?:\.[^\n]+)?)',
            r'Therefore,?\s+([^\.]+(?:\.[^\n]+)?)',
            r'Thus,?\s+([^\.]+(?:\.[^\n]+)?)',
            r'In conclusion,?\s+([^\.]+(?:\.[^\n]+)?)',
            r'The answer is:?\s+([^\.]+(?:\.[^\n]+)?)',
            r'Area\s*=\s*(\d+(?:\.\d+)?(?:\s*square units?)?)',
            r'\d+\.\s*([^\.]+(?:\.[^\n]+)?)'  # Numbered list item
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
            if matches:
                answer = matches[-1].group(1).strip()
                # Clean up the answer
                answer = re.sub(r'\s+', ' ', answer)  # Normalize whitespace
                answer = answer.rstrip('.')  # Remove trailing period
                return answer
        return None
