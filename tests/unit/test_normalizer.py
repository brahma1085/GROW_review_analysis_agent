import pytest
from datetime import datetime
from src.processing.normalizer import ReviewNormalizer
from src.models.review import RawReview

@pytest.fixture
def normalizer():
    return ReviewNormalizer(min_length=5)

def create_raw(text: str) -> RawReview:
    return RawReview(
        review_id="1",
        app_id="test",
        source="test",
        review_text=text,
        star_rating=5,
        review_date=datetime.now(),
        collected_at=datetime.now()
    )

def test_whitespace_normalization(normalizer):
    raw = create_raw("  This   is \n a \t test  ")
    result, _ = normalizer.normalize(raw)
    assert result.cleaned_text == "This is a test"
    assert result.original_text == "  This   is \n a \t test  "
    assert result.is_usable is True

def test_emoji_handling(normalizer):
    # Ensure emojis aren't stripped and whitespace around them is collapsed
    raw = create_raw("Love this app!!! 😍  Works great.")
    result, _ = normalizer.normalize(raw)
    assert result.cleaned_text == "Love this app!!! 😍 Works great."
    assert result.is_usable is True

def test_language_detection(normalizer):
    # English
    raw1 = create_raw("This is a great application")
    result1, _ = normalizer.normalize(raw1)
    assert result1.detected_language == "en"
    
def test_unusable_filtering(normalizer):
    # Empty
    result, reason = normalizer.normalize(create_raw(""))
    assert result.is_usable is False
    assert reason == "empty"
    
    # Too short
    result, reason = normalizer.normalize(create_raw("ok"))
    assert result.is_usable is False
    assert reason == "too_short"
    
    # Just emoji
    result, reason = normalizer.normalize(create_raw("😍😍😍😍😍"))
    assert result.is_usable is False
    assert reason == "too_short"

def test_domain_term_preservation(normalizer):
    # Normalization should not corrupt domain terms
    raw = create_raw("My KYC was rejected for my SIP in MF.")
    result, _ = normalizer.normalize(raw)
    assert result.cleaned_text == "My KYC was rejected for my SIP in MF."
    assert "KYC" in result.cleaned_text

def test_content_hash_determinism(normalizer):
    raw1 = create_raw("Test review")
    raw2 = create_raw("Test review") # Exact same
    
    res1, _ = normalizer.normalize(raw1)
    res2, _ = normalizer.normalize(raw2)
    
    assert res1.content_hash == res2.content_hash
