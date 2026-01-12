#!/bin/bash
# End-to-end test: Submit scenario, check status, get results

API_URL="http://localhost:8000"
SCENARIO_NAME="quick_test"
YEAR=2023
STEPS=1

echo "🧪 End-to-End Scenario Test"
echo "==========================="
echo ""

# Step 1: Submit scenario
echo "1️⃣ Submitting scenario..."
echo "   Scenario: ${SCENARIO_NAME}"
echo "   Year: ${YEAR}"
echo "   Steps: ${STEPS}"
echo "   Shocks: realgdp = 1.0"
echo ""

RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d "{
    \"scenario_name\": \"${SCENARIO_NAME}\",
    \"year\": ${YEAR},
    \"steps\": ${STEPS},
    \"shocks\": {
      \"realgdp\": 1.0
    }
  }")

SCENARIO_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('scenario_id', ''))" 2>/dev/null)

if [ -z "$SCENARIO_ID" ]; then
    echo "❌ Failed to submit scenario"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Scenario submitted successfully!"
echo "   Scenario ID: ${SCENARIO_ID}"
echo ""
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Step 2: Monitor status
echo "2️⃣ Monitoring scenario status..."
echo ""

MAX_WAIT=300  # 5 minutes max
CHECK_INTERVAL=5  # Check every 5 seconds
ELAPSED=0
STATUS="running"

while [ "$STATUS" = "running" ] && [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status)
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Scenario completed!"
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
        echo "   Status: ${STATUS} (elapsed: ${ELAPSED}s)"
        sleep $CHECK_INTERVAL
        ELAPSED=$((ELAPSED + CHECK_INTERVAL))
    fi
done

if [ "$STATUS" = "running" ]; then
    echo "⚠️  Timeout: Scenario still running after ${MAX_WAIT}s"
    echo "   Check status manually: curl ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status"
    exit 1
fi

# Step 3: Get results
echo ""
echo "3️⃣ Retrieving scenario results..."
echo ""

RESULTS_RESPONSE=$(curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/results)

if echo "$RESULTS_RESPONSE" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✅ Results retrieved successfully!"
    echo ""
    echo "Results:"
    echo "$RESULTS_RESPONSE" | python3 -m json.tool
else
    echo "⚠️  Could not parse results as JSON"
    echo "Response:"
    echo "$RESULTS_RESPONSE"
fi

# Step 4: Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo "✅ Scenario submitted: ${SCENARIO_ID}"
echo "✅ Status: ${STATUS}"
echo "✅ Results retrieved"
echo ""
echo "🔗 Useful endpoints:"
echo "   Status: ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status"
echo "   Results: ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/results"
