import json
import copy
import pytest
from unittest.mock import MagicMock, patch
from src.analysis.classifier import ReviewAnalyzer
from src.models.review import NormalizedReview
from src.models.config import AgentConfig, AnalysisConfig

from src.config.manager import ConfigManager

@pytest.fixture
def mock_config():
    config = ConfigManager().get_config()
    config.analysis.batch_size = 2
    return config

@pytest.fixture
def sample_reviews():
    with open("tests/fixtures/sample_reviews.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [NormalizedReview(**r) for r in data]

@pytest.fixture
def sample_analyzed_response():
    with open("tests/fixtures/sample_analyzed.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_analyze_batch_success(mock_config, sample_reviews, sample_analyzed_response):
    analyzer = ReviewAnalyzer(config=mock_config)
    
    with patch.object(analyzer.llm_client, 'analyze_batch_json') as mock_llm:
        # Mock LLM to return the sample response (fresh deepcopy each time)
        mock_llm.side_effect = lambda *args, **kwargs: copy.deepcopy(sample_analyzed_response)
        
        # Test analysis (the 4th review is is_usable=False, so it shouldn't be processed)
        analyzed = analyzer.analyze_batch(sample_reviews)
        
        # We expect 3 reviews back since 1 was unusable
        assert len(analyzed) == 3
        assert analyzed[0].normalized_review.original_review.review_id == "r1"
        assert analyzed[0].sentiment.value == "negative"
        assert analyzed[0].sentiment_confidence == 0.95
        assert analyzed[1].normalized_review.original_review.review_id == "r2"
        assert analyzed[2].normalized_review.original_review.review_id == "r3"
        
        # Check that it split into batches correctly. 
        # Total usable = 3. Batch size = 2. It should have called the LLM twice.
        assert mock_llm.call_count == 2
        
def test_analyze_batch_fallback_on_failure(mock_config, sample_reviews, sample_analyzed_response):
    analyzer = ReviewAnalyzer(config=mock_config)
    
    # We have 3 usable reviews. Batch 1 = [r1, r2]. Batch 2 = [r3].
    # We will make the LLM raise an Exception ONLY on the first call (batch size > 1).
    # Then the fallback kicks in and processes them individually.
    
    call_count = 0
    def mock_analyze_batch_json(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        # If it's the very first call, simulate a failure (e.g. malformed JSON returned from groq SDK)
        if call_count == 1:
            raise ValueError("Malformed JSON")
            
        # For subsequent fallback individual calls, return just the matched review from the fixture
        # We'll parse the prompt to figure out which one it is
        prompt = kwargs.get('prompt', '')
        
        # Find which review is in the prompt and return its mocked response
        res = {"analyzed_reviews": []}
        for expected in sample_analyzed_response["analyzed_reviews"]:
            if expected["review_id"] in prompt:
                res["analyzed_reviews"].append(expected)
        return copy.deepcopy(res)

    with patch.object(analyzer.llm_client, 'analyze_batch_json', side_effect=mock_analyze_batch_json) as mock_llm:
        analyzed = analyzer.analyze_batch(sample_reviews)
        
        # It should still recover and return all 3
        assert len(analyzed) == 3
        # Call 1: Batch of 2 (fails)
        # Call 2: Individual r1 (succeeds)
        # Call 3: Individual r2 (succeeds)
        # Call 4: Batch of 1 (r3) (succeeds)
        assert mock_llm.call_count == 4
