import pytest
from unittest.mock import MagicMock, AsyncMock
from src.delivery.pipeline import DeliveryPipeline
from src.models.pulse import WeeklyPulse, ExecutiveSummary, WeekMetrics, MethodologySection, ThemeSection, PositiveFinding, PainPoint, EmergingSignal, FeatureRequest, ActionItem
from src.models.theme import SentimentDistribution
from src.models.review import ReviewExcerpt
import datetime

@pytest.fixture
def mock_config():
    from src.models.config import DeliveryConfig, GoogleDocsConfig, GmailConfig, McpConfig
    return DeliveryConfig(
        google_docs=GoogleDocsConfig(document_id="folder_123"),
        gmail=GmailConfig(create_draft=True),
        mcp=McpConfig(server_url="test", api_key="test")
    )

@pytest.fixture
def mock_pulse():
    return WeeklyPulse(
        period_start=datetime.datetime.now(),
        period_end=datetime.datetime.now(),
        executive_summary=ExecutiveSummary(bullets=["Summary 1"]),
        metrics=WeekMetrics(
            reviews_analyzed=100,
            avg_star_rating=4.5,
            sentiment_distribution=SentimentDistribution(positive_count=80, neutral_count=10, negative_count=10, mixed_count=0, percentages={}),
            theme_count=5,
            emerging_count=1,
            critical_high_count=0,
            rating_distribution={}
        ),
        top_themes=[],
        what_users_love=[],
        top_pain_points=[],
        emerging_signals=[],
        feature_requests=[],
        representative_voice=[],
        recommended_actions=[],
        methodology=MethodologySection(source="play", app_id="app", period="P1W", timestamp=datetime.datetime.now(), total_fetched=110, usable_reviews=100, limitations=[])
    )

@pytest.mark.asyncio
async def test_end_to_end_delivery(mock_config, mock_pulse):
    pipeline = DeliveryPipeline(mock_config)
    
    mock_docs_adapter = AsyncMock()
    mock_gmail_adapter = AsyncMock()
    
    pipeline.docs_adapter = mock_docs_adapter
    pipeline.gmail_adapter = mock_gmail_adapter
    
    doc_url, email_status = await pipeline.deliver(mock_pulse)
    
    assert doc_url == "delivered_to_mcp"
    assert email_status is True
    
    mock_docs_adapter.deliver_pulse.assert_called_once()
    mock_gmail_adapter.draft_pulse_email.assert_called_once()
