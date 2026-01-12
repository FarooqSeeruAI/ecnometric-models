#!/bin/bash
# Test caching functionality
# First request should take time, second should be instant

BASE_URL="${1:-http://localhost:8000}"

echo "=========================================="
echo "Testing Caching Functionality"
echo "=========================================="
echo ""

# Test scenario parameters
SCENARIO_NAME="cache_test"
YEAR=2023
STEPS=1
SHOCKS='{"realgdp": 1.0}'

echo "Test Scenario:"
echo "  Name: $SCENARIO_NAME"
echo "  Year: $YEAR"
echo "  Steps: $STEPS"
echo "  Shocks: $SHOCKS"
echo ""

# First request - should take time (no cache)
echo "----------------------------------------"
echo "Request 1: First run (no cache)"
echo "----------------------------------------"
echo "Time: $(date '+%H:%M:%S')"
echo ""

RESPONSE1=$(curl -s -X POST "$BASE_URL/api/v1/scenarios/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"scenario_name\": \"${SCENARIO_NAME}_1\",
    \"year\": $YEAR,
    \"steps\": $STEPS,
    \"shocks\": $SHOCKS
  }")

SCENARIO_ID1=$(echo $RESPONSE1 | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario_id'])" 2>/dev/null)
STATUS1=$(echo $RESPONSE1 | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

echo "Response: $RESPONSE1" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE1"
echo ""
echo "Scenario ID: $SCENARIO_ID1"
echo "Status: $STATUS1"
echo ""

# Wait for first request to complete if it's running
if [ "$STATUS1" = "running" ]; then
    echo "Waiting for first request to complete..."
    START_TIME=$(date +%s)
    
    while true; do
        STATUS_CHECK=$(curl -s "$BASE_URL/api/v1/scenarios/$SCENARIO_ID1/status" | \
          python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
        
        if [ "$STATUS_CHECK" = "completed" ]; then
            ELAPSED=$(($(date +%s) - $START_TIME))
            echo "✓ First request completed in ${ELAPSED} seconds"
            break
        elif [ "$STATUS_CHECK" = "error" ]; then
            echo "✗ First request failed!"
            exit 1
        fi
        
        sleep 2
    done
    echo ""
fi

# Wait a moment
sleep 2

# Second request - should be instant (cached)
echo "----------------------------------------"
echo "Request 2: Second run (should use cache)"
echo "----------------------------------------"
echo "Time: $(date '+%H:%M:%S')"
echo ""

START_TIME2=$(date +%s)

RESPONSE2=$(curl -s -X POST "$BASE_URL/api/v1/scenarios/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"scenario_name\": \"${SCENARIO_NAME}_2\",
    \"year\": $YEAR,
    \"steps\": $STEPS,
    \"shocks\": $SHOCKS
  }")

ELAPSED2=$(($(date +%s) - $START_TIME2))

SCENARIO_ID2=$(echo $RESPONSE2 | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario_id'])" 2>/dev/null)
STATUS2=$(echo $RESPONSE2 | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

echo "Response: $RESPONSE2" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE2"
echo ""
echo "Scenario ID: $SCENARIO_ID2"
echo "Status: $STATUS2"
echo "Response time: ${ELAPSED2} seconds"
echo ""

# Verify results are available
if [ "$STATUS2" = "completed" ]; then
    echo "✓ Second request returned immediately (cached)!"
    echo ""
    echo "Verifying results are available..."
    RESULTS=$(curl -s "$BASE_URL/api/v1/scenarios/$SCENARIO_ID2/results" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print('base' in data.get('results', {}), 'policy' in data.get('results', {}))" 2>/dev/null)
    
    if [ "$RESULTS" = "True True" ]; then
        echo "✓ Results are available (both base and policy)"
    else
        echo "✗ Results may not be available"
    fi
else
    echo "✗ Second request did not return completed status"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
