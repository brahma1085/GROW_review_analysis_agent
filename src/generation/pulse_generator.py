import json
import structlog
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.pulse import (
    WeeklyPulse, ExecutiveSummary, WeekMetrics, ThemeSection,
    PositiveFinding, PainPoint, EmergingSignal, FeatureRequest,
    ActionItem, MethodologySection
)
from src.models.review import AnalyzedReview, ReviewCategory
from src.models.theme import ThemeResult, TrendResult, PrioritizedTheme, PriorityLevel, Sentiment, SeverityLevel
from src.models.config import AgentConfig
from src.analysis.llm_client import LLMClient
from src.analysis.evidence_selection import EvidenceResult
from src.prompts.pulse_generation_prompt import PULSE_GENERATION_SYSTEM_PROMPT, PULSE_GENERATION_USER_PROMPT

logger = structlog.get_logger(__name__)

@dataclass
class AnalysisContext:
    app_id: str
    period_start: datetime
    period_end: datetime
    total_fetched: int
    analyzed_reviews: List[AnalyzedReview]
    theme_result: ThemeResult
    trend_result: TrendResult
    prioritized_themes: List[PrioritizedTheme]
    evidence_result: EvidenceResult
    config: AgentConfig
    llm_client: LLMClient

class PulseGenerator:
    def __init__(self):
        pass

    def generate_pulse(self, context: AnalysisContext) -> WeeklyPulse:
        logger.info("Generating Weekly Pulse report...")

        # 1. Generate Metrics
        metrics = self._generate_metrics(context)

        # 2. Extract Top Themes
        top_themes = self._generate_top_themes(context)
        
        # 3. Extract What Users Love
        what_users_love = self._generate_what_users_love(context)
        
        # 4. Extract Pain Points
        top_pain_points = self._generate_pain_points(context)
        
        # 5. Extract Emerging Signals
        emerging_signals = self._generate_emerging_signals(context)
        
        # 6. Extract Feature Requests
        feature_requests = self._generate_feature_requests(context)
        
        # 7. Methodology
        methodology = self._generate_methodology(context)

        # 8. Use LLM to generate Executive Summary & Recommendations
        exec_summary, recommended_actions = self._generate_llm_prose(context)

        pulse = WeeklyPulse(
            period_start=context.period_start,
            period_end=context.period_end,
            executive_summary=exec_summary,
            metrics=metrics,
            top_themes=top_themes,
            what_users_love=what_users_love,
            top_pain_points=top_pain_points,
            emerging_signals=emerging_signals,
            feature_requests=feature_requests,
            prioritized_themes=context.prioritized_themes,
            representative_voice=context.evidence_result.top_overall_voice,
            recommended_actions=recommended_actions,
            methodology=methodology
        )

        return pulse

    def _generate_metrics(self, context: AnalysisContext) -> WeekMetrics:
        reviews = context.analyzed_reviews
        if not reviews:
            # Fallback when no reviews
            from src.models.theme import SentimentDistribution
            dist = SentimentDistribution(
                positive_count=0, neutral_count=0, negative_count=0, mixed_count=0,
                percentages={
                    Sentiment.POSITIVE: 0.0,
                    Sentiment.NEUTRAL: 0.0,
                    Sentiment.NEGATIVE: 0.0,
                    Sentiment.MIXED: 0.0
                }
            )
            return WeekMetrics(
                reviews_analyzed=0,
                avg_star_rating=0.0,
                sentiment_distribution=dist,
                theme_count=0,
                emerging_count=0,
                critical_high_count=0,
                rating_distribution={}
            )

        total = len(reviews)
        avg_rating = sum(r.normalized_review.original_review.star_rating for r in reviews) / total
        
        # Sentiment distribution across all reviews
        pos = sum(1 for r in reviews if r.sentiment == Sentiment.POSITIVE)
        neu = sum(1 for r in reviews if r.sentiment == Sentiment.NEUTRAL)
        neg = sum(1 for r in reviews if r.sentiment == Sentiment.NEGATIVE)
        mix = sum(1 for r in reviews if r.sentiment == Sentiment.MIXED)
        
        from src.models.theme import SentimentDistribution
        dist = SentimentDistribution(
            positive_count=pos, neutral_count=neu, negative_count=neg, mixed_count=mix,
            percentages={
                Sentiment.POSITIVE: round(pos/total*100, 2),
                Sentiment.NEUTRAL: round(neu/total*100, 2),
                Sentiment.NEGATIVE: round(neg/total*100, 2),
                Sentiment.MIXED: round(mix/total*100, 2)
            }
        )

        rating_dist = {i: 0 for i in range(1, 6)}
        for r in reviews:
            rating_dist[r.normalized_review.original_review.star_rating] += 1

        crit_high = sum(1 for r in reviews if r.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH])

        return WeekMetrics(
            reviews_analyzed=total,
            avg_star_rating=round(avg_rating, 2),
            sentiment_distribution=dist,
            theme_count=len(context.theme_result.themes),
            emerging_count=len(context.trend_result.emerging),
            critical_high_count=crit_high,
            rating_distribution=rating_dist
        )

    def _generate_top_themes(self, context: AnalysisContext) -> List[ThemeSection]:
        sections = []
        for pt in context.prioritized_themes[:5]:
            evidence = context.evidence_result.theme_evidence.get(pt.theme.id, [])
            sections.append(ThemeSection(
                theme=pt,
                summary=pt.theme.description,
                key_quotes=evidence
            ))
        return sections

    def _generate_what_users_love(self, context: AnalysisContext) -> List[PositiveFinding]:
        findings = []
        for pt in context.prioritized_themes:
            if pt.theme.sentiment_distribution.percentages.get(Sentiment.POSITIVE, 0) > 50:
                evidence = context.evidence_result.theme_evidence.get(pt.theme.id, [])
                findings.append(PositiveFinding(
                    title=pt.theme.name,
                    description=pt.theme.description,
                    quotes=evidence
                ))
        return findings

    def _generate_pain_points(self, context: AnalysisContext) -> List[PainPoint]:
        points = []
        for pt in context.prioritized_themes:
            if pt.theme.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM] and pt.theme.sentiment_distribution.percentages.get(Sentiment.NEGATIVE, 0) > 30:
                evidence = context.evidence_result.theme_evidence.get(pt.theme.id, [])
                points.append(PainPoint(
                    title=pt.theme.name,
                    severity=pt.theme.severity.value,
                    description=pt.theme.description,
                    quotes=evidence
                ))
        return points

    def _generate_emerging_signals(self, context: AnalysisContext) -> List[EmergingSignal]:
        signals = []
        for signal in context.trend_result.emerging:
            signals.append(EmergingSignal(
                signal=signal,
                summary=signal.interpretation
            ))
        for signal in context.trend_result.new_themes:
            signals.append(EmergingSignal(
                signal=signal,
                summary=f"New theme detected: {signal.theme.description}"
            ))
        return signals[:5]

    def _generate_feature_requests(self, context: AnalysisContext) -> List[FeatureRequest]:
        requests = []
        for theme in context.theme_result.themes:
            if "feature" in theme.name.lower() or "request" in theme.description.lower() or "add" in theme.name.lower():
                requests.append(FeatureRequest(
                    title=theme.name,
                    description=theme.description,
                    frequency=theme.review_count
                ))
        return requests

    def _generate_methodology(self, context: AnalysisContext) -> MethodologySection:
        return MethodologySection(
            source="Google Play Store",
            app_id=context.app_id,
            period=f"{context.period_start.strftime('%Y-%m-%d')} to {context.period_end.strftime('%Y-%m-%d')}",
            timestamp=datetime.now(),
            total_fetched=context.total_fetched,
            usable_reviews=len(context.analyzed_reviews),
            limitations=["Limited to reviews collected in English", "Sentiment analysis is AI-generated and may have edge case errors"]
        )

    def _generate_llm_prose(self, context: AnalysisContext) -> tuple[ExecutiveSummary, List[ActionItem]]:
        if not context.prioritized_themes:
            return ExecutiveSummary(bullets=["No themes detected in this period."]), []

        analysis_data = {
            "top_themes": [
                {
                    "id": pt.theme.id,
                    "name": pt.theme.name,
                    "priority": pt.priority.value,
                    "severity": pt.theme.severity.value,
                    "review_percentage": pt.theme.review_percentage
                } for pt in context.prioritized_themes[:5]
            ],
            "trends": [
                {
                    "theme_name": ts.theme.name,
                    "type": ts.trend_type.value,
                    "interpretation": ts.interpretation
                } for ts in context.trend_result.emerging + context.trend_result.new_themes
            ],
            "metrics": {
                "total_reviews": len(context.analyzed_reviews),
                "critical_high_count": sum(1 for r in context.analyzed_reviews if r.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH])
            }
        }

        prompt = PULSE_GENERATION_USER_PROMPT.format(analysis_data_json=json.dumps(analysis_data, indent=2))
        
        try:
            logger.info("Calling LLM for Executive Summary and Recommended Actions...")
            response = context.llm_client.analyze_batch_json(
                prompt=prompt,
                system_prompt=PULSE_GENERATION_SYSTEM_PROMPT
            )
            
            exec_bullets = response.get("executive_summary", ["Unable to generate executive summary."])
            actions_data = response.get("recommended_actions", [])
            
            exec_summary = ExecutiveSummary(bullets=exec_bullets)
            
            actions = []
            for act in actions_data:
                actions.append(ActionItem(
                    theme_id=act.get("theme_id") or "general",
                    action=act.get("action", "No action specified"),
                    priority="HIGH",
                    owner_suggestion=act.get("owner_suggestion")
                ))
                
            return exec_summary, actions
            
        except Exception as e:
            logger.error(f"Error generating LLM prose: {e}")
            return ExecutiveSummary(bullets=["Error generating summary."]), []
