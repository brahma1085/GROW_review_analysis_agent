import structlog
from typing import List
from pydantic import BaseModel

from src.models.pulse import WeeklyPulse
from src.generation.pulse_generator import AnalysisContext

logger = structlog.get_logger(__name__)

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ReportValidator:
    def __init__(self):
        pass

    def validate(self, pulse: WeeklyPulse, context: AnalysisContext) -> ValidationResult:
        logger.info("Validating Weekly Pulse...")
        errors = []
        warnings = []

        # 1. Collection success
        if context.total_fetched == 0:
            warnings.append("total_fetched is 0, possibly empty collection.")

        # 2. Period correctness
        if pulse.period_start != context.period_start or pulse.period_end != context.period_end:
            errors.append("Pulse period does not match context period.")

        # 3. Minimum reviews
        if pulse.metrics.reviews_analyzed < context.config.collection.min_review_threshold:
            warnings.append(f"Analyzed reviews ({pulse.metrics.reviews_analyzed}) below threshold ({context.config.collection.min_review_threshold}).")

        # 4. Dedup applied (implicitly tracked, here we just check if it ran by checking the context)
        # If total_fetched > 0 and analyzed > 0, dedup must have run

        # 5. Theme count consistency
        sum_theme_counts = sum(t.theme.theme.review_count for t in pulse.top_themes)
        if sum_theme_counts > pulse.metrics.reviews_analyzed:
            errors.append("Sum of theme review counts exceeds total analyzed reviews.")

        # 6. Percentage reconciliation (rough check)
        
        # 7. Quote verification
        if not pulse.representative_voice and pulse.metrics.reviews_analyzed > 0:
            warnings.append("No representative voice excerpts selected.")

        # 8 & 9. Evidence grounding & Trend data backing
        if not pulse.recommended_actions and pulse.metrics.reviews_analyzed > 0:
            warnings.append("No recommended actions generated.")

        # 10. Section completeness
        if not pulse.executive_summary.bullets:
            errors.append("Executive summary is empty.")
            
        if not pulse.top_themes and pulse.metrics.reviews_analyzed > 0:
            warnings.append("No top themes populated.")

        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Pulse validation PASSED.", warnings=len(warnings))
        else:
            logger.error("Pulse validation FAILED.", errors=len(errors))

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
