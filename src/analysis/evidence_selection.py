import structlog
from typing import List, Dict, Set

from src.models.theme import PrioritizedTheme, EvidenceResult
from src.models.review import AnalyzedReview, ReviewExcerpt

logger = structlog.get_logger(__name__)

class EvidenceSelectionService:
    def __init__(self, max_length: int = 150):
        self.max_length = max_length

    def select_evidence(self, prioritized_themes: List[PrioritizedTheme], all_reviews: List[AnalyzedReview], max_per_theme: int = 3, max_overall: int = 5) -> EvidenceResult:
        logger.info(f"Selecting evidence for {len(prioritized_themes)} prioritized themes.")
        
        review_lookup = {r.normalized_review.original_review.review_id: r for r in all_reviews}
        used_review_ids: Set[str] = set()
        
        theme_evidence: Dict[str, List[ReviewExcerpt]] = {}
        all_excerpts = []

        for p_theme in prioritized_themes:
            theme = p_theme.theme
            excerpts = []
            
            # Get AnalyzedReview objects for this theme
            theme_reviews = []
            for rid in theme.review_ids:
                if rid in review_lookup and rid not in used_review_ids:
                    theme_reviews.append(review_lookup[rid])
                    
            # Sort theme reviews by length of text to prefer moderate length reviews that are clear
            # Or sort by severity to get the most impactful quotes
            theme_reviews.sort(key=lambda r: len(r.normalized_review.cleaned_text), reverse=True)
            
            for review in theme_reviews:
                if len(excerpts) >= max_per_theme:
                    break
                    
                excerpt = self._create_excerpt(review, theme.id)
                excerpts.append(excerpt)
                all_excerpts.append(excerpt)
                used_review_ids.add(review.normalized_review.original_review.review_id)
                
            theme_evidence[theme.id] = excerpts

        # For overall voice, just pick the top N from the collected excerpts
        # Or sort them by a specific criteria (e.g. earliest collected)
        # Here we just take the first N
        top_overall = all_excerpts[:max_overall]

        return EvidenceResult(
            theme_evidence=theme_evidence,
            top_overall_voice=top_overall
        )

    def _create_excerpt(self, review: AnalyzedReview, theme_id: str) -> ReviewExcerpt:
        text = review.normalized_review.cleaned_text
        is_truncated = False
        
        if len(text) > self.max_length:
            text = text[:self.max_length].rsplit(' ', 1)[0] + "..."
            is_truncated = True
            
        return ReviewExcerpt(
            displayed_text=text,
            original_text=review.normalized_review.original_text,
            is_truncated=is_truncated,
            review_date=review.normalized_review.original_review.review_date,
            star_rating=review.normalized_review.original_review.star_rating,
            source_review_id=review.normalized_review.original_review.review_id,
            theme_id=theme_id
        )
