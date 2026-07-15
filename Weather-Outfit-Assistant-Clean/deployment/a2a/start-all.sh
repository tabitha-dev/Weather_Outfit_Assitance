#!/bin/bash
# Start all A2A services locally (without Docker)

set -e

echo "======================================================================"
echo "Starting Weather Outfit ADK - A2A Multi-Service Architecture"
echo "======================================================================"

# Check if running in the deployment/a2a directory
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: Please run this script from deployment/a2a directory"
    exit 1
fi

# Load environment variables if .env exists
if [ -f "../../.env" ]; then
    echo "Loading environment variables from .env"
    export $(cat ../../.env | grep -v '^#' | xargs)
fi

mkdir -p logs

echo ""
echo "Starting services in background..."
echo ""

# Start Weather Agent (Port 8001)
echo "► Starting Weather Agent on port 8001..."
python weather_service/app.py > logs/weather.log 2>&1 &
WEATHER_PID=$!
sleep 2

# Start Stylist Agent (Port 8002)
echo "► Starting Stylist Agent on port 8002..."
python stylist_service/app.py > logs/stylist.log 2>&1 &
STYLIST_PID=$!
sleep 2

# Start Activity Agent (Port 8003)
echo "► Starting Activity Agent on port 8003..."
python activity_service/app.py > logs/activity.log 2>&1 &
ACTIVITY_PID=$!
sleep 2

# Start Safety Agent (Port 8004)
echo "► Starting Safety Agent on port 8004..."
python safety_service/app.py > logs/safety.log 2>&1 &
SAFETY_PID=$!
sleep 2

# Start Coach Agent (Port 8000)
echo "► Starting Coach Agent (Orchestrator) on port 8000..."
python coach_service/app.py > logs/coach.log 2>&1 &
COACH_PID=$!
sleep 3

echo ""
echo "======================================================================"
echo "✅ All services started!"
echo "======================================================================"
echo ""
echo "Service URLs:"
echo "  Coach (Main):    http://localhost:8000"
echo "  Weather Agent:   http://localhost:8001"
echo "  Stylist Agent:   http://localhost:8002"
echo "  Activity Agent:  http://localhost:8003"
echo "  Safety Agent:    http://localhost:8004"
echo ""
echo "Agent Cards (.well-known/agent.json):"
echo "  http://localhost:8000/.well-known/agent.json"
echo "  http://localhost:8001/.well-known/agent.json"
echo "  http://localhost:8002/.well-known/agent.json"
echo "  http://localhost:8003/.well-known/agent.json"
echo "  http://localhost:8004/.well-known/agent.json"
echo ""
echo "Process IDs:"
echo "  Weather: $WEATHER_PID"
echo "  Stylist: $STYLIST_PID"
echo "  Activity: $ACTIVITY_PID"
echo "  Safety: $SAFETY_PID"
echo "  Coach: $COACH_PID"
echo ""
echo "Logs available in deployment/a2a/logs/"
echo ""
echo "To stop all services, run: ./stop-all.sh"
echo "======================================================================"

# Save PIDs for stopping later
echo "$WEATHER_PID $STYLIST_PID $ACTIVITY_PID $SAFETY_PID $COACH_PID" > .pids
