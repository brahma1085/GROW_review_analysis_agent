import re
import unicodedata
import hashlib
from typing import List, Tuple
from langdetect import detect, LangDetectException
import emoji

from src.models.review import RawReview, NormalizedReview, NormalizationResult, NormalizationStats
from src.observability.logger import get_logger

logger = get_logger(__name__)

# Domain terms to preserve exactly (e.g. avoid lowercasing if we were doing that, 
# but mostly ensure they aren't stripped or split weirdly).
DOMAIN_TERMS = {"KYC", "IPO", "MF", "SIP", "OTP", "UPI", "SGB", "FD", "NPS"}

class ReviewNormalizer:
    def __init__(self, min_length: int = 5, min_word_count: int = 10):
        self.min_length = min_length
        self.min_word_count = min_word_count
        # Regex to collapse multiple spaces and newlines
        self.whitespace_re = re.compile(r'\s+')
        
    def normalize_batch(self, reviews: List[RawReview]) -> NormalizationResult:
        stats = NormalizationStats(total_processed=len(reviews))
        normalized_reviews = []
        
        for raw_review in reviews:
            normalized, reason = self.normalize(raw_review)
            if normalized.is_usable:
                stats.total_usable += 1
                normalized_reviews.append(normalized)
            else:
                stats.total_discarded += 1
                stats.discard_reasons[reason] = stats.discard_reasons.get(reason, 0) + 1
                
                # Still append if it's discarded, just marked as not usable? 
                # The architecture says "flag reviews that are blank", but often we drop them.
                # Let's keep them in the list with `is_usable=False` so they can be logged or filtered out later.
                normalized_reviews.append(normalized)
                
        return NormalizationResult(normalized=normalized_reviews, stats=stats)
        
    def normalize(self, raw_review: RawReview) -> Tuple[NormalizedReview, str]:
        text = raw_review.review_text or ""
        original_text = text
        notes = []
        is_usable = True
        discard_reason = ""
        
        # 1. Unicode normalization (NFC)
        text = unicodedata.normalize('NFC', text)
        
        # 2. Whitespace normalization (also strips leading/trailing)
        text = self.whitespace_re.sub(' ', text).strip()
        
        # 3. Detect Language
        lang = raw_review.detected_language or "unknown"
        if not text:
             lang = "unknown"
        elif lang == "unknown" or not lang:
            try:
                lang = detect(text)
            except LangDetectException:
                lang = "unknown"
                
        # 4. Filter empty or unusable
        # Remove emojis for length calculation to see if there's actual text
        text_without_emoji = emoji.replace_emoji(text, replace='')
        
        # If it's just punctuation/whitespace
        pure_text = re.sub(r'[^\w\s]', '', text_without_emoji).strip()
        
        if not text:
            is_usable = False
            discard_reason = "empty"
            notes.append("Review is empty")
        elif len(pure_text) < self.min_length:
            is_usable = False
            discard_reason = "too_short"
            notes.append(f"Review too short (length: {len(pure_text)})")
        elif len(pure_text.split()) < self.min_word_count:
            is_usable = False
            discard_reason = "too_few_words"
            notes.append(f"Review has too few words (words: {len(pure_text.split())})")
            
        # 5. Domain term preservation (implicit if we don't aggressively lowercase/stem here)
        # We just keep the text as is (with normalized spaces)
        
        # 6. Content hash generation
        # hash(cleaned_text + star_rating + reviewer_name)
        hash_input = f"{text}|{raw_review.star_rating}|{raw_review.reviewer_name or ''}"
        content_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        
        normalized = NormalizedReview(
            original_review=raw_review,
            original_text=original_text,
            cleaned_text=text,
            detected_language=lang,
            is_usable=is_usable,
            content_hash=content_hash,
            normalization_notes=notes
        )
        
        return normalized, discard_reason
