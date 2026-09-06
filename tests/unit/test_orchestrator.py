import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from src.models.config import AgentConfig, AppConfig, CollectionConfig, AnalysisConfig, PriorityConfig, DeduplicationConfig, GoogleDocsConfig, GmailConfig, McpConfig, DeliveryConfig, StorageConfig, LoggingConfig, SchedulingConfig
from src.agent.orchestrator import Orchestrator
from src.models.enums import CollectionStatus
from src.models.review import RawReview, NormalizedReview, AnalyzedReview, CollectionResult, CollectionMetadata, CollectionError, NormalizationResult, NormalizationStats, DeduplicationResult
from src.models.theme import ThemeResult, TrendResult
from src.models.pulse import WeeklyPulse, ExecutiveSummary, MethodologySection, WeekMetrics, SentimentDistribution
from src.generation.report_validator import ValidationResult

@pytest.fixture
def mock_config():
    return AgentConfig(
        app=AppConfig(name="Test", package_id="com.example.app", store="google_play", play_store_url="http://play"),
        collection=CollectionConfig(),
        analysis=AnalysisConfig(),
        priority=PriorityConfig(),
        deduplication=DeduplicationConfig(),
        delivery=DeliveryConfig(
            google_docs=GoogleDocsConfig(document_id="test-doc-id"),
            gmail=GmailConfig(),
            mcp=McpConfig(server_url="http://test", api_key="test")
        ),
        storage=StorageConfig(),
        logging=LoggingConfig(),
        scheduling=SchedulingConfig()
    )

@pytest.fixture
def orchestrator(mock_config):
    return Orchestrator(
        config=mock_config,
        collector=Mock(),
        normalizer=Mock(),
        deduplicator=Mock(),
        analyzer=Mock(),
        theme_discovery=Mock(),
        trend_analysis=Mock(),
        priority_scoring=Mock(),
        evidence_selection=Mock(),
        pulse_generator=Mock(),
        validator=Mock(),
        storage=Mock(),
        docs_adapter=AsyncMock(),
        gmail_adapter=AsyncMock()
    )

@pytest.mark.asyncio
async def test_orchestrator_happy_path(orchestrator):
    # Create dummy reviews
    dummy_raw = RawReview(
        review_id="1", app_id="com.test", source="google_play",
        review_text="good", star_rating=5, review_date=datetime.now(),
        collected_at=datetime.now()
    )
    dummy_norm = NormalizedReview(
        original_review=dummy_raw,
        original_text="good", cleaned_text="good",
        detected_language="en", is_usable=True, content_hash="hash"
    )
    dummy_analyzed = AnalyzedReview(
        normalized_review=dummy_norm,
        sentiment="positive", sentiment_confidence=0.9,
        categories=["bug_report"], product_area="app", severity="low",
        intent="complaint", key_phrases=["good"]
    )

    # Setup mocks
    orchestrator.collector.fetch_reviews.return_value = CollectionResult(
        reviews=[dummy_raw],
        metadata=CollectionMetadata(
            app_id="com.example.app",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            source="google_play",
            status=CollectionStatus.SUCCESS, 
            total_fetched=10
        )
    )
    
    orchestrator.normalizer.normalize_batch.return_value = NormalizationResult(
        normalized=[dummy_norm],
        stats=NormalizationStats(total_processed=10, total_usable=10, total_discarded=0, discard_reasons={})
    )
    
    orchestrator.deduplicator.deduplicate.return_value = DeduplicationResult(
        unique_reviews=[dummy_norm],
        removed_count=0,
        details=[]
    )
    
    orchestrator.analyzer.analyze_batch.return_value = [dummy_analyzed]
    
    orchestrator.theme_discovery.discover_themes.return_value = ThemeResult(
        themes=[], analysis_context=""
    )
    
    orchestrator.storage.get_previous_aggregate.return_value = Mock()
    orchestrator.trend_analysis.analyze_trends.return_value = TrendResult(signals=[])
    
    orchestrator.priority_scoring.score_themes.return_value = []
    orchestrator.evidence_selection.select_evidence.return_value = Mock()
    
    orchestrator.pulse_generator.generate_pulse.return_value = WeeklyPulse(
        period_start=datetime.now() - timedelta(days=7),
        period_end=datetime.now(),
        executive_summary=ExecutiveSummary(overview="", positive_highlights=[], critical_issues=[]),
        metrics=WeekMetrics(
            reviews_analyzed=10, avg_star_rating=4.5, theme_count=2, emerging_count=1,
            critical_high_count=0, rating_distribution={5: 10},
            sentiment_distribution=SentimentDistribution(positive=10, neutral=0, negative=0)
        ),
        methodology=MethodologySection(
            source="google_play",
            app_id="com.example.app",
            period="weekly",
            timestamp=datetime.now(),
            total_fetched=10,
            usable_reviews=10
        )
    )
    
    orchestrator.validator.validate.return_value = ValidationResult(is_valid=True, errors=[], warnings=[])
    
    # Run
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    report = await orchestrator.run(start_date, end_date, dry_run=True)
    
    assert report.status == "success"
    assert report.collection.total_fetched == 10
    assert report.analysis.trends_analyzed == True

@pytest.mark.asyncio
async def test_orchestrator_collection_failure(orchestrator):
    orchestrator.collector.fetch_reviews.return_value = CollectionResult(
        reviews=[],
        metadata=CollectionMetadata(
            app_id="com.example.app",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            source="google_play",
            status=CollectionStatus.FAILED, 
            total_fetched=0
        ),
        errors=[CollectionError(error_type="network", message="Network error")]
    )
    
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    report = await orchestrator.run(start_date, end_date, dry_run=True)
    
    assert report.status == "failed"
    assert "Network error" in str(report.errors)
    assert report.processing is None
