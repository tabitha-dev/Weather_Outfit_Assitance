"""
Monitoring and Observability Module

Provides Google Cloud Monitoring integration for:
- Metrics (latency, errors, agent calls)
- Traces (OpenTelemetry distributed tracing)
- Logs (structured logging with Cloud Logging)

Quick Start:
    from weather_outfit_adk.monitoring import setup_logging, agent_metrics
    
    # Setup logging
    logger = setup_logging("my-service", enable_cloud_logging=True)
    
    # Track metrics
    with agent_metrics.measure_time("operation", labels={"agent": "weather"}):
        result = do_operation()
"""

from .metrics import MetricsCollector, agent_metrics
from .logging_config import setup_logging, get_logger
from .tracing import setup_tracing, trace_agent_call

__all__ = [
    "MetricsCollector",
    "agent_metrics",
    "setup_logging",
    "get_logger",
    "setup_tracing",
    "trace_agent_call",
]
