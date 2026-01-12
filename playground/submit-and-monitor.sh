#!/bin/bash
# Submit a scenario and monitor it until completion

API_URL="${1:-http://localhost:8000}"

echo "🚀 Submit and Monitor Scenario"
echo "==============================="
echo ""

# Submit scenario
echo "1️⃣ Submitting scenario..."
RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "quick_test",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "realgdp": 1.0
    }
  }')

SCENARIO_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('scenario_id', ''))" 2>/dev/null)

if [ -z "$SCENARIO_ID" ]; then
    echo "❌ Failed to submit scenario"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Scenario submitted!"
echo "   Scenario ID: ${SCENARIO_ID}"
echo ""
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Monitor and get results
echo "2️⃣ Monitoring progress..."
echo ""

./monitor-scenario.sh ${SCENARIO_ID} ${API_URL}
