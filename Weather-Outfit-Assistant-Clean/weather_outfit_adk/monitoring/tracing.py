"""
OpenTelemetry Tracing Configuration

Provides distributed tracing for agent-to-agent calls.
"""

import os
from typing import Optional, Callable, Any
from contextlib import contextmanager

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode, Tracer
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.sdk.resources import Resource
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    trace = None
    Status = None
    StatusCode = None
    Tracer = type(None)  # Type placeholder
    print("ℹ️  OpenTelemetry not available (install opentelemetry packages)")


# Global tracer
_tracer: Optional[Any] = None


def setup_tracing(service_name: str) -> Optional[Any]:
    """
    Set up OpenTelemetry tracing with Cloud Trace export
    
    Args:
        service_name: Name of the service being traced
    
    Returns:
        Tracer instance or None if tracing unavailable
    """
    global _tracer
    
    if not TRACING_AVAILABLE:
        print("ℹ️  Tracing disabled (OpenTelemetry not installed)")
        return None
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("ℹ️  Tracing disabled (GOOGLE_CLOUD_PROJECT not set)")
        return None
    
    try:
        # Create resource with service info
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
        })
        
        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)
        
        # Add Cloud Trace exporter
        cloud_trace_exporter = CloudTraceSpanExporter(project_id=project_id)
        span_processor = BatchSpanProcessor(cloud_trace_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        # Get tracer
        _tracer = trace.get_tracer(service_name)
        
        print(f"✅ Tracing enabled for {service_name} (project: {project_id})")
        return _tracer
        
    except Exception as e:
        print(f"⚠️  Tracing setup failed: {e}")
        return None


def get_tracer() -> Optional[Any]:
    """Get the current tracer instance"""
    return _tracer


@contextmanager
def trace_agent_call(agent_name: str, operation: str = "call"):
    """
    Context manager to trace an agent call
    
    Args:
        agent_name: Name of the agent being called
        operation: Operation being performed
    
    Example:
        with trace_agent_call("weather_agent", "get_forecast"):
            result = weather_agent.call(...)
    """
    if _tracer is None or Status is None:
        yield
        return
    
    with _tracer.start_as_current_span(f"{agent_name}.{operation}") as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.operation", operation)
        try:
            yield span
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def trace_tool_call(tool_name: str):
    """
    Decorator to trace tool calls
    
    Args:
        tool_name: Name of the tool
    
    Example:
        @trace_tool_call("get_weather")
        def get_current_weather(city: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if _tracer is None or Status is None:
                return func(*args, **kwargs)
            
            with _tracer.start_as_current_span(f"tool.{tool_name}") as span:
                span.set_attribute("tool.name", tool_name)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
