import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

from src.models.config import AgentConfig

class ConfigManager:
    _instance: Optional[AgentConfig] = None

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> AgentConfig:
        """Load configuration from YAML, apply env vars, and validate."""
        # Load .env file
        load_dotenv()
        
        # Determine config path, override with env if available
        env_config_path = os.getenv("GROWW_AGENT_CONFIG_PATH")
        if env_config_path and Path(env_config_path).exists():
            config_path = env_config_path
            
        config_data = {}
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
                
        # Handle env overrides specifically mentioned in architecture
        if app_id := os.getenv("GROWW_AGENT_APP_ID"):
            if "app" not in config_data:
                config_data["app"] = {}
            config_data["app"]["package_id"] = app_id
            
        if llm_model := os.getenv("GROWW_AGENT_LLM_MODEL"):
            if "analysis" not in config_data:
                config_data["analysis"] = {}
            config_data["analysis"]["llm_model"] = llm_model
            
        if log_level := os.getenv("GROWW_AGENT_LOG_LEVEL"):
            if "logging" not in config_data:
                config_data["logging"] = {}
            config_data["logging"]["level"] = log_level
            
        if data_dir := os.getenv("GROWW_AGENT_DATA_DIR"):
            if "storage" not in config_data:
                config_data["storage"] = {}
            config_data["storage"]["data_dir"] = data_dir
            
        if doc_id := os.getenv("GROWW_AGENT_GOOGLE_DOC_ID"):
            if "delivery" not in config_data:
                config_data["delivery"] = {}
            if "google_docs" not in config_data["delivery"]:
                config_data["delivery"]["google_docs"] = {}
            config_data["delivery"]["google_docs"]["document_id"] = doc_id
            
        if recipients := os.getenv("GROWW_AGENT_GMAIL_RECIPIENTS"):
            if "delivery" not in config_data:
                config_data["delivery"] = {}
            if "gmail" not in config_data["delivery"]:
                config_data["delivery"]["gmail"] = {}
            config_data["delivery"]["gmail"]["recipients"] = [r.strip() for r in recipients.split(",") if r.strip()]
            
        if mcp_server_url := os.getenv("GROWW_AGENT_MCP_SERVER_URL"):
            if "delivery" not in config_data:
                config_data["delivery"] = {}
            if "mcp" not in config_data["delivery"]:
                config_data["delivery"]["mcp"] = {}
            config_data["delivery"]["mcp"]["server_url"] = mcp_server_url
            
        if mcp_api_key := os.getenv("GROWW_AGENT_MCP_API_KEY"):
            if "delivery" not in config_data:
                config_data["delivery"] = {}
            if "mcp" not in config_data["delivery"]:
                config_data["delivery"]["mcp"] = {}
            config_data["delivery"]["mcp"]["api_key"] = mcp_api_key

        # Pydantic will validate the loaded dictionary against AgentConfig schema
        cls._instance = AgentConfig(**config_data)
        return cls._instance

    @classmethod
    def get_config(cls) -> AgentConfig:
        """Get the singleton configuration instance, loading if necessary."""
        if cls._instance is None:
            return cls.load()
        return cls._instance
