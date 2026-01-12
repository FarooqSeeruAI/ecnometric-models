#!/bin/bash
# Monitor scenario progress and get results when complete

SCENARIO_ID="${1}"
API_URL="${2:-http://localhost:8000}"

if [ -z "$SCENARIO_ID" ]; then
    echo "Usage: $0 <scenario_id> [api_url]"
    echo ""
    echo "Example:"
    echo "  $0 quick_test_20260112_120433"
    echo "  $0 quick_test_20260112_120433 http://13.203.193.142"
    exit 1
fi

echo "📊 Monitoring Scenario: ${SCENARIO_ID}"
echo "======================================"
echo ""

MAX_WAIT=600  # 10 minutes max
CHECK_INTERVAL=5  # Check every 5 seconds
ELAPSED=0
STATUS="running"
START_TIME=$(date +%s)

while [ "$STATUS" = "running" ] && [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status)
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    MINUTES=$((ELAPSED / 60))
    SECONDS=$((ELAPSED % 60))
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Scenario completed! (took ${MINUTES}m ${SECONDS}s)"
        echo ""
        echo "Status:"
        echo "$STATUS_RESPONSE" | python3 -m json.tool
        break
    elif [ "$STATUS" = "error" ]; then
        echo "❌ Scenario failed!"
        echo ""
        echo "Error details:"
        echo "$STATUS_RESPONSE" | python3 -m json.tool
        exit 1
    else
        # Show progress
        printf "\r⏳ Status: ${STATUS} | Elapsed: ${MINUTES}m ${SECONDS}s | Waiting..."
        sleep $CHECK_INTERVAL
    fi
done

if [ "$STATUS" = "running" ]; then
    echo ""
    echo "⚠️  Timeout: Scenario still running after ${MAX_WAIT}s"
    echo "   Check manually: curl ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status"
    exit 1
fi

# Get results
echo ""
echo "📥 Fetching results..."
echo ""

RESULTS=$(curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/results)

if echo "$RESULTS" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✅ Results retrieved!"
    echo ""
    echo "Summary:"
    echo "$RESULTS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"  Base records: {len(data.get('results', {}).get('base', []))}\"); print(f\"  Policy records: {len(data.get('results', {}).get('policy', []))}\")"
    echo ""
    echo "Save to file:"
    echo "  curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/results | python3 -m json.tool > results.json"
else
    echo "❌ Failed to get results"
    echo "$RESULTS"
fi
