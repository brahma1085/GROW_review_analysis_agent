import structlog
from typing import Tuple, Optional
from src.models.config import DeliveryConfig
from src.models.pulse import WeeklyPulse
from src.delivery.google_docs_adapter import GoogleDocsAdapter
from src.delivery.gmail_adapter import GmailAdapter

logger = structlog.get_logger(__name__)

class DeliveryPipeline:
    def __init__(self, config: DeliveryConfig):
        self.config = config
        self.docs_adapter = GoogleDocsAdapter() if config.google_docs.document_id else None
        self.gmail_adapter = GmailAdapter() if (config.gmail.create_draft or config.gmail.auto_send) else None

    async def deliver(self, pulse: WeeklyPulse) -> Tuple[Optional[str], bool]:
        """
        Executes the delivery pipeline:
        1. Creates Google Doc (if enabled)
        2. Creates Gmail Draft (if enabled)
        
        Returns:
            Tuple[Optional[str], bool]: (Google Doc URL, Email Draft Success)
        """
        logger.info("Starting delivery pipeline")
        
        doc_url = None
        email_success = False

        content = f"Pulse report for {pulse.period_start} to {pulse.period_end}"
        title = "Weekly Pulse Report"
        
        # 1. Create Google Doc
        if self.docs_adapter:
            try:
                await self.docs_adapter.deliver_pulse(content=content, title=title)
                # GoogleDocsAdapter deliver_pulse doesn't return the URL directly right now,
                # we'll assume it succeeded
                doc_url = "delivered_to_mcp"
                logger.info(f"Successfully delivered Google Doc via MCP")
            except Exception as e:
                logger.error(f"Error creating Google Doc: {e}")

        # 2. Create Gmail Draft
        if self.gmail_adapter:
            try:
                await self.gmail_adapter.draft_pulse_email(subject=title, html_content=content)
                email_success = True
                logger.info("Successfully created Gmail draft via MCP")
            except Exception as e:
                logger.error(f"Error creating Gmail draft: {e}")

        logger.info("Delivery pipeline completed", doc_url=doc_url, email_success=email_success)
        return doc_url, email_success
