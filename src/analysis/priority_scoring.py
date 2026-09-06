import structlog
from typing import List, Dict

from src.models.theme import ThemeResult, TrendResult, PrioritizedTheme, Theme, TrendSignal
from src.models.enums import PriorityLevel, SeverityLevel

logger = structlog.get_logger(__name__)

class PriorityScoringService:
    def __init__(self, config: dict = None):
        self.config = config or {}
        # Default weights
        self.weights = {
            "frequency": 0.25,
            "negative_sentiment": 0.25,
            "severity_language": 0.25,
            "growth": 0.25
        }

    def score_themes(self, theme_result: ThemeResult, trend_result: TrendResult) -> List[PrioritizedTheme]:
        logger.info(f"Scoring {len(theme_result.themes)} themes for prioritization.")
        
        # Build lookup for trend signals
        trend_signals: Dict[str, TrendSignal] = {}
        all_signals = trend_result.emerging + trend_result.growing + trend_result.declining + trend_result.persistent + trend_result.new_themes
        for signal in all_signals:
            trend_signals[signal.theme.id] = signal

        prioritized = []

        for theme in theme_result.themes:
            score, breakdown, rationale = self._calculate_score(theme, trend_signals.get(theme.id))
            priority = self._map_score_to_priority(score)
            
            prioritized.append(PrioritizedTheme(
                theme=theme,
                priority=priority,
                score=score,
                factor_breakdown=breakdown,
                rationale=rationale
            ))
            
        # Sort by score descending
        prioritized.sort(key=lambda x: x.score, reverse=True)
        return prioritized

    def _calculate_score(self, theme: Theme, trend: TrendSignal = None):
        breakdown = {}
        
        # 1. Frequency (Normalize percentage to 0-1)
        freq_score = min(theme.review_percentage / 50.0, 1.0) # Assume 50% is max expected freq
        breakdown["frequency"] = freq_score * self.weights["frequency"]
        
        # 2. Negative Sentiment
        neg_ratio = (theme.sentiment_distribution.negative_count / theme.review_count) if theme.review_count > 0 else 0
        breakdown["negative_sentiment"] = neg_ratio * self.weights["negative_sentiment"]
        
        # 3. Severity Language
        severity_mapping = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.75,
            SeverityLevel.MEDIUM: 0.5,
            SeverityLevel.LOW: 0.25,
            SeverityLevel.INFORMATIONAL: 0.0
        }
        sev_score = severity_mapping.get(theme.severity, 0.0)
        breakdown["severity_language"] = sev_score * self.weights["severity_language"]
        
        # 4. Growth
        growth_score = 0.0
        if trend and trend.volume_change_pct is not None:
            # Cap at 100% growth
            growth_score = max(min(trend.volume_change_pct / 100.0, 1.0), 0.0)
        elif trend and trend.trend_type.value == "new":
            growth_score = 0.5 # New themes get a default bump
            
        breakdown["growth"] = growth_score * self.weights["growth"]
        
        # Total Score
        total_score = sum(breakdown.values())
        
        # Generate Rationale
        top_factor = max(breakdown, key=breakdown.get) if total_score > 0 else None
        
        if total_score > 0.75:
            rationale = f"Critical priority driven primarily by high {top_factor.replace('_', ' ')}."
        elif total_score > 0.5:
            rationale = f"High priority due to {top_factor.replace('_', ' ')}."
        elif total_score > 0.25:
            rationale = "Medium priority. Needs monitoring."
        else:
            rationale = "Low priority. Routine issue."

        return round(total_score, 2), breakdown, rationale

    def _map_score_to_priority(self, score: float) -> PriorityLevel:
        if score >= 0.75:
            return PriorityLevel.CRITICAL
        elif score >= 0.50:
            return PriorityLevel.HIGH
        elif score >= 0.25:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
