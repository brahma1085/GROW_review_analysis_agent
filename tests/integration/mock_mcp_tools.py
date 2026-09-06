class MockMCPClient:
    def __init__(self):
        self.calls = []
        self.should_fail = False
        self.fail_on_tool = None

    async def call_tool(self, tool_name: str, arguments: dict):
        self.calls.append({"tool": tool_name, "arguments": arguments})
        
        if self.should_fail or self.fail_on_tool == tool_name:
            raise Exception(f"Simulated MCP Failure for tool {tool_name}")
            
        if tool_name == "create_document":
            return {"doc_id": "mock_doc_id", "url": "https://docs.google.com/document/d/mock_doc_id"}
        elif tool_name == "append_formatted_content":
            return {"success": True}
        elif tool_name == "create_draft":
            return {"draft_id": "mock_draft_id", "success": True}
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
