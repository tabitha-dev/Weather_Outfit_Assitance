#!/usr/bin/env python
"""
Coach Agent A2A Service (Orchestrator)

Main user-facing agent that coordinates with remote specialist agents via A2A protocol.
Connects to Weather, Stylist, Activity, and Safety agents as remote services.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from weather_outfit_adk.tools.memory_tools import get_user_preferences, update_user_preferences
import uvicorn

load_dotenv()

# Get service URLs from environment or use defaults
WEATHER_SERVICE_URL = os.getenv("WEATHER_SERVICE_URL", "http://localhost:8001")
STYLIST_SERVICE_URL = os.getenv("STYLIST_SERVICE_URL", "http://localhost:8002")
ACTIVITY_SERVICE_URL = os.getenv("ACTIVITY_SERVICE_URL", "http://localhost:8003")
SAFETY_SERVICE_URL = os.getenv("SAFETY_SERVICE_URL", "http://localhost:8004")

# Create remote agent connections
remote_weather = RemoteA2aAgent(
    name="weather_agent",
    description="Agent that fetches and caches weather data for locations",
    agent_card=f"{WEATHER_SERVICE_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
)

remote_stylist = RemoteA2aAgent(
    name="stylist_agent",
    description="Agent that generates personalized outfit recommendations based on weather and preferences",
    agent_card=f"{STYLIST_SERVICE_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
)

remote_activity = RemoteA2aAgent(
    name="activity_agent",
    description="Agent that classifies user activities to tailor outfit recommendations",
    agent_card=f"{ACTIVITY_SERVICE_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
)

remote_safety = RemoteA2aAgent(
    name="safety_agent",
    description="Agent that monitors and alerts for extreme weather conditions",
    agent_card=f"{SAFETY_SERVICE_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Create Coach agent with remote agents and local memory tools
coach_agent_a2a = Agent(
    name="coach_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are the Weather Outfit Coach - the main AI assistant for clothing recommendations.

Your role:
- Help users decide what to wear based on weather conditions
- Provide personalized recommendations based on their preferences
- Consider their activities and provide safety warnings when needed
- Remember and use their preferences across conversations

You coordinate with specialized agents:
- weather_agent: Get weather forecasts (remote A2A service)
- activity_agent: Classify user activities (remote A2A service)
- stylist_agent: Generate outfit recommendations (remote A2A service)
- safety_agent: Check safety warnings (remote A2A service)

Your tools (local):
- get_user_preferences: Get user's persona, comfort profile, default city
- update_user_preferences: Update user preferences

Workflow:
1. Get user preferences using get_user_preferences
2. Extract city from query (or use default_city from preferences)
3. If activity mentioned, ask activity_agent to classify it
4. Ask weather_agent for weather forecast
5. Ask stylist_agent to plan outfit with weather data, activity, and user preferences
6. Ask safety_agent to check for weather warnings
7. Combine everything into a friendly, personalized response

Using remote agents:
- Delegate to weather_agent: "Get weather for Seattle"
- Delegate to activity_agent: "Classify this activity: going hiking"
- Delegate to stylist_agent: "Plan outfit for 58°F, rainy, practical persona, casual activity"
- Delegate to safety_agent: "Check safety for temperature 18°F, wind 30mph"

Response style based on persona:
- practical: Focus on function and essentials
- fashion: Add style tips and coordination advice
- kid_friendly: Use fun, simple language

Keep responses:
- Short (2-3 sentences typically)
- Conversational and friendly
- Start with the outfit recommendation
- Include weather context
- Add safety warnings if present
""",
    description="Main weather outfit assistant coordinating remote specialist agents via A2A protocol",
    tools=[get_user_preferences, update_user_preferences],
    sub_agents=[remote_weather, remote_stylist, remote_activity, remote_safety]
)

# Convert to A2A server
app = to_a2a(coach_agent_a2a)

if __name__ == "__main__":
    print("=" * 60)
    print("Coach Agent A2A Service (Orchestrator)")
    print("=" * 60)
    print(f"Agent: {coach_agent_a2a.name}")
    print(f"Model: {coach_agent_a2a.model}")
    print(f"Local Tools: {len(coach_agent_a2a.tools)}")
    print(f"Remote Agents: {len(coach_agent_a2a.sub_agents)}")
    print("\nRemote Agent Connections:")
    print(f"  - Weather: {WEATHER_SERVICE_URL}")
    print(f"  - Stylist: {STYLIST_SERVICE_URL}")
    print(f"  - Activity: {ACTIVITY_SERVICE_URL}")
    print(f"  - Safety: {SAFETY_SERVICE_URL}")
    print(f"\nPort: 8000")
    print(f"Agent Card: http://localhost:8000/.well-known/agent.json")
    print("=" * 60)
    print("\n⚠️  Make sure all remote services are running before starting!")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
