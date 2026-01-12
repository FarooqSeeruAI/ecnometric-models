#!/bin/bash
# Test the async /api/v1/scenarios/run endpoint locally

echo "🧪 Testing Async Endpoint Locally"
echo "=================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server is not running on port 8000"
    echo ""
    echo "Start the server with:"
    echo "  ./start_local.sh"
    echo "  or"
    echo "  python3 api_server.py"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test the endpoint
echo "📤 Testing POST /api/v1/scenarios/run..."
echo ""

START_TIME=$(date +%s)

RESPONSE=$(curl -s -w "\n%{http_code}\n%{time_total}" -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "local_test",
    "year": 2025,
    "steps": 1,
    "shocks": {
      "realgdp": 1.0
    }
  }')

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | tail -2 | head -1)
TIME_TOTAL=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -2)

echo "Response Time: ${TIME_TOTAL}s"
echo "HTTP Status: ${HTTP_CODE}"
echo ""
echo "Response Body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

# Check if it returned quickly (should be < 1 second)
if (( $(echo "$TIME_TOTAL < 1.0" | bc -l) )); then
    echo "✅ SUCCESS: Endpoint returned quickly (${TIME_TOTAL}s)"
    echo ""
    
    # Extract scenario_id
    SCENARIO_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('scenario_id', ''))" 2>/dev/null)
    
    if [ -n "$SCENARIO_ID" ]; then
        echo "📋 Scenario ID: ${SCENARIO_ID}"
        echo ""
        echo "Check status with:"
        echo "  curl http://localhost:8000/api/v1/scenarios/${SCENARIO_ID}/status"
    fi
else
    echo "⚠️  WARNING: Endpoint took ${TIME_TOTAL}s (should be < 1s)"
    echo "   This suggests it's still blocking"
fi

echo ""
echo "📊 Full test details:"
echo "  - Response time: ${TIME_TOTAL}s"
echo "  - HTTP status: ${HTTP_CODE}"
echo "  - Elapsed time: ${ELAPSED}s"
