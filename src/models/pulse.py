from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from src.models.enums import Sentiment
from src.models.theme import PrioritizedTheme, TrendSignal, SentimentDistribution
from src.models.review import ReviewExcerpt

class ExecutiveSummary(BaseModel):
    bullets: List[str] = Field(default_factory=list)

class WeekMetrics(BaseModel):
    reviews_analyzed: int
    avg_star_rating: float
    sentiment_distribution: SentimentDistribution
    theme_count: int
    emerging_count: int
    critical_high_count: int
    rating_distribution: Dict[int, int] = Field(default_factory=dict)

class ThemeSection(BaseModel):
    theme: PrioritizedTheme
    summary: str
    key_quotes: List[ReviewExcerpt] = Field(default_factory=list)

class PositiveFinding(BaseModel):
    title: str
    description: str
    quotes: List[ReviewExcerpt] = Field(default_factory=list)

class PainPoint(BaseModel):
    title: str
    severity: str
    description: str
    quotes: List[ReviewExcerpt] = Field(default_factory=list)

class EmergingSignal(BaseModel):
    signal: TrendSignal
    summary: str

class FeatureRequest(BaseModel):
    title: str
    description: str
    frequency: int

class ActionItem(BaseModel):
    theme_id: str
    action: str
    priority: str
    owner_suggestion: Optional[str] = None

class MethodologySection(BaseModel):
    source: str
    app_id: str
    period: str
    timestamp: datetime
    total_fetched: int
    usable_reviews: int
    limitations: List[str] = Field(default_factory=list)

class WeeklyPulse(BaseModel):
    period_start: datetime
    period_end: datetime
    executive_summary: ExecutiveSummary
    metrics: WeekMetrics
    top_themes: List[ThemeSection] = Field(default_factory=list)
    what_users_love: List[PositiveFinding] = Field(default_factory=list)
    top_pain_points: List[PainPoint] = Field(default_factory=list)
    emerging_signals: List[EmergingSignal] = Field(default_factory=list)
    feature_requests: List[FeatureRequest] = Field(default_factory=list)
    representative_voice: List[ReviewExcerpt] = Field(default_factory=list)
    recommended_actions: List[ActionItem] = Field(default_factory=list)
    methodology: MethodologySection

class WeeklyAggregate(BaseModel):
    run_id: str
    app_id: str
    period_start: datetime
    period_end: datetime
    metrics: WeekMetrics
    themes: List[PrioritizedTheme] = Field(default_factory=list)
    doc_url: Optional[str] = None
    gmail_status: Optional[str] = None
