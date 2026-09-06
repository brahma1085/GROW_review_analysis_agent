from typing import List, Set, Dict
from rapidfuzz import fuzz

from src.models.review import NormalizedReview, DeduplicationResult, DedupRecord
from src.observability.logger import get_logger

logger = get_logger(__name__)

class ReviewDeduplicator:
    def __init__(self, exact_match: bool = True, near_duplicate_threshold: float = 0.85):
        self.exact_match = exact_match
        self.near_duplicate_threshold = near_duplicate_threshold
        
    def deduplicate(self, reviews: List[NormalizedReview], historical_ids: Set[str] = None) -> DeduplicationResult:
        if historical_ids is None:
            historical_ids = set()
            
        result = DeduplicationResult()
        
        # We will keep track of unique reviews and hashes
        unique_reviews = []
        seen_hashes: Dict[str, str] = {} # hash -> review_id
        
        for review in reviews:
            rid = review.original_review.review_id
            chash = review.content_hash
            
            # 1. Cross-period deduplication
            if rid in historical_ids or chash in historical_ids:
                result.removed_count += 1
                result.details.append(DedupRecord(
                    review_id=rid,
                    content_hash=chash,
                    reason="historical"
                ))
                continue
                
            # 2. Exact match within the batch
            if self.exact_match and chash in seen_hashes:
                result.removed_count += 1
                result.details.append(DedupRecord(
                    review_id=rid,
                    content_hash=chash,
                    matched_with=seen_hashes[chash],
                    reason="exact"
                ))
                continue
                
            # 3. Near duplicate within the batch
            is_near_dup = False
            matched_id = None
            similarity = 0.0
            
            if self.near_duplicate_threshold > 0:
                for existing in unique_reviews:
                    # Compare cleaned texts
                    score = fuzz.ratio(review.cleaned_text, existing.cleaned_text) / 100.0
                    if score >= self.near_duplicate_threshold:
                        is_near_dup = True
                        matched_id = existing.original_review.review_id
                        similarity = score
                        break
                        
            if is_near_dup:
                result.removed_count += 1
                result.details.append(DedupRecord(
                    review_id=rid,
                    content_hash=chash,
                    matched_with=matched_id,
                    similarity_score=similarity,
                    reason="near_duplicate"
                ))
                continue
                
            # If it passes all checks, it's unique
            unique_reviews.append(review)
            seen_hashes[chash] = rid
            
        result.unique_reviews = unique_reviews
        logger.info("Deduplication complete", initial=len(reviews), unique=len(unique_reviews), removed=result.removed_count)
        return result
