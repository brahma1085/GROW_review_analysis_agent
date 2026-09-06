from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from src.models.enums import Sentiment, PriorityLevel, SeverityLevel, TrendType
from src.models.review import ReviewExcerpt

class SentimentDistribution(BaseModel):
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    mixed_count: int = 0
    percentages: Dict[Sentiment, float] = Field(default_factory=dict)

class SentimentShift(BaseModel):
    previous: float
    current: float
    delta: float

class Theme(BaseModel):
    id: str
    name: str
    description: str
    review_count: int
    review_percentage: float
    sentiment_distribution: SentimentDistribution
    product_area: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.INFORMATIONAL
    is_recurring: bool = False
    is_emerging: bool = False
    recommended_action: Optional[str] = None
    review_ids: List[str] = Field(default_factory=list)

class PrioritizedTheme(BaseModel):
    theme: Theme
    priority: PriorityLevel
    score: float
    factor_breakdown: Dict[str, float] = Field(default_factory=dict)
    rationale: str

class TrendSignal(BaseModel):
    theme: Theme
    trend_type: TrendType
    evidence: str
    interpretation: str
    recommendation: str
    volume_change_pct: Optional[float] = None
    sentiment_change: Optional[SentimentShift] = None

class TrendResult(BaseModel):
    emerging: List[TrendSignal] = Field(default_factory=list)
    growing: List[TrendSignal] = Field(default_factory=list)
    declining: List[TrendSignal] = Field(default_factory=list)
    persistent: List[TrendSignal] = Field(default_factory=list)
    new_themes: List[TrendSignal] = Field(default_factory=list)
    comparison_period: Optional[str] = None
    data_availability_note: Optional[str] = None

class ThemeResult(BaseModel):
    themes: List[Theme] = Field(default_factory=list)
    unthemed_count: int = 0

class EvidenceResult(BaseModel):
    theme_evidence: Dict[str, List[ReviewExcerpt]] = Field(default_factory=dict)
    top_overall_voice: List[ReviewExcerpt] = Field(default_factory=list)
