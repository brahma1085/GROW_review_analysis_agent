import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path so we can import src modules
sys.path.append(str(Path(__file__).parent))

from src.config.manager import ConfigManager
from src.storage.json_file_store import JsonFileStore
from src.collection.google_play_adapter import GooglePlayAdapter
from src.collection.incremental_manager import IncrementalManager
from src.processing.normalizer import ReviewNormalizer
from src.processing.deduplicator import ReviewDeduplicator
from src.utils.date_utils import get_last_complete_week
from src.analysis.classifier import ReviewAnalyzer
from src.analysis.llm_client import LLMClient
from src.analysis.theme_discovery import ThemeDiscoveryService
from src.analysis.trend_analysis import TrendAnalysisService
from src.analysis.priority_scoring import PriorityScoringService
from src.analysis.evidence_selection import EvidenceSelectionService
from src.observability.logger import get_logger
import os
import json

logger = get_logger("scratch_run")

def main():
    logger.info("Loading configuration...")
    config = ConfigManager.load("config.yaml")
    
    app_id = config.app.package_id
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info("Initializing components...")
    store = JsonFileStore(config.storage.data_dir)
    adapter = GooglePlayAdapter(
        max_retries=config.analysis.max_retries,
        retry_backoff_seconds=config.analysis.retry_backoff_seconds
    )
    # We bypass IncrementalManager so we don't skip reviews we already collected
    normalizer = ReviewNormalizer()
    deduplicator = ReviewDeduplicator(
        exact_match=config.deduplication.exact_match,
        near_duplicate_threshold=config.deduplication.near_duplicate_threshold
    )
    analyzer = ReviewAnalyzer(config)
    
    # Let's fetch just the last 3 days of reviews to keep the demo quick
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    max_reviews = 50 # Limit to 50 for the scratch run
    
    # Fetch historical IDs BEFORE we run collection so we don't accidentally
    # flag the newly collected reviews as duplicates
    logger.info("Ignoring historical IDs for this test run...")
    historical_ids = set()

    logger.info(f"Running collection for {app_id} (max {max_reviews} reviews)...")
    reviews = adapter.fetch_reviews(
        app_id=app_id,
        start_date=start_date,
        end_date=end_date,
        max_count=max_reviews
    )
    
    if not reviews or not reviews.reviews:
        logger.info("No new reviews collected.")
        return
        
    logger.info(f"Collected {len(reviews.reviews)} raw reviews. Running normalizer...")
    
    # Normalization
    norm_result = normalizer.normalize_batch(reviews.reviews)
    logger.info(f"Normalization complete. Usable: {norm_result.stats.total_usable}, Discarded: {norm_result.stats.total_discarded}")
    
    # Deduplication
    logger.info("Running deduplicator...")
    dedup_result = deduplicator.deduplicate(norm_result.normalized, historical_ids)
    
    logger.info(f"Deduplication complete. Unique reviews: {len(dedup_result.unique_reviews)}")
    
    # Save normalized reviews
    if dedup_result.unique_reviews:
        logger.info("Saving normalized unique reviews to storage...")
        store.save_normalized_reviews(dedup_result.unique_reviews, run_id)
        
        logger.info("Running AI Classification...")
        analyzed_reviews = analyzer.analyze_batch(dedup_result.unique_reviews)
        if analyzed_reviews:
            logger.info(f"Analyzed {len(analyzed_reviews)} reviews. Saving to storage...")
            store.save_analysis_results(analyzed_reviews, run_id)
            
            logger.info("Starting Phase 5: Synthesis...")
            import dotenv
            dotenv.load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            
            if not api_key:
                logger.error("GROQ_API_KEY not set. Skipping Phase 5.")
                return
                
            llm_client = LLMClient(api_key=api_key, model_name="openai/gpt-oss-120b")
            
            # 1. Theme Discovery
            logger.info("Discovering Themes...")
            theme_discovery = ThemeDiscoveryService(llm_client=llm_client, max_reviews_per_chunk=30)
            theme_result = theme_discovery.discover_themes(analyzed_reviews)
            logger.info(f"Discovered {len(theme_result.themes)} themes. ({theme_result.unthemed_count} unthemed reviews)")
            
            # 2. Trend Analysis
            logger.info("Analyzing Trends...")
            trend_service = TrendAnalysisService(llm_client=llm_client)
            trend_result = trend_service.analyze_trends(current=theme_result, historical=None)
            logger.info(f"Trend Analysis complete. New themes: {len(trend_result.new_themes)}")
            
            # 3. Priority Scoring
            logger.info("Scoring Priorities...")
            priority_service = PriorityScoringService()
            prioritized_themes = priority_service.score_themes(theme_result=theme_result, trend_result=trend_result)
            
            # 4. Evidence Selection
            logger.info("Selecting Evidence...")
            evidence_service = EvidenceSelectionService()
            evidence_result = evidence_service.select_evidence(
                prioritized_themes=prioritized_themes, 
                all_reviews=analyzed_reviews, 
                max_per_theme=2, 
                max_overall=3
            )
            
            # Save Synthesis Results manually for scratch test
            out_file = Path(config.storage.data_dir) / "phase5_output.json"
            output_data = {
                "themes": [pt.model_dump() for pt in prioritized_themes],
                "trends": {
                    "emerging": [ts.model_dump() for ts in trend_result.emerging],
                    "growing": [ts.model_dump() for ts in trend_result.growing],
                    "declining": [ts.model_dump() for ts in trend_result.declining],
                    "persistent": [ts.model_dump() for ts in trend_result.persistent],
                    "new_themes": [ts.model_dump() for ts in trend_result.new_themes],
                },
                "evidence": evidence_result.model_dump()
            }
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=str)
                
            logger.info(f"Phase 5 complete. Synthesis results saved to {out_file}")
            
            # --- Phase 6: Report Generation & Validation ---
            logger.info("Starting Phase 6: Report Generation & Validation...")
            
            from src.generation.pulse_generator import PulseGenerator, AnalysisContext
            from src.generation.report_validator import ReportValidator
            
            context = AnalysisContext(
                app_id=app_id,
                period_start=start_date,
                period_end=end_date,
                total_fetched=len(reviews.reviews),
                analyzed_reviews=analyzed_reviews,
                theme_result=theme_result,
                trend_result=trend_result,
                prioritized_themes=prioritized_themes,
                evidence_result=evidence_result,
                config=config,
                llm_client=llm_client
            )
            
            pulse_generator = PulseGenerator()
            pulse = pulse_generator.generate_pulse(context)
            
            validator = ReportValidator()
            validation_result = validator.validate(pulse, context)
            
            logger.info(f"Validation Result: Valid={validation_result.is_valid}, Errors={len(validation_result.errors)}, Warnings={len(validation_result.warnings)}")
            
            pulse_out_file = Path(config.storage.data_dir) / "phase6_pulse.json"
            with open(pulse_out_file, 'w', encoding='utf-8') as f:
                json.dump(pulse.model_dump(), f, indent=2, default=str)
                
            logger.info(f"Phase 6 complete. Pulse saved to {pulse_out_file}")
            
        else:
            logger.info("No reviews were successfully analyzed.")
        
    logger.info(f"Pipeline complete! Check the '{config.storage.data_dir}' folder in your project root.")

if __name__ == "__main__":
    main()
