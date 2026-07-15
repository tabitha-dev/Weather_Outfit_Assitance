"""
Google Cloud Monitoring Dashboards

Creates pre-configured dashboards for Weather Outfit ADK monitoring.
"""

import os
from typing import Optional

try:
    from google.cloud import monitoring_v3
    DASHBOARDS_AVAILABLE = True
except ImportError:
    DASHBOARDS_AVAILABLE = False


def create_agent_dashboard(project_id: Optional[str] = None) -> Optional[str]:
    """
    Create a Cloud Monitoring dashboard for agent metrics
    
    Args:
        project_id: Google Cloud project ID (uses env var if not provided)
    
    Returns:
        Dashboard name or None if creation failed
    """
    if not DASHBOARDS_AVAILABLE:
        print("⚠️  Dashboard creation requires google-cloud-monitoring")
        return None
    
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("⚠️  GOOGLE_CLOUD_PROJECT not set")
        return None
    
    try:
        client = monitoring_v3.DashboardsServiceClient()
        project_name = f"projects/{project_id}"
        
        dashboard = {
            "display_name": "Weather Outfit ADK - Agent Metrics",
            "mosaic_layout": {
                "columns": 12,
                "tiles": [
                    # Agent Call Latency
                    {
                        "width": 6,
                        "height": 4,
                        "widget": {
                            "title": "Agent Call Latency (ms)",
                            "xy_chart": {
                                "data_sets": [{
                                    "time_series_query": {
                                        "time_series_filter": {
                                            "filter": f'resource.type="global" AND metric.type="custom.googleapis.com/agent/agent_call_latency"',
                                            "aggregation": {
                                                "alignment_period": {"seconds": 60},
                                                "per_series_aligner": "ALIGN_MEAN"
                                            }
                                        }
                                    },
                                    "plot_type": "LINE"
                                }],
                                "y_axis": {
                                    "label": "Latency (ms)",
                                    "scale": "LINEAR"
                                }
                            }
                        }
                    },
                    # Agent Call Count
                    {
                        "x_pos": 6,
                        "width": 6,
                        "height": 4,
                        "widget": {
                            "title": "Agent Calls (per minute)",
                            "xy_chart": {
                                "data_sets": [{
                                    "time_series_query": {
                                        "time_series_filter": {
                                            "filter": f'resource.type="global" AND metric.type="custom.googleapis.com/agent/agent_calls"',
                                            "aggregation": {
                                                "alignment_period": {"seconds": 60},
                                                "per_series_aligner": "ALIGN_RATE"
                                            }
                                        }
                                    },
                                    "plot_type": "STACKED_AREA"
                                }],
                                "y_axis": {
                                    "label": "Calls/min",
                                    "scale": "LINEAR"
                                }
                            }
                        }
                    },
                    # Tool Execution Time
                    {
                        "y_pos": 4,
                        "width": 6,
                        "height": 4,
                        "widget": {
                            "title": "Tool Execution Time (ms)",
                            "xy_chart": {
                                "data_sets": [{
                                    "time_series_query": {
                                        "time_series_filter": {
                                            "filter": f'resource.type="global" AND metric.type="custom.googleapis.com/agent/tool_execution_latency"',
                                            "aggregation": {
                                                "alignment_period": {"seconds": 60},
                                                "per_series_aligner": "ALIGN_MEAN"
                                            }
                                        }
                                    },
                                    "plot_type": "LINE"
                                }],
                                "y_axis": {
                                    "label": "Latency (ms)"
                                }
                            }
                        }
                    },
                    # Error Rate
                    {
                        "x_pos": 6,
                        "y_pos": 4,
                        "width": 6,
                        "height": 4,
                        "widget": {
                            "title": "Error Rate",
                            "xy_chart": {
                                "data_sets": [{
                                    "time_series_query": {
                                        "time_series_filter": {
                                            "filter": f'resource.type="global" AND metric.type="custom.googleapis.com/agent/agent_calls" AND metric.label.status="error"',
                                            "aggregation": {
                                                "alignment_period": {"seconds": 60},
                                                "per_series_aligner": "ALIGN_RATE"
                                            }
                                        }
                                    },
                                    "plot_type": "LINE"
                                }],
                                "y_axis": {
                                    "label": "Errors/min"
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Create dashboard
        created_dashboard = client.create_dashboard(
            parent=project_name,
            dashboard=dashboard
        )
        
        dashboard_name = created_dashboard.name
        print(f"✅ Dashboard created: {dashboard_name}")
        print(f"   View at: https://console.cloud.google.com/monitoring/dashboards/custom/{dashboard_name.split('/')[-1]}?project={project_id}")
        
        return dashboard_name
        
    except Exception as e:
        print(f"❌ Dashboard creation failed: {e}")
        return None


if __name__ == "__main__":
    # Create dashboard when run directly
    create_agent_dashboard()
