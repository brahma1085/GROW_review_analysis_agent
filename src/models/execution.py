from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from src.generation.report_validator import ValidationResult

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

class CollectionSummary(BaseModel):
    status: str
    total_fetched: int
    error: Optional[str] = None

class ProcessingSummary(BaseModel):
    normalized_count: int
    unique_count: int
    dropped_count: int

class AnalysisSummary(BaseModel):
    analyzed_count: int
    themes_discovered: int
    trends_analyzed: bool
    prioritized_themes: int

class DeliverySummary(BaseModel):
    docs_success: bool
    gmail_success: bool
    docs_url: Optional[str] = None
    gmail_draft_id: Optional[str] = None
    error: Optional[str] = None

class ExecutionReport(BaseModel):
    run_id: str
    status: str              # "success" | "partial_success" | "failed"
    app_id: str
    reporting_period: DateRange
    collection: Optional[CollectionSummary] = None
    processing: Optional[ProcessingSummary] = None
    analysis: Optional[AnalysisSummary] = None
    delivery: Optional[DeliverySummary] = None
    validation: Optional[ValidationResult] = None
    duration_seconds: float
    timestamp: datetime
    warnings: List[str] = []
    errors: List[str] = []
