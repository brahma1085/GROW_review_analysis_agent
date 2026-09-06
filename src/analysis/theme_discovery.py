import json
import structlog
from typing import List, Dict, Any, Optional

from src.models.review import AnalyzedReview
from src.models.theme import ThemeResult, Theme, SentimentDistribution, Sentiment, SeverityLevel
from src.analysis.llm_client import LLMClient
from src.prompts.theme_discovery_prompt import THEME_DISCOVERY_SYSTEM_PROMPT, THEME_DISCOVERY_USER_PROMPT

logger = structlog.get_logger(__name__)

class ThemeDiscoveryService:
    def __init__(self, llm_client: LLMClient, max_reviews_per_chunk: int = 50):
        self.llm_client = llm_client
        self.max_reviews_per_chunk = max_reviews_per_chunk

    def discover_themes(self, analyzed_reviews: List[AnalyzedReview]) -> ThemeResult:
        logger.info(f"Discovering themes from {len(analyzed_reviews)} reviews.")
        
        # Optimize payload by extracting only necessary fields to reduce tokens
        optimized_reviews = []
        for review in analyzed_reviews:
            optimized_reviews.append({
                "review_id": review.normalized_review.original_review.review_id,
                "categories": [c.value for c in review.categories],
                "sentiment": review.sentiment.value,
                "intent": review.intent,
                "key_phrases": review.key_phrases
            })

        all_discovered_themes = []
        all_unthemed_ids = set()

        # Process in chunks to stay within Groq TPM limits
        for i in range(0, len(optimized_reviews), self.max_reviews_per_chunk):
            chunk = optimized_reviews[i:i + self.max_reviews_per_chunk]
            chunk_json = json.dumps(chunk, indent=2)
            
            prompt = THEME_DISCOVERY_USER_PROMPT.format(reviews_json=chunk_json)
            
            try:
                logger.info(f"Sending chunk {i // self.max_reviews_per_chunk + 1} for theme discovery...")
                response = self.llm_client.analyze_batch_json(
                    prompt=prompt,
                    system_prompt=THEME_DISCOVERY_SYSTEM_PROMPT
                )
                
                themes_data = response.get("themes", [])
                unthemed = response.get("unthemed_review_ids", [])
                
                all_discovered_themes.extend(themes_data)
                all_unthemed_ids.update(unthemed)
                
            except Exception as e:
                logger.error(f"Error during theme discovery for chunk: {e}")
                # If a chunk fails completely after retries, add its reviews to unthemed
                all_unthemed_ids.update([r["review_id"] for r in chunk])

        # Post-process: Aggregate themes with the same name (case-insensitive) across chunks
        aggregated_themes_dict: Dict[str, dict] = {}
        for theme_data in all_discovered_themes:
            name_key = theme_data.get("name", "Unknown Theme").strip().lower()
            if name_key not in aggregated_themes_dict:
                aggregated_themes_dict[name_key] = {
                    "id": theme_data.get("id"),
                    "name": theme_data.get("name"),
                    "description": theme_data.get("description"),
                    "review_ids": set(theme_data.get("review_ids", []))
                }
            else:
                aggregated_themes_dict[name_key]["review_ids"].update(theme_data.get("review_ids", []))
                
        # Calculate statistics
        final_themes = []
        total_reviews = len(analyzed_reviews)
        review_lookup = {r.normalized_review.original_review.review_id: r for r in analyzed_reviews}
        
        for name_key, theme_data in aggregated_themes_dict.items():
            review_ids = list(theme_data["review_ids"])
            if not review_ids:
                continue
                
            theme_reviews = [review_lookup[rid] for rid in review_ids if rid in review_lookup]
            
            if not theme_reviews:
                continue

            review_count = len(theme_reviews)
            review_percentage = round((review_count / total_reviews) * 100, 2)
            
            sentiment_dist = self._calculate_sentiment_distribution(theme_reviews)
            
            # Determine highest severity
            severity = SeverityLevel.INFORMATIONAL
            for r in theme_reviews:
                if r.severity == SeverityLevel.CRITICAL:
                    severity = SeverityLevel.CRITICAL
                    break
                elif r.severity == SeverityLevel.HIGH and severity not in [SeverityLevel.CRITICAL]:
                    severity = SeverityLevel.HIGH
                elif r.severity == SeverityLevel.MEDIUM and severity in [SeverityLevel.LOW, SeverityLevel.INFORMATIONAL]:
                    severity = SeverityLevel.MEDIUM
                elif r.severity == SeverityLevel.LOW and severity == SeverityLevel.INFORMATIONAL:
                    severity = SeverityLevel.LOW

            # Find most common product area
            product_areas = [r.product_area for r in theme_reviews if r.product_area]
            product_area = max(set(product_areas), key=product_areas.count) if product_areas else None

            theme_obj = Theme(
                id=theme_data["id"],
                name=theme_data["name"],
                description=theme_data["description"],
                review_count=review_count,
                review_percentage=review_percentage,
                sentiment_distribution=sentiment_dist,
                product_area=product_area,
                severity=severity,
                review_ids=review_ids
            )
            final_themes.append(theme_obj)

        # Sort themes by review count descending
        final_themes.sort(key=lambda t: t.review_count, reverse=True)

        return ThemeResult(
            themes=final_themes,
            unthemed_count=len(all_unthemed_ids)
        )

    def _calculate_sentiment_distribution(self, reviews: List[AnalyzedReview]) -> SentimentDistribution:
        counts = {s: 0 for s in Sentiment}
        total = len(reviews)
        
        for r in reviews:
            counts[r.sentiment] += 1
            
        percentages = {s: round((c / total) * 100, 2) for s, c in counts.items()}
        
        return SentimentDistribution(
            positive_count=counts.get(Sentiment.POSITIVE, 0),
            neutral_count=counts.get(Sentiment.NEUTRAL, 0),
            negative_count=counts.get(Sentiment.NEGATIVE, 0),
            mixed_count=counts.get(Sentiment.MIXED, 0),
            percentages=percentages
        )
