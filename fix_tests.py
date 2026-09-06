import datetime

content = """import pytest
from unittest.mock import MagicMock
from src.delivery.gmail_adapter import GmailAdapter
from src.models.pulse import WeeklyPulse, ExecutiveSummary, WeekMetrics, MethodologySection, ThemeSection, PositiveFinding, PainPoint, EmergingSignal, FeatureRequest, ActionItem
from src.models.theme import SentimentDistribution
from src.models.review import ReviewExcerpt
import datetime

@pytest.fixture
def mock_config():
    return {
        "mcp_server_url": "http://localhost:8080",
        "mcp_api_key": "test_key",
        "to_email": "test@example.com"
    }

@pytest.fixture
def sample_pulse():
    return WeeklyPulse(
        period_start=datetime.datetime.now(),
        period_end=datetime.datetime.now(),
        executive_summary=ExecutiveSummary(bullets=["Summary 1", "Summary 2"]),
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

def test_gmail_create_draft(mock_config, sample_pulse):
    mock_client = MagicMock()
    mock_client.call_tool.return_value = {"status": "success", "draft_id": "draft_123"}
    
    adapter = GmailAdapter(mock_config)
    adapter._client = mock_client
    
    result = adapter.create_draft(sample_pulse)
    
    assert result is True
    mock_client.call_tool.assert_called_once()

def test_gmail_failure(mock_config, sample_pulse):
    mock_client = MagicMock()
    mock_client.call_tool.side_effect = Exception("API Error")
    
    adapter = GmailAdapter(mock_config)
    adapter._client = mock_client
    
    result = adapter.create_draft(sample_pulse)
    
    assert result is False
"""

with open("tests/unit/test_gmail_adapter.py", "w") as f:
    f.write(content)

content_docs = """import pytest
from unittest.mock import MagicMock
from src.delivery.google_docs_adapter import GoogleDocsAdapter
from src.models.pulse import WeeklyPulse, ExecutiveSummary, WeekMetrics, MethodologySection, ThemeSection, PositiveFinding, PainPoint, EmergingSignal, FeatureRequest, ActionItem
from src.models.theme import SentimentDistribution
import datetime

@pytest.fixture
def mock_config():
    return {
        "mcp_server_url": "http://localhost:8080",
        "mcp_api_key": "test_key",
        "folder_id": "folder_123"
    }

@pytest.fixture
def sample_pulse():
    return WeeklyPulse(
        period_start=datetime.datetime.now(),
        period_end=datetime.datetime.now(),
        executive_summary=ExecutiveSummary(bullets=["Summary 1", "Summary 2"]),
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

def test_google_docs_create(mock_config, sample_pulse):
    mock_client = MagicMock()
    mock_client.call_tool.return_value = {"status": "success", "document_id": "doc_123", "url": "http://docs.google.com/doc_123"}
    
    adapter = GoogleDocsAdapter(mock_config)
    adapter._client = mock_client
    
    url = adapter.create_document(sample_pulse)
    
    assert url == "http://docs.google.com/doc_123"
    mock_client.call_tool.assert_called_once()

def test_google_docs_append(mock_config, sample_pulse):
    mock_client = MagicMock()
    mock_client.call_tool.return_value = {"status": "success"}
    
    adapter = GoogleDocsAdapter(mock_config)
    adapter._client = mock_client
    
    result = adapter.append_to_document("doc_123", sample_pulse)
    
    assert result is True
    mock_client.call_tool.assert_called_once()

def test_google_docs_failure(mock_config, sample_pulse):
    mock_client = MagicMock()
    mock_client.call_tool.side_effect = Exception("API Error")
    
    adapter = GoogleDocsAdapter(mock_config)
    adapter._client = mock_client
    
    url = adapter.create_document(sample_pulse)
    
    assert url is None
"""

with open("tests/unit/test_google_docs_adapter.py", "w") as f:
    f.write(content_docs)
