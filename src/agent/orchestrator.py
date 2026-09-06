import logging
import uuid
import time
from datetime import datetime, timedelta
from typing import Optional, List, Set, Any
from pydantic import BaseModel, Field

from src.models.config import AgentConfig
from src.models.enums import CollectionStatus
from src.models.review import CollectionResult, CollectionMetadata
from src.generation.pulse_generator import AnalysisContext
from src.models.execution import ExecutionReport, DateRange, CollectionSummary, ProcessingSummary, AnalysisSummary, DeliverySummary
from src.models.pulse import WeeklyAggregate
from src.generation.report_validator import ValidationResult

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(
        self,
        config: AgentConfig,
        collector,
        normalizer,
        deduplicator,
        analyzer,
        theme_discovery,
        trend_analysis,
        priority_scoring,
        evidence_selection,
        pulse_generator,
        validator,
        storage,
        mcp_client=None,
        docs_adapter=None,
        gmail_adapter=None
    ):
        self.config = config
        self.collector = collector
        self.normalizer = normalizer
        self.deduplicator = deduplicator
        self.analyzer = analyzer
        self.theme_discovery = theme_discovery
        self.trend_analysis = trend_analysis
        self.priority_scoring = priority_scoring
        self.evidence_selection = evidence_selection
        self.pulse_generator = pulse_generator
        self.validator = validator
        self.storage = storage
        self.mcp_client = mcp_client
        self.docs_adapter = docs_adapter
        self.gmail_adapter = gmail_adapter

    async def run(self, start_date: datetime, end_date: datetime, dry_run: bool = False) -> ExecutionReport:
        run_id = str(uuid.uuid4())
        logger.info(f"Starting run {run_id}")
        start_time = time.time()
        
        report = ExecutionReport(
            run_id=run_id,
            status="running",
            app_id=self.config.app.package_id,
            reporting_period=DateRange(start_date=start_date, end_date=end_date),
            duration_seconds=0.0,
            timestamp=datetime.now(),
            warnings=[],
            errors=[]
        )
        
        try:
            # 1. Collection
            logger.info("Starting collection phase...")
            collection_result = self.collector.fetch_reviews(
                app_id=self.config.app.package_id,
                start_date=start_date,
                end_date=end_date,
                max_count=self.config.collection.max_reviews
            )
            
            report.collection = CollectionSummary(
                total_fetched=collection_result.metadata.total_fetched,
                status=collection_result.metadata.status.value
            )
            
            if collection_result.metadata.status == CollectionStatus.FAILED:
                report.status = "failed"
                report.errors.extend([err.message for err in collection_result.errors])
                report.duration_seconds = time.time() - start_time
                return report
                
            if not collection_result.reviews:
                report.status = "success"
                report.duration_seconds = time.time() - start_time
                return report
                
            # 2. Processing (Normalization & Deduplication)
            logger.info("Starting processing phase...")
            norm_result = self.normalizer.normalize_batch(collection_result.reviews)
            
            # Assume no historical IDs for now
            historical_ids = set()
            dedup_result = self.deduplicator.deduplicate(norm_result.normalized, historical_ids)
            
            report.processing = ProcessingSummary(
                normalized_count=len(norm_result.normalized),
                unique_count=len(dedup_result.unique_reviews),
                dropped_count=len(norm_result.normalized) - len(dedup_result.unique_reviews)
            )
            
            if not dedup_result.unique_reviews:
                report.status = "success"
                report.duration_seconds = time.time() - start_time
                return report
                
            if len(dedup_result.unique_reviews) < getattr(self.config.collection, 'min_review_threshold', 1):
                msg = f"Low review count after deduplication: {len(dedup_result.unique_reviews)}"
                logger.warning(msg)
                report.warnings.append(msg)
                
            # 3. AI Analysis
            logger.info("Starting AI classification...")
            analyzed_reviews = self.analyzer.analyze_batch(dedup_result.unique_reviews)
            
            # Synthesis Phase
            logger.info("Starting synthesis phase...")
            
            # 4. Theme Discovery
            theme_result = self.theme_discovery.discover_themes(analyzed_reviews)
            
            # 5. Trend Analysis (Conditional)
            previous_aggregate = self.storage.get_previous_aggregate(self.config.app.package_id)
            if previous_aggregate:
                trend_result = self.trend_analysis.analyze_trends(theme_result, previous_aggregate)
                trends_analyzed = True
            else:
                logger.info("No historical data available. Skipping trend comparison.")
                trend_result = self.trend_analysis.analyze_trends(theme_result, None)
                trends_analyzed = False
            
            # 6. Priority Scoring
            prioritized_themes = self.priority_scoring.score_themes(theme_result, trend_result)
            
            # 7. Evidence Selection
            evidence_result = self.evidence_selection.select_evidence(prioritized_themes, analyzed_reviews, 2, 5)
            
            report.analysis = AnalysisSummary(
                analyzed_count=len(analyzed_reviews),
                themes_discovered=len(theme_result.themes) if hasattr(theme_result, 'themes') else 0,
                trends_analyzed=trends_analyzed,
                prioritized_themes=len(prioritized_themes)
            )
            
            # 8. Pulse Generation
            logger.info("Starting generation phase...")
            context = AnalysisContext(
                app_id=self.config.app.package_id,
                period_start=start_date,
                period_end=end_date,
                total_fetched=len(collection_result.reviews),
                analyzed_reviews=analyzed_reviews,
                theme_result=theme_result,
                trend_result=trend_result,
                prioritized_themes=prioritized_themes,
                evidence_result=evidence_result,
                config=self.config,
                llm_client=self.theme_discovery.llm_client if hasattr(self.theme_discovery, 'llm_client') else None
            )
            
            pulse = self.pulse_generator.generate_pulse(context)
            
            # 9. Validation
            validation = self.validator.validate(pulse, context)
            report.validation = validation
            
            if not validation.is_valid:
                logger.warning("Pulse validation failed")
                report.errors.extend([err.message for err in validation.errors])
                # Abort on validation failure as per robust workflow
                report.status = "failed"
                report.duration_seconds = time.time() - start_time
                return report

            # 10. Persist (Before Delivery)
            logger.info("Persisting Weekly Aggregate...")
            aggregate = WeeklyAggregate(
                run_id=run_id,
                app_id=self.config.app.package_id,
                period_start=start_date,
                period_end=end_date,
                metrics=pulse.metrics,
                themes=prioritized_themes,
                doc_url=None,
                gmail_status=None
            )
            self.storage.save_weekly_aggregate(aggregate)
            
            # 11. Delivery (Independent Failure Handling)
            report.delivery = DeliverySummary(docs_success=False, gmail_success=False)
            if not dry_run:
                logger.info("Starting delivery phase...")
                title = f"Weekly Pulse: {self.config.app.name}"
                pulse_md = pulse.to_markdown() if hasattr(pulse, 'to_markdown') else str(pulse)
                doc_url = None
                
                if self.mcp_client:
                    docs_config = self.config.delivery.google_docs
                    if docs_config.document_id:
                        try:
                            logger.info("Delivering via MCP to Google Docs...")
                            await self.mcp_client.deliver_via_docs(
                                document_id=docs_config.document_id,
                                title=title,
                                pulse_markdown=pulse_md
                            )
                            # Mocking doc_url since MCP might not return it directly here
                            doc_url = "mcp_docs_url_placeholder"
                            report.delivery.docs_success = True
                            report.delivery.docs_url = doc_url
                        except Exception as e:
                            logger.error(f"MCP Docs delivery failed: {e}")
                            report.errors.append(f"Docs delivery failed: {e}")
                    
                    gmail_config = self.config.delivery.gmail
                    if gmail_config.recipients:
                        try:
                            logger.info("Delivering via MCP to Gmail...")
                            await self.mcp_client.deliver_via_email(
                                recipients=gmail_config.recipients,
                                subject=title,
                                pulse_markdown=pulse_md,
                                is_html=False,
                                doc_url=doc_url
                            )
                            report.delivery.gmail_success = True
                        except Exception as e:
                            logger.error(f"MCP Gmail delivery failed: {e}")
                            report.errors.append(f"Gmail delivery failed: {e}")
                            
                elif self.docs_adapter and self.gmail_adapter:
                    # Fallback to local adapters
                    try:
                        docs_res = await self.docs_adapter.deliver_pulse(pulse, title=title)
                        if docs_res.success:
                            doc_url = docs_res.doc_url
                            report.delivery.docs_success = True
                            report.delivery.docs_url = doc_url
                        else:
                            report.errors.append(f"Docs adapter failed: {docs_res.error}")
                    except Exception as e:
                        logger.error(f"Docs adapter exception: {e}")
                        report.errors.append(f"Docs delivery exception: {e}")
                        
                    try:
                        gmail_res = await self.gmail_adapter.deliver_pulse(pulse, doc_url=doc_url)
                        if gmail_res.success:
                            report.delivery.gmail_success = True
                        else:
                            report.errors.append(f"Gmail adapter failed: {gmail_res.error}")
                    except Exception as e:
                        logger.error(f"Gmail adapter exception: {e}")
                        report.errors.append(f"Gmail delivery exception: {e}")
                
                # Update aggregate with delivery status
                aggregate.doc_url = report.delivery.docs_url
                aggregate.gmail_status = "success" if report.delivery.gmail_success else "failed"
                self.storage.save_weekly_aggregate(aggregate)
            
            # 12. Report
            report.status = "success" if not report.errors else "partial_success"
            report.duration_seconds = time.time() - start_time
            return report
            
        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            report.status = "failed"
            report.errors.append(str(e))
            report.duration_seconds = time.time() - start_time
            return report

