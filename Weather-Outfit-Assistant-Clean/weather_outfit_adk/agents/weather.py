from google.adk.agents import Agent
from ..tools.weather_tools import get_current_weather, get_hourly_forecast, get_weather_smart


weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a weather specialist agent.

Your role:
- Always call the weather tools before providing any weather information
- Never guess or use your training data for current weather conditions
- Return clean, structured forecast data
- Focus only on weather data, not clothing recommendations

Rules:
- Use get_weather_smart for efficiency (it caches results)
- Be precise with temperature, wind, and rain probability
- Keep responses focused on weather facts
- Format data clearly for other agents to use
""",
    description="Provides accurate weather forecasts by calling weather APIs",
    tools=[get_current_weather, get_hourly_forecast, get_weather_smart]
)
