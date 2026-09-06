from datetime import datetime
from typing import Optional, List, Dict, Any
import time

from google_play_scraper import Sort, reviews

from src.collection.base_adapter import ReviewSourceAdapter
from src.models.review import RawReview, CollectionResult, CollectionMetadata, CollectionError
from src.models.enums import CollectionStatus
from src.observability.logger import get_logger

logger = get_logger(__name__)

class GooglePlayAdapter(ReviewSourceAdapter):
    def __init__(self, max_retries: int = 3, retry_backoff_seconds: int = 2):
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def get_source_name(self) -> str:
        return "google_play"

    def supports_incremental(self) -> bool:
        return True

    def fetch_reviews(
        self, 
        app_id: str, 
        start_date: datetime, 
        end_date: datetime, 
        max_count: int
    ) -> CollectionResult:
        """
        Fetches reviews from Google Play Store using google-play-scraper.
        Handles pagination, date filtering, and rate limiting/retries.
        """
        all_fetched_reviews: List[RawReview] = []
        errors: List[CollectionError] = []
        continuation_token = None
        
        logger.info("Starting Google Play review fetch", app_id=app_id, start=start_date, end=end_date, max_count=max_count)
        
        try:
            while len(all_fetched_reviews) < max_count:
                batch_reviews, continuation_token = self._fetch_batch_with_retry(
                    app_id, continuation_token
                )
                
                if not batch_reviews:
                    logger.info("No more reviews returned from scraper", app_id=app_id)
                    break
                
                # Process the batch
                for r in batch_reviews:
                    review_date = r.get("at")
                    
                    # Some reviews might not have a date, skip if we strictly filter by date
                    if not review_date:
                        continue
                        
                    # Stop fetching entirely if we go past the start_date in NEWEST sort
                    # Sort.NEWEST implies they are generally ordered descending by date.
                    if review_date < start_date:
                        logger.debug("Reached reviews older than start_date, stopping fetch", 
                                     review_date=review_date, start_date=start_date)
                        continuation_token = None # Force break outer loop
                        break
                        
                    # Only include if within range
                    if start_date <= review_date <= end_date:
                        raw_review = self._map_to_raw_review(r, app_id)
                        all_fetched_reviews.append(raw_review)
                        
                        if len(all_fetched_reviews) >= max_count:
                            break
                            
                if continuation_token is None:
                    break
                    
        except Exception as e:
            logger.error("Failed to fetch reviews", error=str(e), app_id=app_id)
            errors.append(CollectionError(error_type="FetchError", message=str(e)))
            
        status = CollectionStatus.SUCCESS
        if errors and len(all_fetched_reviews) == 0:
            status = CollectionStatus.FAILED
        elif errors:
            status = CollectionStatus.PARTIAL
            
        metadata = CollectionMetadata(
            app_id=app_id,
            start_date=start_date,
            end_date=end_date,
            total_fetched=len(all_fetched_reviews),
            source=self.get_source_name(),
            status=status,
            error_message=errors[0].message if errors else None
        )
        
        return CollectionResult(
            reviews=all_fetched_reviews,
            metadata=metadata,
            errors=errors
        )
        
    def _fetch_batch_with_retry(self, app_id: str, continuation_token: Any) -> tuple[List[Dict[str, Any]], Any]:
        """Fetch a single page of reviews with retry logic."""
        retries = 0
        while retries <= self.max_retries:
            try:
                result, token = reviews(
                    app_id,
                    lang='en', # default to en, can be parameterized
                    country='in', # default to in, can be parameterized
                    sort=Sort.NEWEST,
                    count=100,
                    continuation_token=continuation_token
                )
                return result, token
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise e
                logger.warning("Scraper fetch failed, retrying", retry=retries, error=str(e))
                time.sleep(self.retry_backoff_seconds * retries)
        
        return [], None
        
    def _map_to_raw_review(self, scraper_review: dict, app_id: str) -> RawReview:
        """Map the dictionary returned by google-play-scraper to our RawReview model."""
        return RawReview(
            review_id=scraper_review.get("reviewId", ""),
            app_id=app_id,
            source=self.get_source_name(),
            reviewer_name=scraper_review.get("userName"),
            review_text=scraper_review.get("content", ""),
            star_rating=scraper_review.get("score", 0),
            review_date=scraper_review.get("at"),
            developer_reply=scraper_review.get("replyContent"),
            app_version=scraper_review.get("reviewCreatedVersion"),
            collected_at=datetime.now()
        )
