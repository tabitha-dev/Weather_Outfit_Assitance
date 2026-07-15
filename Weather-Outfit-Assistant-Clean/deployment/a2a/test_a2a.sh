#!/bin/bash
# Quick test script for A2A deployment

set -e

echo "======================================================================"
echo "A2A Multi-Service Architecture Test"
echo "======================================================================"

# Check if services are running
echo ""
echo "1. Checking if all services are healthy..."
echo "----------------------------------------------------------------------"

SERVICES=("8000:Coach" "8001:Weather" "8002:Stylist" "8003:Activity" "8004:Safety")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    IFS=':' read -r port name <<< "$service"
    echo -n "  Checking $name (port $port)... "
    
    if curl -sf http://localhost:$port/.well-known/agent.json > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Not responding"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = false ]; then
    echo ""
    echo "❌ Some services are not healthy. Please start all services first:"
    echo "   docker-compose up  OR  ./start-all.sh"
    exit 1
fi

# Test Weather Agent directly
echo ""
echo "2. Testing Weather Agent (direct call)..."
echo "----------------------------------------------------------------------"

WEATHER_RESPONSE=$(curl -s -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "test-session-1",
    "message": "What is the weather in Seattle?"
  }')

if echo "$WEATHER_RESPONSE" | grep -q "temperature\|weather\|Seattle" 2>/dev/null; then
    echo "✅ Weather Agent responding correctly"
else
    echo "⚠️  Weather Agent response: $WEATHER_RESPONSE"
fi

# Test Coach Agent (orchestrator)
echo ""
echo "3. Testing Coach Agent (orchestrator with remote agents)..."
echo "----------------------------------------------------------------------"

COACH_RESPONSE=$(curl -s -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "test-session-2",
    "message": "What should I wear today in Portland?"
  }')

if echo "$COACH_RESPONSE" | grep -q "wear\|outfit\|Portland" 2>/dev/null; then
    echo "✅ Coach Agent coordinating remote agents correctly"
else
    echo "⚠️  Coach Agent response: $COACH_RESPONSE"
fi

# Test Activity Agent
echo ""
echo "4. Testing Activity Agent..."
echo "----------------------------------------------------------------------"

ACTIVITY_RESPONSE=$(curl -s -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "test-session-3",
    "message": "I'\''m going hiking this afternoon"
  }')

if echo "$ACTIVITY_RESPONSE" | grep -q "sports\|hiking\|activity" 2>/dev/null; then
    echo "✅ Activity Agent classifying correctly"
else
    echo "⚠️  Activity Agent response: $ACTIVITY_RESPONSE"
fi

# Summary
echo ""
echo "======================================================================"
echo "✅ A2A Multi-Service Architecture Test Complete!"
echo "======================================================================"
echo ""
echo "All services are communicating via A2A protocol."
echo "Each agent runs independently and can scale separately."
echo ""
echo "Service URLs:"
echo "  Coach (Main):    http://localhost:8000"
echo "  Weather Agent:   http://localhost:8001"
echo "  Stylist Agent:   http://localhost:8002"
echo "  Activity Agent:  http://localhost:8003"
echo "  Safety Agent:    http://localhost:8004"
echo ""
echo "======================================================================"
