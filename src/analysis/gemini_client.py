import json
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google import genai
from google.genai.errors import APIError
import structlog

logger = structlog.get_logger(__name__)

class GeminiClient:
    """Wrapper around the Google GenAI SDK with retry logic and structured JSON support."""
    
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.1, max_tokens: int = 4096):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((APIError,)),
        before_sleep=lambda retry_state: logger.warning(
            f"Gemini API call failed with {retry_state.outcome.exception()}. Retrying in {retry_state.next_action.sleep}s..."
        )
    )
    def analyze_batch_json(self, prompt: str, system_prompt: str) -> dict:
        """
        Calls the LLM with the provided prompts, enforcing a JSON response format.
        Retries automatically on transient API errors.
        """
        logger.debug(f"Calling Gemini API with model {self.model_name}")
        
        full_prompt = f"{system_prompt}\n\nUser Request:\n{prompt}"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )
        )
        
        content = response.text
        if not content:
            raise ValueError("LLM returned empty content.")
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {content}")
            raise ValueError(f"LLM returned invalid JSON: {e}")
