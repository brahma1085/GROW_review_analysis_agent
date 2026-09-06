import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.generation.pulse_generator import PulseGenerator, AnalysisContext
from src.models.pulse import WeeklyPulse, WeekMetrics
from src.models.review import AnalyzedReview, NormalizedReview, RawReview
from src.models.theme import ThemeResult, TrendResult, PrioritizedTheme, Theme, SentimentDistribution, TrendSignal, TrendType, PriorityLevel, Sentiment, SeverityLevel
from src.analysis.evidence_selection import EvidenceResult
from src.models.config import AgentConfig

@pytest.fixture
def mock_context():
    # Construct a minimal AnalysisContext for testing
    config = MagicMock(spec=AgentConfig)
    config.collection = MagicMock()
    config.collection.min_review_threshold = 10
    theme1 = Theme(
        id="t1", name="Bugs", description="App bugs", review_count=5, review_percentage=50.0,
        sentiment_distribution=SentimentDistribution(positive_count=0, neutral_count=0, negative_count=5, mixed_count=0, percentages={}),
        product_area="Core", severity=SeverityLevel.HIGH, review_ids=["r1"]
    )
    
    pt1 = PrioritizedTheme(
        theme=theme1, priority=PriorityLevel.HIGH, score=0.8, factor_breakdown={}, rationale="Bad bugs"
    )
    
    context = AnalysisContext(
        app_id="test.app",
        period_start=datetime.now() - timedelta(days=7),
        period_end=datetime.now(),
        total_fetched=10,
        analyzed_reviews=[],
        theme_result=ThemeResult(themes=[theme1], unthemed_count=0),
        trend_result=TrendResult(emerging=[], growing=[], declining=[], persistent=[], new_themes=[], comparison_period=None, data_availability_note=None),
        prioritized_themes=[pt1],
        evidence_result=EvidenceResult(theme_evidence={}, top_voice_excerpts=[]),
        config=config,
        llm_client=MagicMock()
    )
    
    # Mock LLM response
    context.llm_client.analyze_batch_json.return_value = {
        "executive_summary": ["Exec summary 1"],
        "recommended_actions": [{"theme_id": "t1", "action": "Fix bugs", "rationale": "Because bugs are bad"}]
    }
    
    return context

def test_generate_pulse(mock_context):
    generator = PulseGenerator()
    pulse = generator.generate_pulse(mock_context)
    
    assert isinstance(pulse, WeeklyPulse)
    assert len(pulse.executive_summary.bullets) == 1
    assert pulse.executive_summary.bullets[0] == "Exec summary 1"
    assert len(pulse.top_themes) == 1
    assert pulse.top_themes[0].theme.theme.id == "t1"
    assert len(pulse.recommended_actions) == 1
    assert pulse.recommended_actions[0].action == "Fix bugs"

