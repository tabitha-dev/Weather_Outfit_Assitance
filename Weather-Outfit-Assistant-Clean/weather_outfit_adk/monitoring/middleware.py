"""
Monitoring Middleware for A2A Services

Automatically adds monitoring to ADK agents and A2A services.
"""

from typing import Callable, Any
import time
from .metrics import agent_metrics
from .logging_config import get_logger

logger = get_logger(__name__)


class MonitoringMiddleware:
    """Middleware to add monitoring to agent calls"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = get_logger(agent_name)
    
    async def __call__(self, request: Any, call_next: Callable) -> Any:
        """Process request with monitoring"""
        start_time = time.time()
        
        # Log request
        self.logger.info(f"Agent call started: {self.agent_name}")
        
        try:
            # Execute the agent call
            response = await call_next(request)
            
            # Record success metrics
            duration_ms = (time.time() - start_time) * 1000
            agent_metrics.record_latency(
                "agent_request_latency",
                duration_ms,
                labels={"agent": self.agent_name, "status": "success"}
            )
            agent_metrics.increment_counter(
                "agent_requests",
                labels={"agent": self.agent_name, "status": "success"}
            )
            
            self.logger.info(
                f"Agent call completed: {self.agent_name} ({duration_ms:.2f}ms)"
            )
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration_ms = (time.time() - start_time) * 1000
            agent_metrics.record_latency(
                "agent_request_latency",
                duration_ms,
                labels={"agent": self.agent_name, "status": "error"}
            )
            agent_metrics.increment_counter(
                "agent_requests",
                labels={"agent": self.agent_name, "status": "error"}
            )
            
            self.logger.error(
                f"Agent call failed: {self.agent_name} - {str(e)} ({duration_ms:.2f}ms)"
            )
            
            raise


def add_monitoring_to_app(app: Any, service_name: str):
    """
    Add monitoring middleware to a FastAPI/Uvicorn app
    
    Args:
        app: The FastAPI application
        service_name: Name of the service for metrics labeling
    """
    # Add middleware
    try:
        from starlette.middleware.base import BaseHTTPMiddleware
        
        class MetricsMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                start_time = time.time()
                
                # Process request
                response = await call_next(request)
                
                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                agent_metrics.record_latency(
                    "http_request_latency",
                    duration_ms,
                    labels={
                        "service": service_name,
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code
                    }
                )
                agent_metrics.increment_counter(
                    "http_requests",
                    labels={
                        "service": service_name,
                        "method": request.method,
                        "status": response.status_code
                    }
                )
                
                return response
        
        app.add_middleware(MetricsMiddleware)
        logger.info(f"✅ Monitoring middleware added to {service_name}")
        
    except ImportError:
        logger.warning("⚠️  Starlette not available, skipping middleware")
