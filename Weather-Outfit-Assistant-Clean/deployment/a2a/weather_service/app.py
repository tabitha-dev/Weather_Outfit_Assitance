#!/usr/bin/env python
"""
Weather Agent A2A Service

Exposes the weather agent as an independent A2A-compatible microservice.
Runs on port 8001 and provides weather forecast capabilities.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from weather_outfit_adk.agents.weather import weather_agent
import uvicorn

load_dotenv()

# Convert agent to A2A server (auto-generates agent card)
app = to_a2a(weather_agent)

if __name__ == "__main__":
    print("=" * 60)
    print("Weather Agent A2A Service")
    print("=" * 60)
    print(f"Agent: {weather_agent.name}")
    print(f"Model: {weather_agent.model}")
    print(f"Tools: {len(weather_agent.tools)}")
    print(f"Port: 8001")
    print(f"Agent Card: http://localhost:8001/.well-known/agent.json")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
