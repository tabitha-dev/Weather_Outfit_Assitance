"""
Metrics Collection for Google Cloud Monitoring

Tracks:
- Agent call latency
- Tool execution time
- Error rates
- Request counts
"""

import time
import os
from typing import Dict, Optional, Any
from contextlib import contextmanager

# Try to import Google Cloud Monitoring
try:
    from google.cloud import monitoring_v3
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️  Google Cloud Monitoring not available (install google-cloud-monitoring)")


class MetricsCollector:
    """Collects and sends metrics to Google Cloud Monitoring"""
    
    # Define complete label schemas for all metrics
    # Must match exactly what's provided when calling increment_counter or record_latency
    METRIC_SCHEMAS = {
        "agent_call_latency": ["agent"],  # Only agent label, no status
        "agent_calls": ["agent", "status"],
        "agent_requests": ["agent", "status"],
        "agent_request_latency": ["agent", "status"],
        "tool_execution_latency": ["tool"],  # Only tool label, no status
        "tool_calls": ["tool", "status"],
        "http_request_latency": ["service", "method", "path", "status"],
        "http_requests": ["service", "method", "status"],
    }
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.enabled = MONITORING_AVAILABLE and self.project_id is not None
        self._descriptors_created: set = set()
        
        if self.enabled:
            try:
                self.client = monitoring_v3.MetricServiceClient()
                self.project_name = f"projects/{self.project_id}"
                print(f"✅ Metrics enabled for project: {self.project_id}")
            except Exception as e:
                print(f"⚠️  Metrics client init failed: {e}")
                self.enabled = False
        else:
            self.client = None
            if not self.project_id:
                print("ℹ️  Metrics disabled (GOOGLE_CLOUD_PROJECT not set)")
        
        # In-memory counters for local tracking
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, list] = {}
    
    def increment_counter(self, metric_name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = f"{metric_name}:{labels or {}}"
        self.counters[key] = self.counters.get(key, 0) + value
        
        if self.enabled:
            # Use gauge to report current count
            self._write_custom_metric(
                metric_type="gauge",
                metric_name=metric_name,
                value=self.counters[key],
                labels=labels or {}
            )
    
    def record_latency(self, metric_name: str, duration_ms: float, labels: Optional[Dict[str, str]] = None):
        """Record a latency/duration metric"""
        key = f"{metric_name}:{labels or {}}"
        if key not in self.timers:
            self.timers[key] = []
        self.timers[key].append(duration_ms)
        
        if self.enabled:
            self._write_custom_metric(
                metric_type="gauge",
                metric_name=metric_name,
                value=duration_ms,
                labels=labels or {}
            )
    
    @contextmanager
    def measure_time(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager to measure execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.record_latency(metric_name, duration_ms, labels)
    
    def _ensure_metric_descriptor(self, metric_name: str, metric_type: str):
        """Ensure metric descriptor exists before writing metrics"""
        if not self.enabled or not self.client:
            return
        
        descriptor_key = f"{metric_name}:{metric_type}"
        if descriptor_key in self._descriptors_created:
            return
        
        try:
            metric_descriptor = monitoring_v3.MetricDescriptor()
            metric_descriptor.type = f"custom.googleapis.com/agent/{metric_name}"
            metric_descriptor.display_name = metric_name.replace("_", " ").title()
            metric_descriptor.description = f"Custom metric for {metric_name}"
            
            # All metrics are GAUGE for simplicity
            metric_descriptor.metric_kind = monitoring_v3.MetricDescriptor.MetricKind.GAUGE
            
            metric_descriptor.value_type = monitoring_v3.MetricDescriptor.ValueType.DOUBLE
            
            # Add ALL possible label descriptors from schema
            label_keys = self.METRIC_SCHEMAS.get(metric_name, [])
            for key in label_keys:
                label = monitoring_v3.LabelDescriptor()
                label.key = key
                label.value_type = monitoring_v3.LabelDescriptor.ValueType.STRING
                metric_descriptor.labels.append(label)
            
            # Create descriptor (idempotent - won't fail if already exists)
            try:
                self.client.create_metric_descriptor(
                    name=self.project_name,
                    metric_descriptor=metric_descriptor
                )
                self._descriptors_created.add(descriptor_key)
            except Exception as e:
                if "already exists" in str(e).lower():
                    self._descriptors_created.add(descriptor_key)
                else:
                    raise
                    
        except Exception as e:
            print(f"⚠️  Metric descriptor creation failed for {metric_name}: {e}")
    
    def _write_custom_metric(
        self, 
        metric_type: str, 
        metric_name: str, 
        value: float,
        labels: Dict[str, str]
    ):
        """Write custom metric to Cloud Monitoring"""
        if not self.enabled or not self.client:
            return
        
        try:
            # Ensure descriptor exists
            self._ensure_metric_descriptor(metric_name, metric_type)
            
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/agent/{metric_name}"
            
            # Add labels
            for key, val in labels.items():
                series.metric.labels[key] = str(val)
            
            # Set resource
            series.resource.type = "global"
            
            # Create point
            point = monitoring_v3.Point()
            point.value.double_value = float(value)
            
            # Set timestamp (GAUGE metrics only need end_time)
            now = time.time()
            point.interval.end_time.seconds = int(now)
            point.interval.end_time.nanos = int((now - int(now)) * 10**9)
            
            series.points = [point]
            
            # Write to Cloud Monitoring
            self.client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
        except Exception as e:
            # Don't fail the application if metrics fail
            print(f"⚠️  Metrics write failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics statistics"""
        stats = {
            "counters": dict(self.counters),
            "latencies": {}
        }
        
        # Calculate average latencies
        for key, values in self.timers.items():
            if values:
                stats["latencies"][key] = {
                    "count": len(values),
                    "avg_ms": sum(values) / len(values),
                    "min_ms": min(values),
                    "max_ms": max(values)
                }
        
        return stats


# Global metrics collector instance
agent_metrics = MetricsCollector()


# Convenience decorators
def track_agent_call(agent_name: str):
    """Decorator to track agent calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with agent_metrics.measure_time("agent_call_latency", {"agent": agent_name}):
                try:
                    result = func(*args, **kwargs)
                    agent_metrics.increment_counter("agent_calls", labels={"agent": agent_name, "status": "success"})
                    return result
                except Exception as e:
                    agent_metrics.increment_counter("agent_calls", labels={"agent": agent_name, "status": "error"})
                    raise
        return wrapper
    return decorator


def track_tool_execution(tool_name: str):
    """Decorator to track tool executions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with agent_metrics.measure_time("tool_execution_latency", {"tool": tool_name}):
                try:
                    result = func(*args, **kwargs)
                    agent_metrics.increment_counter("tool_calls", labels={"tool": tool_name, "status": "success"})
                    return result
                except Exception as e:
                    agent_metrics.increment_counter("tool_calls", labels={"tool": tool_name, "status": "error"})
                    raise
        return wrapper
    return decorator
