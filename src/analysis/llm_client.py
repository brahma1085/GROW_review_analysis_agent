import json
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from groq import Groq, APIError, APIConnectionError, RateLimitError
import structlog

logger = structlog.get_logger(__name__)

class LLMClient:
    """Wrapper around the Groq SDK with retry logic and structured JSON support."""
    
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.1, max_tokens: int = 4096):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError)),
        before_sleep=lambda retry_state: logger.warning(
            f"LLM API call failed with {retry_state.outcome.exception()}. Retrying in {retry_state.next_action.sleep}s..."
        )
    )
    def analyze_batch_json(self, prompt: str, system_prompt: str) -> dict:
        """
        Calls the LLM with the provided prompts, enforcing a JSON response format.
        Retries automatically on transient API errors.
        """
        logger.debug(f"Calling Groq API with model {self.model_name}")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty content.")
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {content}")
            raise ValueError(f"LLM returned invalid JSON: {e}")
