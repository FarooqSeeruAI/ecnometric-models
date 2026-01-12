#!/bin/bash
# Check scenario status, results, and cache

BASE_URL="${1:-http://localhost:8000}"
SCENARIO_ID="${2}"

if [ -z "$SCENARIO_ID" ]; then
    echo "Usage: $0 [base_url] <scenario_id>"
    echo ""
    echo "Listing recent scenarios..."
    curl -s "$BASE_URL/api/v1/scenarios" | python3 -m json.tool
    echo ""
    echo "Please provide scenario_id as second argument"
    exit 1
fi

echo "=========================================="
echo "Checking Scenario: $SCENARIO_ID"
echo "=========================================="
echo ""

# 1. Check Status
echo "1. Status Check:"
echo "----------------------------------------"
STATUS_RESPONSE=$(curl -s "$BASE_URL/api/v1/scenarios/$SCENARIO_ID/status")
echo "$STATUS_RESPONSE" | python3 -m json.tool
echo ""

STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
CACHED=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('cached', False))" 2>/dev/null)

# 2. Check Results (if completed)
if [ "$STATUS" = "completed" ]; then
    echo "2. Results Check:"
    echo "----------------------------------------"
    RESULTS_RESPONSE=$(curl -s "$BASE_URL/api/v1/scenarios/$SCENARIO_ID/results")
    
    # Check if results have data
    HAS_BASE=$(echo "$RESULTS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('base' in data.get('results', {}))" 2>/dev/null)
    HAS_POLICY=$(echo "$RESULTS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('policy' in data.get('results', {}))" 2>/dev/null)
    
    if [ "$HAS_BASE" = "True" ] && [ "$HAS_POLICY" = "True" ]; then
        BASE_COUNT=$(echo "$RESULTS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('results', {}).get('base', [])))" 2>/dev/null)
        POLICY_COUNT=$(echo "$RESULTS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('results', {}).get('policy', [])))" 2>/dev/null)
        echo "✓ Results available:"
        echo "  - Base records: $BASE_COUNT"
        echo "  - Policy records: $POLICY_COUNT"
        echo ""
        echo "Sample results (first 3 base records):"
        echo "$RESULTS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
base = data.get('results', {}).get('base', [])
for i, record in enumerate(base[:3]):
    print(f\"  {i+1}. {record.get('SVAR', 'N/A')}: {list(record.keys())[:5]}\")
" 2>/dev/null
    else
        echo "✗ Results not available or incomplete"
        echo "$RESULTS_RESPONSE" | python3 -m json.tool
    fi
    echo ""
elif [ "$STATUS" = "running" ]; then
    echo "2. Results: Not available yet (still running)"
    echo ""
elif [ "$STATUS" = "error" ]; then
    ERROR=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null)
    echo "2. Error: $ERROR"
    echo ""
fi

# 3. Check Cache
echo "3. Cache Check:"
echo "----------------------------------------"
if [ "$CACHED" = "True" ]; then
    echo "✓ This scenario was loaded from cache"
    CACHE_KEY=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('cache_key', 'N/A'))" 2>/dev/null)
    echo "  Cache key: $CACHE_KEY"
else
    echo "This scenario was NOT from cache (new run)"
    
    # Check if cache directory exists and has files
    if [ -d "cache" ]; then
        CACHE_COUNT=$(find cache -name "base.xlsx" -o -name "policy.xlsx" | wc -l | tr -d ' ')
        echo "  Cache directory exists with $CACHE_COUNT cached scenarios"
        
        # Try to find cache key from scenario
        CACHE_KEY=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('cache_key', ''))" 2>/dev/null)
        if [ -n "$CACHE_KEY" ] && [ "$CACHE_KEY" != "None" ]; then
            CACHE_DIR="cache/$CACHE_KEY"
            if [ -d "$CACHE_DIR" ]; then
                echo "  ✓ Cache saved to: $CACHE_DIR"
                ls -lh "$CACHE_DIR" 2>/dev/null | tail -n +2
            else
                echo "  Cache directory not found: $CACHE_DIR"
            fi
        fi
    else
        echo "  Cache directory does not exist yet"
    fi
fi
echo ""

echo "=========================================="
echo "Check Complete"
echo "=========================================="
