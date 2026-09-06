import pytest
from unittest.mock import MagicMock, AsyncMock
from src.delivery.gmail_adapter import GmailAdapter
import datetime

@pytest.fixture
def mock_config():
    from src.models.config import DeliveryConfig, GmailConfig, GoogleDocsConfig, McpConfig
    return DeliveryConfig(
        google_docs=GoogleDocsConfig(),
        gmail=GmailConfig(create_draft=True),
        mcp=McpConfig()
    )

@pytest.mark.asyncio
async def test_gmail_create_draft(mock_config):
    mock_client = AsyncMock()
    mock_client.call_tool.return_value = {"status": "success", "draft_id": "draft_123"}
    
    adapter = GmailAdapter(mcp_client=mock_client)
    # Patch config directly since ConfigManager might be tricky
    adapter.config = mock_config.gmail
    
    await adapter.draft_pulse_email("subject", "html_content")
    mock_client.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_gmail_failure(mock_config):
    mock_client = AsyncMock()
    mock_client.call_tool.side_effect = Exception("API Error")
    
    adapter = GmailAdapter(mcp_client=mock_client)
    adapter.config = mock_config.gmail
    
    with pytest.raises(Exception):
        await adapter.draft_pulse_email("subject", "html_content")
