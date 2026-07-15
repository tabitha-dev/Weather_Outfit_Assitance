"""
Alert Policy Management for Google Cloud Monitoring

Creates and manages alert policies for:
- High error rates
- High latency
- Low availability
"""

import os
from typing import Optional, List, Dict

try:
    from google.cloud import monitoring_v3
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️  Google Cloud Monitoring not available")


class AlertPolicyManager:
    """Manages alert policies for Weather Outfit ADK"""
    
    def __init__(self, project_id: Optional[str] = None, notification_channels: Optional[List[str]] = None):
        """
        Initialize alert policy manager
        
        Args:
            project_id: Google Cloud project ID
            notification_channels: List of notification channel IDs
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.notification_channels = notification_channels or []
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set")
        
        if MONITORING_AVAILABLE:
            self.client = monitoring_v3.AlertPolicyServiceClient()
            self.project_name = f"projects/{self.project_id}"
        else:
            raise ImportError("google-cloud-monitoring is required for alert management")
    
    def create_high_error_rate_alert(self, errors_per_minute: float = 5, duration_seconds: int = 300) -> str:
        """
        Create alert for high error rate (NOT a percentage/ratio alert)
        
        This triggers when the error rate (errors/second averaged over 1 minute) exceeds the threshold.
        It does NOT compute error percentage. For percentage-based alerts that compute
        errors/(errors+successes), see ALERTS.md for MQL examples.
        
        Args:
            errors_per_minute: Error rate threshold in errors/minute (default 5 = 0.083 errors/sec)
            duration_seconds: Duration to evaluate (default 5 minutes)
        
        Returns:
            Alert policy name
        """
        # Convert errors/minute to errors/second for ALIGN_RATE
        errors_per_second = errors_per_minute / 60
        
        policy = monitoring_v3.AlertPolicy()
        policy.display_name = "Weather Outfit ADK - High Error Rate"
        policy.documentation.content = (
            f"Error rate exceeded {errors_per_minute} errors/min ({errors_per_second:.3f} errors/sec) for {duration_seconds} seconds. "
            "This may indicate an issue with agent operations or external API calls. "
            f"Note: This tracks error rate using ALIGN_RATE. For percentage-based tracking, see ALERTS.md."
        )
        
        # Condition: error rate > threshold
        condition = monitoring_v3.AlertPolicy.Condition()
        condition.display_name = f"Errors > {errors_per_minute}/min"
        condition.condition_threshold.filter = (
            'resource.type="global" '
            'AND metric.type="custom.googleapis.com/agent/agent_calls" '
            'AND metric.label.status="error"'
        )
        condition.condition_threshold.comparison = monitoring_v3.ComparisonType.COMPARISON_GT
        condition.condition_threshold.threshold_value = errors_per_second
        condition.condition_threshold.duration.seconds = duration_seconds
        condition.condition_threshold.aggregations.append(
            monitoring_v3.Aggregation(
                alignment_period={"seconds": 60},
                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
            )
        )
        
        policy.conditions.append(condition)
        policy.combiner = monitoring_v3.AlertPolicy.ConditionCombinerType.OR
        
        # Add notification channels if provided
        for channel in self.notification_channels:
            policy.notification_channels.append(channel)
        
        # Create policy
        created_policy = self.client.create_alert_policy(
            name=self.project_name,
            alert_policy=policy
        )
        
        print(f"✅ Created alert policy: {created_policy.name}")
        return created_policy.name
    
    def create_high_latency_alert(self, threshold_ms: float = 2000, duration_seconds: int = 180) -> str:
        """
        Create alert for high agent latency (>2s by default)
        
        Args:
            threshold_ms: Latency threshold in milliseconds
            duration_seconds: Duration to evaluate (default 3 minutes)
        
        Returns:
            Alert policy name
        """
        policy = monitoring_v3.AlertPolicy()
        policy.display_name = "Weather Outfit ADK - High Agent Latency"
        policy.documentation.content = (
            f"Agent response time exceeded {threshold_ms}ms for {duration_seconds} seconds. "
            "This may indicate slow external API calls or resource constraints."
        )
        
        # Condition: P95 latency > threshold
        condition = monitoring_v3.AlertPolicy.Condition()
        condition.display_name = f"Latency > {threshold_ms}ms"
        condition.condition_threshold.filter = (
            'resource.type="global" '
            'AND metric.type="custom.googleapis.com/agent/agent_call_latency"'
        )
        condition.condition_threshold.comparison = monitoring_v3.ComparisonType.COMPARISON_GT
        condition.condition_threshold.threshold_value = threshold_ms
        condition.condition_threshold.duration.seconds = duration_seconds
        condition.condition_threshold.aggregations.append(
            monitoring_v3.Aggregation(
                alignment_period={"seconds": 60},
                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95,
            )
        )
        
        policy.conditions.append(condition)
        policy.combiner = monitoring_v3.AlertPolicy.ConditionCombinerType.OR
        
        # Add notification channels
        for channel in self.notification_channels:
            policy.notification_channels.append(channel)
        
        # Create policy
        created_policy = self.client.create_alert_policy(
            name=self.project_name,
            alert_policy=policy
        )
        
        print(f"✅ Created alert policy: {created_policy.name}")
        return created_policy.name
    
    def create_low_success_rate_alert(self, min_successes_per_minute: float = 10, duration_seconds: int = 600) -> str:
        """
        Create alert for low success rate (NOT a percentage/ratio alert)
        
        This triggers when the success rate (successes/second averaged over 1 minute) drops below the threshold.
        It does NOT compute success percentage. For percentage-based alerts that compute
        successes/(errors+successes), see ALERTS.md for MQL examples.
        
        Args:
            min_successes_per_minute: Success rate threshold in successes/minute (default 10 = 0.167 successes/sec)
            duration_seconds: Duration to evaluate (default 10 minutes)
        
        Returns:
            Alert policy name
        """
        # Convert successes/minute to successes/second for ALIGN_RATE
        successes_per_second = min_successes_per_minute / 60
        
        policy = monitoring_v3.AlertPolicy()
        policy.display_name = "Weather Outfit ADK - Low Success Rate"
        policy.documentation.content = (
            f"Success rate dropped below {min_successes_per_minute} successes/min ({successes_per_second:.3f} successes/sec) for {duration_seconds} seconds. "
            "This indicates low traffic or failed agent calls. "
            f"Note: This tracks success rate using ALIGN_RATE. For percentage-based tracking, see ALERTS.md."
        )
        
        # Condition: success rate < threshold
        condition = monitoring_v3.AlertPolicy.Condition()
        condition.display_name = f"Successes < {min_successes_per_minute}/min"
        condition.condition_threshold.filter = (
            'resource.type="global" '
            'AND metric.type="custom.googleapis.com/agent/agent_calls" '
            'AND metric.label.status="success"'
        )
        condition.condition_threshold.comparison = monitoring_v3.ComparisonType.COMPARISON_LT
        condition.condition_threshold.threshold_value = successes_per_second
        condition.condition_threshold.duration.seconds = duration_seconds
        condition.condition_threshold.aggregations.append(
            monitoring_v3.Aggregation(
                alignment_period={"seconds": 60},
                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
            )
        )
        
        policy.conditions.append(condition)
        policy.combiner = monitoring_v3.AlertPolicy.ConditionCombinerType.OR
        
        # Add notification channels
        for channel in self.notification_channels:
            policy.notification_channels.append(channel)
        
        # Create policy
        created_policy = self.client.create_alert_policy(
            name=self.project_name,
            alert_policy=policy
        )
        
        print(f"✅ Created alert policy: {created_policy.name}")
        return created_policy.name
    
    def create_all_alerts(self) -> Dict[str, str]:
        """
        Create all recommended alert policies (rate-based)
        
        Note: These alerts monitor throughput rates (errors/min, successes/min).
        For percentage-based alerts (error rate, availability), see ALERTS.md for MQL examples.
        
        Returns:
            Dictionary mapping alert names to policy IDs
        """
        alerts = {}
        
        print("\n📊 Creating Alert Policies (Rate-Based)...")
        print("=" * 50)
        
        try:
            alerts["high_error_rate"] = self.create_high_error_rate_alert()
        except Exception as e:
            print(f"⚠️  Failed to create error rate alert: {e}")
        
        try:
            alerts["high_latency"] = self.create_high_latency_alert()
        except Exception as e:
            print(f"⚠️  Failed to create latency alert: {e}")
        
        try:
            alerts["low_success_rate"] = self.create_low_success_rate_alert()
        except Exception as e:
            print(f"⚠️  Failed to create success rate alert: {e}")
        
        print("=" * 50)
        print(f"✅ Created {len(alerts)} alert policies (rate-based)\n")
        print("ℹ️  For percentage-based alerts (error %, availability %), see ALERTS.md\n")
        
        return alerts
    
    def list_notification_channels(self) -> List[Dict]:
        """List available notification channels"""
        channels = []
        
        for channel in self.client.list_notification_channels(name=self.project_name):
            channels.append({
                "name": channel.name,
                "display_name": channel.display_name,
                "type": channel.type_,
                "enabled": channel.enabled
            })
        
        return channels


def create_notification_channel_email(project_id: str, email: str, display_name: str = "Weather Outfit Alerts") -> str:
    """
    Create an email notification channel
    
    Args:
        project_id: Google Cloud project ID
        email: Email address for notifications
        display_name: Display name for the channel
    
    Returns:
        Notification channel name
    """
    if not MONITORING_AVAILABLE:
        raise ImportError("google-cloud-monitoring is required")
    
    client = monitoring_v3.NotificationChannelServiceClient()
    project_name = f"projects/{project_id}"
    
    channel = monitoring_v3.NotificationChannel(
        type_="email",
        display_name=display_name,
        labels={"email_address": email},
        enabled=True
    )
    
    created_channel = client.create_notification_channel(
        name=project_name,
        notification_channel=channel
    )
    
    print(f"✅ Created notification channel: {created_channel.name}")
    return created_channel.name


if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] == "--create-all":
        manager = AlertPolicyManager()
        print("Creating rate-based alert policies...")
        alerts = manager.create_all_alerts()
        print(f"\n✅ Created {len(alerts)} alert policies (rate-based):")
        for name, policy in alerts.items():
            print(f"  - {name}: {policy}")
    else:
        print("Usage: python -m weather_outfit_adk.monitoring.alerts --create-all")
        print("\nOr use in code:")
        print("  from weather_outfit_adk.monitoring.alerts import AlertPolicyManager")
        print("  manager = AlertPolicyManager(notification_channels=['channel-id'])")
        print("  manager.create_all_alerts()")
        print("\nNote: Alerts use rate-based thresholds (errors/min converted to errors/sec).")
