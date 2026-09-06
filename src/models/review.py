from datetime import datetime
from typing import List, Optional, Set
from pydantic import BaseModel, Field

from src.models.enums import Sentiment, SeverityLevel, ReviewCategory, CollectionStatus

class RawReview(BaseModel):
    review_id: str
    app_id: str
    source: str
    reviewer_name: Optional[str] = None
    review_text: str
    star_rating: int
    review_date: datetime
    developer_reply: Optional[str] = None
    detected_language: Optional[str] = None
    app_version: Optional[str] = None
    source_url: Optional[str] = None
    collected_at: datetime

class NormalizedReview(BaseModel):
    original_review: RawReview
    original_text: str
    cleaned_text: str
    detected_language: str
    is_usable: bool
    content_hash: str
    normalization_notes: List[str] = Field(default_factory=list)

class AnalyzedReview(BaseModel):
    normalized_review: NormalizedReview
    sentiment: Sentiment
    sentiment_confidence: float
    categories: List[ReviewCategory] = Field(default_factory=list)
    product_area: Optional[str] = None
    severity: SeverityLevel
    intent: Optional[str] = None
    key_phrases: List[str] = Field(default_factory=list)

class ReviewExcerpt(BaseModel):
    displayed_text: str
    original_text: str
    is_truncated: bool
    review_date: datetime
    star_rating: int
    source_review_id: str
    theme_id: Optional[str] = None

class CollectionMetadata(BaseModel):
    app_id: str
    start_date: datetime
    end_date: datetime
    total_fetched: int
    source: str
    status: CollectionStatus
    error_message: Optional[str] = None

class CollectionError(BaseModel):
    error_type: str
    message: str
    details: Optional[str] = None

class CollectionResult(BaseModel):
    reviews: List[RawReview] = Field(default_factory=list)
    metadata: CollectionMetadata
    errors: List[CollectionError] = Field(default_factory=list)

class NormalizationStats(BaseModel):
    total_processed: int = 0
    total_usable: int = 0
    total_discarded: int = 0
    discard_reasons: dict[str, int] = Field(default_factory=dict)

class NormalizationResult(BaseModel):
    normalized: List[NormalizedReview] = Field(default_factory=list)
    stats: NormalizationStats

class DedupRecord(BaseModel):
    review_id: str
    content_hash: str
    matched_with: Optional[str] = None
    similarity_score: float = 1.0
    reason: str = "exact"

class DeduplicationResult(BaseModel):
    unique_reviews: List[NormalizedReview] = Field(default_factory=list)
    removed_count: int = 0
    details: List[DedupRecord] = Field(default_factory=list)