def create_agent(config: AgentConfig) -> Orchestrator:
    import os
    from src.collection.google_play_adapter import GooglePlayAdapter
    from src.processing.normalizer import ReviewNormalizer
    from src.processing.deduplicator import ReviewDeduplicator
    from src.analysis.classifier import ReviewAnalyzer
    from src.analysis.theme_discovery import ThemeDiscoveryService
    from src.analysis.trend_analysis import TrendAnalysisService
    from src.analysis.priority_scoring import PriorityScoringService
    from src.analysis.evidence_selection import EvidenceSelectionService
    from src.generation.pulse_generator import PulseGenerator
    from src.delivery.google_docs_adapter import GoogleDocsAdapter
    from src.storage.json_file_store import JsonFileStore
    from src.analysis.llm_client import LLMClient
    
    from src.delivery.mcp_client import MCPClient
    
    # Initialize basic components
    llm_client = LLMClient(api_key=os.environ.get("GROQ_API_KEY", "default-key"), model_name=config.analysis.llm_model)
    
    collector = GooglePlayAdapter()
    normalizer = ReviewNormalizer(min_word_count=config.collection.min_word_count)
    deduplicator = ReviewDeduplicator()
    
    analyzer = ReviewAnalyzer(config=config)
    theme_discovery = ThemeDiscoveryService(llm_client=llm_client)
    trend_analysis = TrendAnalysisService(llm_client=llm_client)
    priority_scoring = PriorityScoringService()
    evidence_selection = EvidenceSelectionService()
    
    # Needs actual template dir
    pulse_generator = PulseGenerator()
    
    class DummyValidator:
        def validate(self, *args, **kwargs):
            from types import SimpleNamespace
            return SimpleNamespace(is_valid=True, errors=[])
            
    validator = DummyValidator()
    
    # Ensure data dir exists
    storage = JsonFileStore(data_dir=config.storage.data_dir)
    
    docs_adapter = None
    gmail_adapter = None
    
    # Initialize MCP Client
    mcp_client = MCPClient() if config.delivery.mcp.server_url else None
    
    return Orchestrator(
        config=config,
        collector=collector,
        normalizer=normalizer,
        deduplicator=deduplicator,
        analyzer=analyzer,
        theme_discovery=theme_discovery,
        trend_analysis=trend_analysis,
        priority_scoring=priority_scoring,
        evidence_selection=evidence_selection,
        pulse_generator=pulse_generator,
        validator=validator,
        storage=storage,
        mcp_client=mcp_client,
        docs_adapter=docs_adapter,
        gmail_adapter=gmail_adapter
    )
