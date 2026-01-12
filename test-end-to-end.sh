#!/bin/bash
# End-to-End Test for CGE Model API
# Tests all major functionality: health, scenario submission, status, results, caching

set -e

API_URL="${1:-http://3.110.189.51:8000}"

echo "🧪 End-to-End Test for CGE Model API"
echo "======================================"
echo "API URL: ${API_URL}"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected_status=${5:-200}
    
    echo -n "Testing ${name}... "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X ${method} "${url}" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X ${method} "${url}" \
            -H "Content-Type: application/json" \
            -d "${data}" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code, expected $expected_status)"
        echo "Response: $body"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Health endpoint" "GET" "${API_URL}/health"
HEALTH_RESPONSE=$(curl -s "${API_URL}/health")
echo "Response: $HEALTH_RESPONSE"
echo ""

# Test 2: API Info
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  API Info"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "OpenAPI spec" "GET" "${API_URL}/openapi.json"
echo ""

# Test 3: Variables Endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Variables Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Get variables" "GET" "${API_URL}/api/v1/variables"
VARS_COUNT=$(curl -s "${API_URL}/api/v1/variables" | grep -o '"name"' | wc -l | tr -d ' ')
echo "Found $VARS_COUNT variables"
echo ""

# Test 4: Sectors Endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Sectors Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Get sectors" "GET" "${API_URL}/api/v1/sectors"
echo ""

# Test 5: Submit Scenario (First Run - Should Execute)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Submit Scenario (First Run - Should Execute)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SCENARIO_PAYLOAD='{
  "scenario_name": "e2e_test",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "realgdp": 1.0
  },
  "reporting_vars": ["realgdp", "employi"]
}'

echo "Submitting scenario..."
SUBMIT_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/scenarios/run" \
    -H "Content-Type: application/json" \
    -d "${SCENARIO_PAYLOAD}")

SCENARIO_ID=$(echo "$SUBMIT_RESPONSE" | grep -o '"scenario_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SCENARIO_ID" ]; then
    echo -e "${RED}✗ FAILED${NC} - Could not extract scenario_id"
    echo "Response: $SUBMIT_RESPONSE"
    ((TESTS_FAILED++))
    exit 1
else
    echo -e "${GREEN}✓ PASSED${NC} - Scenario submitted"
    echo "Scenario ID: $SCENARIO_ID"
    ((TESTS_PASSED++))
fi

echo "Full response: $SUBMIT_RESPONSE"
echo ""

# Test 6: Check Status (Initial)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Check Scenario Status (Initial)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
STATUS_URL="${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status"
echo "Checking status at: $STATUS_URL"

MAX_WAIT=300  # 5 minutes
WAIT_TIME=0
STATUS="running"

while [ "$STATUS" = "running" ] && [ $WAIT_TIME -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s "${STATUS_URL}")
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    CACHED=$(echo "$STATUS_RESPONSE" | grep -o '"cached":[^,}]*' | cut -d':' -f2 | tr -d ' ')
    
    if [ -z "$STATUS" ]; then
        STATUS="unknown"
    fi
    
    echo "  Status: $STATUS (waited ${WAIT_TIME}s)"
    
    if [ "$STATUS" = "completed" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Scenario completed"
        if [ "$CACHED" = "true" ]; then
            echo "  (Cached: true)"
        else
            echo "  (Cached: false - executed model)"
        fi
        ((TESTS_PASSED++))
        break
    elif [ "$STATUS" = "failed" ]; then
        echo -e "${RED}✗ FAILED${NC} - Scenario failed"
        echo "Response: $STATUS_RESPONSE"
        ((TESTS_FAILED++))
        exit 1
    fi
    
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
done

if [ "$STATUS" = "running" ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} - Scenario still running after ${MAX_WAIT}s"
    ((TESTS_FAILED++))
fi

echo ""

# Test 7: Get Results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Get Scenario Results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESULTS_URL="${API_URL}/api/v1/scenarios/${SCENARIO_ID}/results"
echo "Getting results from: $RESULTS_URL"

RESULTS_RESPONSE=$(curl -s "${RESULTS_URL}")
RESULTS_SIZE=$(echo "$RESULTS_RESPONSE" | wc -c)

if [ $RESULTS_SIZE -gt 100 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Results retrieved (${RESULTS_SIZE} bytes)"
    echo "Sample response (first 200 chars): ${RESULTS_RESPONSE:0:200}..."
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Results too small or empty"
    echo "Response: $RESULTS_RESPONSE"
    ((TESTS_FAILED++))
fi

echo ""

# Test 8: Submit Same Scenario Again (Should Use Cache)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  Submit Same Scenario (Should Use Cache)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Submitting identical scenario (should return cached result immediately)..."

CACHE_START_TIME=$(date +%s)
CACHE_SUBMIT_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/scenarios/run" \
    -H "Content-Type: application/json" \
    -d "${SCENARIO_PAYLOAD}")
CACHE_END_TIME=$(date +%s)
CACHE_DURATION=$((CACHE_END_TIME - CACHE_START_TIME))

CACHE_SCENARIO_ID=$(echo "$CACHE_SUBMIT_RESPONSE" | grep -o '"scenario_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CACHE_SCENARIO_ID" ]; then
    echo -e "${RED}✗ FAILED${NC} - Could not extract scenario_id from cache test"
    ((TESTS_FAILED++))
else
    echo "Cache test Scenario ID: $CACHE_SCENARIO_ID"
    echo "Response time: ${CACHE_DURATION}s"
    
    # Check if it's cached
    sleep 2
    CACHE_STATUS_RESPONSE=$(curl -s "${API_URL}/api/v1/scenarios/${CACHE_SCENARIO_ID}/status")
    CACHE_STATUS=$(echo "$CACHE_STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    CACHE_CACHED=$(echo "$CACHE_STATUS_RESPONSE" | grep -o '"cached":[^,}]*' | cut -d':' -f2 | tr -d ' ')
    
    if [ "$CACHE_STATUS" = "completed" ] && [ "$CACHE_CACHED" = "true" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Cache working (returned immediately, cached=true)"
        ((TESTS_PASSED++))
    elif [ "$CACHE_STATUS" = "completed" ]; then
        echo -e "${YELLOW}⚠ WARNING${NC} - Completed but not marked as cached"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Cache not working (status: $CACHE_STATUS)"
        echo "Response: $CACHE_STATUS_RESPONSE"
        ((TESTS_FAILED++))
    fi
fi

echo ""

# Test 9: Chat Endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  Chat Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CHAT_PAYLOAD='{"question": "What is the CGE model?"}'
test_endpoint "Chat endpoint" "POST" "${API_URL}/api/v1/chat" "${CHAT_PAYLOAD}"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
else
    echo -e "${GREEN}Failed: $TESTS_FAILED${NC}"
fi

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
