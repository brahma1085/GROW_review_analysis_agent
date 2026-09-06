import json
import math
from typing import List
import structlog
from src.models.review import NormalizedReview, AnalyzedReview
from src.models.config import AgentConfig
from src.analysis.llm_client import LLMClient
from src.prompts.classification_prompt import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_PROMPT

logger = structlog.get_logger(__name__)

import os

class ReviewAnalyzer:
    """Service to classify and analyze a batch of normalized reviews."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        api_key = os.environ.get("GROQ_API_KEY", "dummy_key_for_tests")
        self.llm_client = LLMClient(
            api_key=api_key,
            model_name=config.analysis.llm_model,
            temperature=config.analysis.llm_temperature,
            max_tokens=4096 # Hardcoded for now or add to config
        )
        self.batch_size = config.analysis.batch_size
        
    def analyze_batch(self, reviews: List[NormalizedReview]) -> List[AnalyzedReview]:
        """Analyzes a list of reviews in smaller batches to avoid prompt length limits."""
        # Filter out unusable reviews before processing
        usable_reviews = [r for r in reviews if r.is_usable]
        if not usable_reviews:
            logger.info("No usable reviews to analyze.")
            return []
            
        num_batches = math.ceil(len(usable_reviews) / self.batch_size)
        logger.info(f"Analyzing {len(usable_reviews)} reviews across {num_batches} batches...")
        
        all_analyzed = []
        for i in range(num_batches):
            batch = usable_reviews[i * self.batch_size : (i + 1) * self.batch_size]
            logger.debug(f"Processing batch {i+1}/{num_batches} (size: {len(batch)})")
            
            try:
                batch_result = self._process_batch(batch)
                all_analyzed.extend(batch_result)
            except Exception as e:
                logger.error(f"Batch {i+1} failed completely. Falling back to individual processing. Error: {e}")
                # Fallback: process individually so we don't lose the whole batch on a parsing error
                for r in batch:
                    try:
                        single_result = self._process_batch([r])
                        all_analyzed.extend(single_result)
                    except Exception as single_e:
                        logger.error(f"Failed to analyze review {r.original_review.review_id}: {single_e}")
                        
        logger.info(f"Successfully analyzed {len(all_analyzed)}/{len(usable_reviews)} reviews.")
        return all_analyzed

    def _process_batch(self, batch: List[NormalizedReview]) -> List[AnalyzedReview]:
        # Format the reviews into a JSON array string for the prompt
        # OPTIMIZATION: Only send the minimum required fields to the LLM to save tokens
        optimized_batch = []
        for r in batch:
            optimized_batch.append({
                "review_id": r.original_review.review_id,
                "text": r.cleaned_text,
                "star_rating": r.original_review.star_rating
            })
            
        batch_json = json.dumps(optimized_batch, indent=2)
        prompt = CLASSIFICATION_USER_PROMPT.replace("{batch_json}", batch_json)
        
        response_json = self.llm_client.analyze_batch_json(
            prompt=prompt,
            system_prompt=CLASSIFICATION_SYSTEM_PROMPT
        )
        
        if "analyzed_reviews" not in response_json:
            raise ValueError("LLM response did not contain 'analyzed_reviews' key.")
            
        review_map = {r.original_review.review_id: r for r in batch}
        analyzed = []
        for review_dict in response_json["analyzed_reviews"]:
            # Validate each review through Pydantic
            try:
                review_id = review_dict.pop("review_id", None)
                if not review_id or review_id not in review_map:
                    logger.warning(f"LLM returned unknown or missing review_id: {review_id}")
                    continue
                    
                analyzed.append(AnalyzedReview(
                    normalized_review=review_map[review_id],
                    **review_dict
                ))
            except Exception as e:
                logger.warning(f"Failed to parse a review from LLM response. Error: {e}, Data: {review_dict}")
                
        return analyzed
