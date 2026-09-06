import structlog
from typing import Optional, Dict, Any
from src.delivery.mcp_client import MCPClient
from src.config.manager import ConfigManager

logger = structlog.get_logger(__name__)

class GoogleDocsAdapter:
    """Adapter for interacting with Google Docs via MCP."""
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.config = ConfigManager.get_config().delivery.google_docs
        self.client = mcp_client or MCPClient()

    async def deliver_pulse(self, content: str, title: str = "Weekly Pulse Report") -> None:
        """Deliver the pulse report to Google Docs."""
        mode = self.config.mode
        doc_id = self.config.document_id
        
        logger.info(f"Delivering pulse to Google Docs via MCP. Mode: {mode}")
        
        try:
            if mode == "append" and doc_id:
                await self.client.call_tool(
                    "append_formatted_content",
                    arguments={
                        "document_id": doc_id,
                        "content": content,
                        "separator": self.config.separator
                    }
                )
                logger.info(f"Successfully appended pulse to document {doc_id}")
            else:
                # Default to create if mode is create or doc_id is missing
                result = await self.client.call_tool(
                    "create_document",
                    arguments={
                        "title": title,
                        "content": content
                    }
                )
                logger.info("Successfully created new document", result=result)
        except Exception as e:
            logger.error("Failed to deliver pulse to Google Docs via MCP", error=str(e))
            raise
