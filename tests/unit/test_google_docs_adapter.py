import pytest
from unittest.mock import MagicMock, AsyncMock
from src.delivery.google_docs_adapter import GoogleDocsAdapter
import datetime

@pytest.fixture
def mock_config():
    from src.models.config import DeliveryConfig, GmailConfig, GoogleDocsConfig, McpConfig
    return DeliveryConfig(
        google_docs=GoogleDocsConfig(document_id="folder_123"),
        gmail=GmailConfig(),
        mcp=McpConfig()
    )

@pytest.mark.asyncio
async def test_google_docs_create(mock_config):
    mock_client = AsyncMock()
    mock_client.call_tool.return_value = {"status": "success", "document_id": "doc_123", "url": "http://docs.google.com/doc_123"}
    
    adapter = GoogleDocsAdapter(mcp_client=mock_client)
    adapter.config = mock_config.google_docs
    
    await adapter.deliver_pulse("content")
    
    mock_client.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_google_docs_failure(mock_config):
    mock_client = AsyncMock()
    mock_client.call_tool.side_effect = Exception("API Error")
    
    adapter = GoogleDocsAdapter(mcp_client=mock_client)
    adapter.config = mock_config.google_docs
    
    with pytest.raises(Exception):
        await adapter.deliver_pulse("content")
