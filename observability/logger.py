import structlog
from typing import Optional

from config import settings

def _setup_structlog() -> None:
    """Configures structlog processors depending on the log level."""
    if structlog.is_configured():
        return

    is_development = settings.LOG_LEVEL.upper() == "DEBUG"

    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,     
        structlog.stdlib.add_log_level,       
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"), 
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    formatter = (
        structlog.dev.ConsoleRenderer(colors=True)
        if is_development
        else structlog.processors.JSONRenderer()
    )

    processors = shared_processors + [formatter]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

_setup_structlog()

def get_logger(name: str) -> structlog.BoundLogger:
    """
    Returns a configured structlog BoundLogger wrapping stdlib logger 
    with the required static base properties injected into the root bound context.
    """
    logger = structlog.get_logger(name)
    return logger.bind(service="resume-screener")

def log_screening_run(
    logger: structlog.BoundLogger,
    n_resumes: int,
    processing_time: float,
    top_score: float,
    error: Optional[str] = None
) -> None:
    """
    Helper function emitting structured analytical payload metrics encompassing 
    a particular screening task conclusion.
    """
    event_dict = {
        "n_resumes": n_resumes,
        "processing_time": round(processing_time, 2),
        "top_score": round(top_score, 4)
    }

    if error:
        event_dict["error_detail"] = error
        logger.error("Screening run failed", **event_dict)
    else:
        logger.info("Screening run completed", **event_dict)

# Sets up structlog with console (dev) or JSON (prod) rendering, exposes `get_logger()` for service-bound loggers, and provides `log_screening_run()` to emit structured metrics after each screening pipeline execution.
