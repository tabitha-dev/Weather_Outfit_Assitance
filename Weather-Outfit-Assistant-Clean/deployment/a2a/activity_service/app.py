#!/usr/bin/env python
"""
Activity Agent A2A Service

Exposes the activity agent as an independent A2A-compatible microservice.
Runs on port 8003 and provides activity classification capabilities.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from weather_outfit_adk.agents.activity import activity_agent
import uvicorn

load_dotenv()

# Convert agent to A2A server (auto-generates agent card)
app = to_a2a(activity_agent)

if __name__ == "__main__":
    print("=" * 60)
    print("Activity Agent A2A Service")
    print("=" * 60)
    print(f"Agent: {activity_agent.name}")
    print(f"Model: {activity_agent.model}")
    print(f"Tools: {len(activity_agent.tools)}")
    print(f"Port: 8003")
    print(f"Agent Card: http://localhost:8003/.well-known/agent.json")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
