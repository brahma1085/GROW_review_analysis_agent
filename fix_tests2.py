import datetime

content_pipeline = """import pytest
from unittest.mock import MagicMock
from src.delivery.pipeline import DeliveryPipeline
from src.models.pulse import WeeklyPulse, ExecutiveSummary, WeekMetrics, MethodologySection
from src.models.theme import SentimentDistribution
import datetime

@pytest.fixture
def mock_config():
    from src.models.config import DeliveryConfig, GoogleDocsConfig, GmailConfig
    return DeliveryConfig(
        enabled=True,
        google_docs=GoogleDocsConfig(enabled=True, folder_id="folder_123"),
        gmail=GmailConfig(enabled=True, to_email="test@example.com")
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

def test_end_to_end_delivery(mock_config, mock_pulse):
    mock_docs_adapter = MagicMock()
    mock_docs_adapter.create_document.return_value = "http://docs.google.com/doc_123"
    
    mock_gmail_adapter = MagicMock()
    mock_gmail_adapter.create_draft.return_value = True
    
    pipeline = DeliveryPipeline(mock_config)
    pipeline.docs_adapter = mock_docs_adapter
    pipeline.gmail_adapter = mock_gmail_adapter
    
    doc_url, email_status = pipeline.deliver(mock_pulse)
    
    assert doc_url == "http://docs.google.com/doc_123"
    assert email_status is True
    
    mock_docs_adapter.create_document.assert_called_once_with(mock_pulse)
    mock_gmail_adapter.create_draft.assert_called_once_with(mock_pulse)
"""

with open("tests/integration/test_delivery_pipeline.py", "w") as f:
    f.write(content_pipeline)
