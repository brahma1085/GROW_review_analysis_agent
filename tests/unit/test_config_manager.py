import os
from pathlib import Path
from src.config.manager import ConfigManager
from src.models.config import AgentConfig

def test_load_default_config():
    # Write a temporary config.yaml if it doesn't exist to test fallback or loading
    config = ConfigManager.load("config.yaml")
    assert isinstance(config, AgentConfig)
    assert config.app.package_id == "com.nextbillion.groww"
    
def test_env_overrides(monkeypatch):
    monkeypatch.setenv("GROWW_AGENT_APP_ID", "com.test.override")
    monkeypatch.setenv("GROWW_AGENT_LLM_MODEL", "test-model")
    
    config = ConfigManager.load("config.yaml")
    assert config.app.package_id == "com.test.override"
    assert config.analysis.llm_model == "test-model"
    
def test_singleton_behavior():
    config1 = ConfigManager.get_config()
    config2 = ConfigManager.get_config()
    assert config1 is config2
