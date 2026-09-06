import json
from io import StringIO
import structlog
from src.observability.logger import get_logger

def test_logger_json_output_and_run_id():
    # Setup in-memory stream for testing
    stream = StringIO()
    
    # We need to re-configure structlog to write to our stream for testing
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(file=stream),
        cache_logger_on_first_use=False
    )
    
    logger = get_logger("test_component")
    
    # Bind run_id
    bound_logger = logger.bind(run_id="run_123")
    bound_logger.info("test_event", foo="bar")
    
    # Verify output
    log_output = stream.getvalue().strip()
    log_data = json.loads(log_output)
    
    assert log_data["event"] == "test_event"
    assert log_data["run_id"] == "run_123"
    assert log_data["foo"] == "bar"
    assert log_data["level"] == "info"
    assert "timestamp" in log_data

def test_pii_sanitization():
    stream = StringIO()
    
    from src.observability.logger import sanitize_pii_filter
    
    structlog.configure(
        processors=[
            sanitize_pii_filter,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(file=stream),
        cache_logger_on_first_use=False
    )
    
    logger = get_logger("test_pii")
    logger.info("found_review", reviewer_name="John Doe", review_id="abc")
    
    log_output = stream.getvalue().strip()
    log_data = json.loads(log_output)
    
    assert log_data["reviewer_name"] == "***"
    assert log_data["review_id"] == "abc"
