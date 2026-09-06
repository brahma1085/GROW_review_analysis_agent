import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.generation.report_validator import ReportValidator
from src.generation.pulse_generator import AnalysisContext
from src.models.pulse import WeeklyPulse, WeekMetrics, ExecutiveSummary, MethodologySection
from src.models.theme import PrioritizedTheme, Theme, SentimentDistribution, SeverityLevel, PriorityLevel
from src.models.config import AgentConfig

@pytest.fixture
def mock_context():
    config = MagicMock(spec=AgentConfig)
    config.collection = MagicMock()
    config.collection.min_review_threshold = 10
    
    context = AnalysisContext(
        app_id="test.app",
        period_start=datetime.now() - timedelta(days=7),
        period_end=datetime.now(),
        total_fetched=50,
        analyzed_reviews=[],
        theme_result=MagicMock(),
        trend_result=MagicMock(),
        prioritized_themes=[],
        evidence_result=MagicMock(),
        config=config,
        llm_client=MagicMock()
    )
    return context

@pytest.fixture
def mock_pulse(mock_context):
    metrics = WeekMetrics(
        reviews_analyzed=50,
        avg_star_rating=4.2,
        sentiment_distribution=SentimentDistribution(),
        theme_count=5,
        emerging_count=2,
        critical_high_count=10,
        rating_distribution={}
    )
    
    pulse = WeeklyPulse(
        period_start=mock_context.period_start,
        period_end=mock_context.period_end,
        executive_summary=ExecutiveSummary(bullets=["Great week", "Fixed bugs"]),
        metrics=metrics,
        top_themes=[],
        what_users_love=[],
        top_pain_points=[],
        emerging_signals=[],
        feature_requests=[],
        prioritized_themes=[],
        representative_voice=[],
        recommended_actions=[],
        methodology=MethodologySection(
            source="Google Play",
            app_id="test.app",
            period="Past 7 days",
            timestamp=datetime.now(),
            total_fetched=50,
            usable_reviews=50
        )
    )
    
    return pulse

def test_validator_valid(mock_context, mock_pulse):
    validator = ReportValidator()
    result = validator.validate(mock_pulse, mock_context)
    
    # We might have warnings (no themes, no actions), but it should be valid based on strict errors
    assert result.is_valid is True
    assert len(result.warnings) > 0

def test_validator_invalid_period(mock_context, mock_pulse):
    mock_pulse.period_start = mock_pulse.period_start - timedelta(days=1)
    
    validator = ReportValidator()
    result = validator.validate(mock_pulse, mock_context)
    
    assert result.is_valid is False
    assert "Pulse period does not match context period." in result.errors

def test_validator_empty_exec_summary(mock_context, mock_pulse):
    mock_pulse.executive_summary.bullets = []
    
    validator = ReportValidator()
    result = validator.validate(mock_pulse, mock_context)
    
    assert result.is_valid is False
    assert "Executive summary is empty." in result.errors
