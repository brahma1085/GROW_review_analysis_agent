import logging
import sys
import structlog
from typing import Any, Dict

def sanitize_pii_filter(logger: logging.Logger, log_method: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Basic PII sanitization filter for logs."""
    # We mask obvious fields if they appear in logs, e.g. "reviewer_name"
    for key, value in event_dict.items():
        if key == "reviewer_name" and isinstance(value, str):
            event_dict[key] = "***"
    return event_dict

def setup_logging(level: str = "INFO", sanitize_pii: bool = True) -> None:
    """Configure the structlog logging system."""
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if sanitize_pii:
        processors.append(sanitize_pii_filter)
        
    processors.append(structlog.processors.JSONRenderer())
        
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(component: str) -> structlog.BoundLogger:
    """Factory function to get a bound logger for a component."""
    # Ensure basic config is applied if get_logger is called before setup
    if not structlog.is_configured():
        setup_logging()
    return structlog.get_logger(component)
