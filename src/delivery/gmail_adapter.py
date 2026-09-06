import structlog
from typing import Optional, List
from src.delivery.mcp_client import MCPClient
from src.config.manager import ConfigManager

logger = structlog.get_logger(__name__)

class GmailAdapter:
    """Adapter for interacting with Gmail via MCP."""
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.config = ConfigManager.get_config().delivery.gmail
        self.client = mcp_client or MCPClient()

    async def draft_pulse_email(self, subject: str, html_content: str, recipients: Optional[List[str]] = None) -> None:
        """Create a draft email with the pulse report."""
        if not self.config.create_draft:
            logger.info("Gmail draft creation is disabled in configuration.")
            return
            
        target_recipients = recipients or self.config.recipients
        if not target_recipients:
            logger.warning("No recipients configured for Gmail draft.")
            
        logger.info("Creating Gmail draft via MCP")
        
        try:
            result = await self.client.call_tool(
                "create_draft",
                arguments={
                    "subject": subject,
                    "html_content": html_content,
                    "recipients": target_recipients
                }
            )
            logger.info("Successfully created Gmail draft", result=result)
        except Exception as e:
            logger.error("Failed to create Gmail draft via MCP", error=str(e))
            raise
