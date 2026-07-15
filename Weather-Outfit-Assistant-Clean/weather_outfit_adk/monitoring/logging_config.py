"""
Structured Logging Configuration

Integrates with Google Cloud Logging for centralized log management.
"""

import logging
import os
import sys
from typing import Optional

# Try to import Google Cloud Logging
try:
    from google.cloud import logging as cloud_logging
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False


def setup_logging(
    service_name: str,
    level: str = "INFO",
    enable_cloud_logging: bool = True
) -> logging.Logger:
    """
    Set up logging with optional Cloud Logging integration
    
    Args:
        service_name: Name of the service (e.g., "coach-agent")
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        enable_cloud_logging: Whether to send logs to Cloud Logging
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Structured format
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "service": "' + service_name + '", "message": "%(message)s"}',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Cloud Logging integration
    if enable_cloud_logging and CLOUD_LOGGING_AVAILABLE:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if project_id:
            try:
                client = cloud_logging.Client(project=project_id)
                cloud_handler = client.get_default_handler()
                cloud_handler.setLevel(getattr(logging, level.upper()))
                logger.addHandler(cloud_handler)
                logger.info(f"✅ Cloud Logging enabled for {service_name}")
            except Exception as e:
                logger.warning(f"⚠️  Cloud Logging setup failed: {e}")
        else:
            logger.info("ℹ️  Cloud Logging disabled (GOOGLE_CLOUD_PROJECT not set)")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name or __name__)


# Create default logger
default_logger = setup_logging("weather-outfit-adk", enable_cloud_logging=False)
