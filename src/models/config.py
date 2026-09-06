from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    name: str
    package_id: str
    store: str
    play_store_url: str

class CollectionConfig(BaseModel):
    max_reviews: int = 500
    min_review_threshold: int = 10
    min_word_count: int = 10
    reporting_period_days: int = 7
    historical_comparison_periods: int = 1
    pagination_limit: int = 100

class AnalysisConfig(BaseModel):
    llm_model: str = "opengpt-oss-120b"
    llm_temperature: float = 0.2
    batch_size: int = 30
    max_retries: int = 3
    retry_backoff_seconds: int = 2
    sentiment_labels: List[str] = ["positive", "neutral", "negative", "mixed"]
    custom_categories: List[str] = Field(default_factory=list)

class PriorityConfig(BaseModel):
    weights: Dict[str, float] = {
        "frequency": 0.20,
        "negative_sentiment": 0.20,
        "severity_language": 0.15,
        "recency": 0.10,
        "growth": 0.15,
        "breadth": 0.10,
        "business_impact": 0.10
    }
    thresholds: Dict[str, float] = {
        "critical": 0.85,
        "high": 0.65,
        "medium": 0.40,
        "low": 0.0
    }

class DeduplicationConfig(BaseModel):
    exact_match: bool = True
    near_duplicate_threshold: float = 0.85

class GoogleDocsConfig(BaseModel):
    mode: str = "append"
    document_id: str = ""
    separator: str = "--- WEEK SEPARATOR ---"

class GmailConfig(BaseModel):
    create_draft: bool = True
    auto_send: bool = False
    recipients: List[str] = Field(default_factory=list)

class McpConfig(BaseModel):
    server_url: str = "https://mymcpserver-production-131e.up.railway.app/sse"
    api_key: str = "a8b4f2c9e7d341a296f8b5e1c4d7a3f0"

class DeliveryConfig(BaseModel):
    google_docs: GoogleDocsConfig = Field(default_factory=GoogleDocsConfig)
    gmail: GmailConfig = Field(default_factory=GmailConfig)
    mcp: McpConfig = Field(default_factory=McpConfig)

class StorageConfig(BaseModel):
    backend: str = "json_file"
    data_dir: str = "./data"

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"
    sanitize_pii: bool = True

class SchedulingConfig(BaseModel):
    enabled: bool = False
    cron_expression: str = "0 8 * * 1"

class AgentConfig(BaseModel):
    app: AppConfig
    collection: CollectionConfig = Field(default_factory=CollectionConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    priority: PriorityConfig = Field(default_factory=PriorityConfig)
    deduplication: DeduplicationConfig = Field(default_factory=DeduplicationConfig)
    delivery: DeliveryConfig = Field(default_factory=DeliveryConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    scheduling: SchedulingConfig = Field(default_factory=SchedulingConfig)
