import asyncio
import argparse
import sys
import structlog
from pathlib import Path

# Add project root to path so we can import from src
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.agent.orchestrator import Orchestrator
from src.config.manager import ConfigManager

from src.collection.google_play_adapter import GooglePlayAdapter
from src.processing.normalizer import ReviewNormalizer
from src.processing.deduplicator import ReviewDeduplicator
from src.analysis.classifier import ReviewAnalyzer
from src.analysis.theme_discovery import ThemeDiscoveryService
from src.analysis.trend_analysis import TrendAnalysisService
from src.analysis.priority_scoring import PriorityScoringService
from src.analysis.evidence_selection import EvidenceSelectionService
from src.generation.pulse_generator import PulseGenerator
from src.generation.report_validator import ReportValidator
from src.storage.json_file_store import JsonFileStore
from src.delivery.google_docs_adapter import GoogleDocsAdapter
from src.delivery.gmail_adapter import GmailAdapter
from datetime import datetime, timedelta

from src.analysis.llm_client import LLMClient
import os

logger = structlog.get_logger(__name__)

async def run_pipeline(config_path: str = "config.yaml"):
    try:
        logger.info(f"Loading configuration from {config_path}")
        # Initialize config
        ConfigManager.load(config_path)
        config = ConfigManager.get_config()
        
        # Initialize orchestrator using create_agent
        from src.agent.orchestrator import create_agent
        orchestrator = create_agent(config)
        
        # Run pipeline
        logger.info("Starting review analysis pipeline")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=config.collection.reporting_period_days)
        result = await orchestrator.run(start_date=start_date, end_date=end_date)
        
        if result:
            logger.info("Pipeline completed successfully",
                       status=result.status)
            return 0
        else:
            logger.error("Pipeline completed without producing a result")
            return 1
            
    except Exception as e:
        logger.exception("Pipeline failed with error", error=str(e))
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GROWW Review Analysis Agent")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.yaml",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Run async main
    exit_code = asyncio.run(run_pipeline(args.config))
    sys.exit(exit_code)
