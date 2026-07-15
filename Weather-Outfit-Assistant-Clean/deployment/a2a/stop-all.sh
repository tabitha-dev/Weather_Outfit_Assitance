#!/bin/bash
# Stop all A2A services

echo "Stopping all Weather Outfit ADK A2A services..."

if [ -f ".pids" ]; then
    PIDS=$(cat .pids)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping process $PID..."
            kill $PID
        fi
    done
    rm .pids
    echo "✅ All services stopped"
else
    echo "No .pids file found. Killing by port..."
    lsof -ti:8000,8001,8002,8003,8004 | xargs kill -9 2>/dev/null || true
    echo "✅ Services stopped"
fi
