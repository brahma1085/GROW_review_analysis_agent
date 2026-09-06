import hashlib
from typing import List, Set
from datetime import datetime

from src.models.review import RawReview, CollectionResult
from src.collection.base_adapter import ReviewSourceAdapter
from src.storage.base_store import StorageBackend
from src.observability.logger import get_logger

logger = get_logger(__name__)

class IncrementalManager:
    def __init__(self, adapter: ReviewSourceAdapter, storage: StorageBackend):
        self.adapter = adapter
        self.storage = storage

    def collect_new_reviews(self, app_id: str, start_date: datetime, end_date: datetime, max_count: int, run_id: str) -> CollectionResult:
        """
        Orchestrates fetching reviews, filtering out previously processed ones,
        and updating the storage state.
        """
        logger.info("Starting incremental collection", app_id=app_id, run_id=run_id)
        
        # 1. Load previously processed IDs
        processed_ids = self.storage.get_processed_review_ids(app_id)
        logger.info("Loaded processed history", count=len(processed_ids))
        
        # 2. Fetch new reviews
        collection_result = self.adapter.fetch_reviews(
            app_id=app_id,
            start_date=start_date,
            end_date=end_date,
            max_count=max_count
        )
        
        if not collection_result.reviews:
            logger.info("No reviews fetched")
            self._save_metadata(collection_result, run_id)
            return collection_result

        # 3. Filter out already processed reviews
        new_reviews = []
        for review in collection_result.reviews:
            stable_id = self._generate_stable_id(review)
            
            # Ensure the review has the stable ID set
            if not review.review_id:
                review.review_id = stable_id
                
            # Fallback check against stable_id
            if review.review_id not in processed_ids and stable_id not in processed_ids:
                new_reviews.append(review)
                # Keep processed_ids updated in memory to catch duplicates in the same batch
                processed_ids.add(review.review_id)
                processed_ids.add(stable_id)
        
        logger.info("Incremental filtering completed", 
                    fetched=len(collection_result.reviews), 
                    new=len(new_reviews))
        
        # Update the result with only the new reviews
        collection_result.reviews = new_reviews
        
        # 4. Save to storage
        if new_reviews:
            self.storage.save_raw_reviews(new_reviews, run_id)
            
        self._save_metadata(collection_result, run_id)
        
        return collection_result
        
    def _save_metadata(self, result: CollectionResult, run_id: str):
        # We might want to inject run_id into metadata if needed, but for now we just save it.
        # Ensure we record how many were actually new
        result.metadata.total_fetched = len(result.reviews) 
        self.storage.save_collection_metadata(result.metadata)

    def _generate_stable_id(self, review: RawReview) -> str:
        """Generate a stable content hash for reviews lacking a consistent ID."""
        if review.review_id:
            return review.review_id
            
        # If the source didn't provide a unique ID, create a stable hash
        content = f"{review.reviewer_name or ''}|{review.review_text}|{review.star_rating}|{review.review_date.isoformat()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
