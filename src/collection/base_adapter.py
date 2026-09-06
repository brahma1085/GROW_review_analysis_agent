from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from src.models.review import CollectionResult

class ReviewSourceAdapter(ABC):
    @abstractmethod
    def fetch_reviews(self, app_id: str, start_date: datetime, end_date: datetime, max_count: int) -> CollectionResult:
        """
        Fetch reviews for a given application within a date range.
        
        Args:
            app_id: The identifier for the application (e.g. package ID)
            start_date: Fetch reviews from this date onwards (inclusive)
            end_date: Fetch reviews up to this date (inclusive)
            max_count: Maximum number of reviews to fetch
            
        Returns:
            CollectionResult containing the fetched reviews, metadata, and any errors.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of the review source (e.g. 'google_play')."""
        pass

    @abstractmethod
    def supports_incremental(self) -> bool:
        """Return True if this source supports incremental fetching natively."""
        pass
