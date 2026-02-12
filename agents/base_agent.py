import os
import json
import logging
from typing import Optional
from urllib import response
from openai import OpenAI

from config.config import DEFAULT_MODEL

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all travel planning agents."""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        """
        Initialize the base agent.
        
        Args:
            name: The name of the agent
            api_key: OpenAI API key (uses environment variable if not provided)
        """
        self.name = name
        api_key = self.get_api_key()
        self.client = OpenAI(api_key=api_key)
    
    def call_openai_api(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict:
        """
        Make a call to the OpenAI API and return parsed JSON response.
        
        Args:
            system_prompt: System role context
            user_prompt: User message/prompt
            model: Model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (default: 1000)
        
        Returns:
            Parsed JSON response or error dict
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_text = response.choices[0].message.content
            
            # Log the response for debugging
            if response_text:
                logger.debug(f"API response received: {response_text[:200]}")
            
            if not response_text or not response_text.strip():
                logger.error("API returned empty response")
                return {"error": "Empty response from API"}
            
            # Strip markdown code block wrapper if present
            cleaned_text = self.clean_response(response_text)
            
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response_text[:500]}")
                logger.error(f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}")
                return {"error": f"Invalid JSON from API: {e.msg}"}
        
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return {"error": str(e)}
    
    def clean_response(self, response: str) -> str:
        """
        Clean the API response by removing markdown code block wrappers if present.
        
        Args:
            response: The raw response string from the API
        Returns:
            Cleaned JSON response string
        """    
        cleaned_text = response.strip()
        
        # Remove markdown code blocks (``` or ```json)
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.strip("`").strip()
            # Remove language identifier if present (e.g., "json\n")
            if cleaned_text.startswith("json"):
                cleaned_text = cleaned_text[4:].lstrip()
        
        return cleaned_text.strip()
    
    def get_api_key(self):
        """
        Retrieve the OpenAI API key from environment variable.
        
        Returns:
            The API key string
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        return api_key