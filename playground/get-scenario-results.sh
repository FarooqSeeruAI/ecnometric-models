#!/bin/bash
# Get scenario results using curl

SCENARIO_ID="${1:-quick_test_20260112_120433}"
API_URL="${2:-http://localhost:8000}"

if [ -z "$1" ]; then
    echo "Usage: $0 <scenario_id> [api_url]"
    echo ""
    echo "Example:"
    echo "  $0 quick_test_20260112_120433"
    echo "  $0 quick_test_20260112_120433 http://13.203.193.142"
    echo ""
    exit 1
fi

echo "📊 Getting results for scenario: ${SCENARIO_ID}"
echo "=============================================="
echo ""

# Get status first
echo "1️⃣ Status:"
curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/status | python3 -m json.tool
echo ""

# Get results
echo "2️⃣ Results (JSON):"
curl -s ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/results | python3 -m json.tool
echo ""

# Option to download as Excel
echo "3️⃣ Download as Excel:"
echo "curl -O ${API_URL}/api/v1/scenarios/${SCENARIO_ID}/download/excel"
echo ""
