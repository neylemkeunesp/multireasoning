from typing import List, Dict, Any, Optional
import re
import json
from .models.openrouter import OpenRouterClient

class Summarizer:
    def __init__(self):
        self.client = OpenRouterClient()
    async def analyze_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze responses from multiple agents and determine the best answer.
        
        Args:
            responses: List of formatted responses from agents
            
        Returns:
            Dictionary containing analysis and best answer
        """
        if not responses:
            return {
                "status": "error",
                "message": "No valid responses received from agents",
                "all_answers": {}
            }

        if len(responses) == 1:
            # If we only have one response, use it directly
            response = responses[0]
            answer = self._extract_final_answer(response["raw_response"])
            return {
                "status": "single_response",
                "message": "Only one agent provided a valid response",
                "best_answer": answer if answer else "No clear answer found",
                "confidence": "medium",
                "selected_from": response["model"],
                "reasoning": "Only one response available, using it directly",
                "all_answers": {response["model"]: answer if answer else "No clear answer found"}
            }

        # Create analysis prompt
        analysis_prompt = self._create_analysis_prompt(responses)
        
        # Get analysis from o1-preview model
        analysis = await self.client.generate_response("o1", analysis_prompt)
        
        if not analysis:
            # Fallback to basic analysis if API call fails
            return self._basic_analysis(responses)
            
        try:
            # Parse the analysis response
            analysis_dict = json.loads(analysis)
            
            # Add all answers to the result
            # Extract answers for each model
            answers = {}
            for response in responses:
                answer = self._extract_final_answer(response["raw_response"])
                answers[response["model"]] = answer if answer else "No clear answer found"
            analysis_dict["all_answers"] = answers
            
            return analysis_dict
        except json.JSONDecodeError:
            # Fallback to basic analysis if parsing fails
            return self._basic_analysis(responses)

    def _create_analysis_prompt(self, responses: List[Dict[str, Any]]) -> str:
        """Create a prompt for analyzing multiple agent responses."""
        prompt = """As an expert analyst, carefully analyze these solutions and determine the best answer. Consider:
1. Correctness and validity of each approach
2. Completeness and clarity of explanations
3. Proper application of concepts and methods
4. Verification steps used
5. Precision and accuracy of the final answer

Provide your analysis in JSON format with the following structure:
{
    "status": "agreement" or "disagreement",
    "message": "Brief explanation of agreement status",
    "best_answer": "The selected best answer",
    "confidence": "high", "medium", or "low",
    "selected_from": "model name that provided best answer",
    "reasoning": "Detailed explanation including:
        - Validity of each approach
        - Comparison of solution methods
        - Why the selected answer is most reliable
        - Any potential issues in other solutions
        - Verification of the chosen answer"
}

The solutions to analyze are:

"""
        # Add each agent's response
        for response in responses:
            prompt += f"\n{response['model']} Solution:\n"
            prompt += f"{response['raw_response']}\n"
            
        prompt += "\nProvide your analysis in the exact JSON format specified above. Include detailed reasoning for your selection."
        
        return prompt

    def _basic_analysis(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback method for basic analysis when API call fails."""
        # Extract final answers from raw responses
        final_answers = []
        for response in responses:
            answer = self._extract_final_answer(response["raw_response"])
            if answer:
                final_answers.append((response["model"], answer))
        
        if not final_answers:
            return {
                "status": "error",
                "message": "Could not extract clear answers from responses",
                "all_answers": {r["model"]: "No clear answer found" for r in responses}
            }

        # Check for exact text match agreement first
        first_answer = final_answers[0][1]
        text_agreement = all(
            answer == first_answer
            for _, answer in final_answers[1:]
        )
        
        if text_agreement:
            return {
                "status": "agreement",
                "message": "All agents agree on the answer",
                "best_answer": first_answer,
                "confidence": "high",
                "selected_from": "consensus",
                "reasoning": "All agents provided the same answer",
                "all_answers": {model: answer for model, answer in final_answers}
            }
            
        # If no exact match, try numerical comparison for numeric answers
        numerical_values = []
        for model, answer in final_answers:
            match = re.search(r'(\d+(?:\.\d+)?)', answer)
            if match:
                numerical_values.append((model, float(match.group(1))))

        # Check for numerical agreement if all answers are numeric
        if len(numerical_values) == len(final_answers):
            first_value = numerical_values[0][1]
            numerical_agreement = all(
                abs(value - first_value) <= 0.01
                for _, value in numerical_values[1:]
            )
            if numerical_agreement:
                return {
                    "status": "agreement",
                    "message": "All agents agree on the numerical value",
                    "best_answer": final_answers[0][1],
                    "confidence": "high",
                    "selected_from": "consensus",
                    "reasoning": "All agents provided equivalent numerical answers",
                    "all_answers": {model: answer for model, answer in final_answers}
                }
        
        # If no agreement, select the most detailed response
        best_response = max(responses, key=lambda r: len(r["raw_response"]))
        best_answer = self._extract_final_answer(best_response["raw_response"]) or "No clear answer found"
        
        return {
            "status": "disagreement",
            "message": "Agents provided different answers",
            "best_answer": best_answer,
            "confidence": "medium",
            "selected_from": best_response["model"],
            "reasoning": "Selected based on most detailed explanation and solution steps",
            "all_answers": {model: answer for model, answer in final_answers}
        }
        
    def _extract_final_answer(self, text: str) -> Optional[str]:
        """Extract final answer from raw response."""
        # Try to find explicit final answer markers first
        patterns = [
            r'Final [Aa]nswer:?\s*([^\.]+(?:\.[^\n]+)?)',
            r'Therefore,?\s+([^\.]+(?:\.[^\n]+)?)',
            r'Thus,?\s+([^\.]+(?:\.[^\n]+)?)',
            r'In conclusion,?\s+([^\.]+(?:\.[^\n]+)?)',
            r'The answer is:?\s+([^\.]+(?:\.[^\n]+)?)',
            # Fallback to numeric patterns for backward compatibility
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
                # For numeric answers, ensure units are included if applicable
                if re.search(r'^\d+(?:\.\d+)?$', answer):
                    if not re.search(r'square units?', text, re.IGNORECASE):
                        answer = f"{answer} square units"
                return answer
        return None
