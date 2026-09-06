import structlog
from typing import Dict, Any
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from src.config.manager import ConfigManager

logger = structlog.get_logger(__name__)

class MCPClient:
    """Client for interacting with the external MCP server via SSE."""
    
    def __init__(self):
        config = ConfigManager.get_config()
        self.server_url = config.delivery.mcp.server_url
        self.api_key = config.delivery.mcp.api_key
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the remote MCP server."""
        if not self.server_url:
            logger.error("MCP server URL not configured")
            raise ValueError("MCP server URL is required")
            
        headers = {}
        if self.api_key:
            # Add API key to headers, usually as a Bearer token or x-api-key depending on the server setup
            # Here we provide both common variants, or we can use Authorization
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["x-api-key"] = self.api_key
            
        logger.info(f"Calling MCP tool: {tool_name} on {self.server_url}")
        try:
            async with sse_client(self.server_url, headers=headers) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)
                    logger.info(f"MCP tool call successful: {tool_name}")
                    return result
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            raise

    async def deliver_via_docs(self, document_id: str, title: str, pulse_markdown: str):
        """Deliver the pulse report by appending it to a Google Doc."""
        arguments = {
            "documentId": document_id,
            "content": [
                {
                    "type": "heading",
                    "text": title,
                    "level": 1
                },
                {
                    "type": "paragraph",
                    "text": pulse_markdown
                }
            ]
        }
        return await self.call_tool("google_docs_append_content", arguments)

    async def deliver_via_email(self, recipients: list[str], subject: str, pulse_markdown: str, is_html: bool = False):
        """Deliver the pulse report by sending an email."""
        arguments = {
            "to": recipients,
            "subject": subject,
            "body": pulse_markdown,
            "isHtml": is_html
        }
        return await self.call_tool("gmail_send_email", arguments)
