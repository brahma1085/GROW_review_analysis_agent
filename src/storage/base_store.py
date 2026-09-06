from abc import ABC, abstractmethod
from typing import List, Optional, Set

from src.models.review import RawReview, NormalizedReview, AnalyzedReview, CollectionMetadata
from src.models.theme import Theme
from src.models.pulse import WeeklyAggregate

class StorageBackend(ABC):
    @abstractmethod
    def save_raw_reviews(self, reviews: List[RawReview], run_id: str) -> None:
        pass

    @abstractmethod
    def save_normalized_reviews(self, reviews: List[NormalizedReview], run_id: str) -> None:
        pass

    @abstractmethod
    def save_analysis_results(self, results: List[AnalyzedReview], run_id: str) -> None:
        pass

    @abstractmethod
    def save_themes(self, themes: List[Theme], run_id: str) -> None:
        pass

    @abstractmethod
    def save_weekly_aggregate(self, aggregate: WeeklyAggregate) -> None:
        pass

    @abstractmethod
    def save_collection_metadata(self, metadata: CollectionMetadata) -> None:
        pass

    @abstractmethod
    def get_previous_aggregate(self, app_id: str, periods_back: int = 1) -> Optional[WeeklyAggregate]:
        pass

    @abstractmethod
    def get_processed_review_ids(self, app_id: str) -> Set[str]:
        pass

    @abstractmethod
    def get_run_history(self, app_id: str, limit: int = 5) -> List[WeeklyAggregate]:
        pass

    @abstractmethod
    def save_error_log(self, error: dict) -> None:
        pass
