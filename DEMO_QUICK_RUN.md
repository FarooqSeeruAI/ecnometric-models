# Quick Demo Run Guide

## Understanding Model Execution Time

The model execution time depends on:

1. **Steps** (years to simulate) - **BIGGEST IMPACT**
   - Default: 18 steps = 18 years (2023-2040)
   - Each step = 1 year simulation
   - Each step runs both base AND policy simulations
   - Formula: `Time ≈ steps × 2 × (base_time + policy_time)`
   - **For single shock demo: Use `steps: 1`** = 1 year only (fastest)

2. **Substeps** (iterations per step)
   - Default: 1 substep
   - More substeps = more iterations = slower
   - **For demo: Keep `substeps: 1`** (already optimal)

3. **doiterative** (solver type)
   - Default: FALSE (direct solver - faster)
   - TRUE = iterative solver (slower but more accurate for large systems)
   - **For demo: Keep `doiterative: FALSE`** (already optimal)

4. **Model Size** (fixed)
   - ~33,677 equations
   - ~4,089 solution variables
   - This is fixed and cannot be reduced

## Quick Demo Request

### Fastest Demo (1 step, ~30-60 seconds)

```bash
curl -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "demo_quick",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "realgdp": 1.0
    }
  }'
```

**Expected time: 30-60 seconds** (vs 3-4 minutes for 18 steps)

### Why This is Faster

- **`steps: 1`** = Simulate only **1 year** (2023) instead of 18 years (2023-2040)
- Perfect for single shock analysis - see immediate impact
- Still runs both base and policy simulations (required for comparison)
- Same model complexity, just 1 iteration instead of 18
- **18x faster** than full projection

## How the Model Works

### Execution Flow

```
1. Submit Request → Returns immediately with scenario_id
   ↓
2. Background Processing:
   ├─ Read model file (orani.model)
   ├─ Read data (database/oranignm.xlsx)
   ├─ For each simulation type ['base', 'policy']:
   │   └─ For each step (0 to steps-1):
   │       └─ For each substep (0 to substeps-1):
   │           ├─ Evaluate formulae
   │           ├─ Build matrix system (33,677 equations)
   │           ├─ Solve: Ax = b
   │           └─ Update variables
   └─ Write outputs (base.xlsx, policy.xlsx, summary.xlsx)
   ↓
3. Status: completed
   ↓
4. Fetch Results (~1 second to read files)
```

### Time Breakdown (for 1 step)

- Model initialization: ~5 seconds
- Base simulation (1 step): ~15-20 seconds
- Policy simulation (1 step): ~15-20 seconds
- File writing: ~5 seconds
- **Total: ~30-60 seconds**

### Time Breakdown (for 18 steps - default)

- Model initialization: ~5 seconds
- Base simulation (18 steps): ~2-3 minutes
- Policy simulation (18 steps): ~2-3 minutes
- File writing: ~5 seconds
- **Total: ~4-6 minutes**

## API Parameters Explained

### Request Parameters

```json
{
  "scenario_name": "demo_quick",     // Unique name
  "year": 2023,                      // Starting year (affects which closure files used)
  "steps": 1,                        // ⚡ KEY: Number of years to simulate
                                     //   1 = 1 year (2023 only) - FASTEST for single shock
                                     //   18 = 18 years (2023-2040) - Full projection
  "shocks": {                        // Economic shocks to apply
    "realgdp": 1.0                   // Example: 1% shock to real GDP
  },
  "reporting_vars": null            // Optional: Specific variables to include in output
}
```

### What Gets Overridden

When you submit a request:
- `steps` from request → Overrides `default.yml` steps
- `substeps` → Uses from `default.yml` (currently 1 - optimal)
- `doiterative` → Uses from `default.yml` (currently FALSE - optimal)

## Demo Workflow

### Step 1: Submit (Fast - 0.06s)

```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "demo_quick",
    "year": 2023,
    "steps": 1,
    "shocks": {"realgdp": 1.0}
  }')

SCENARIO_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario_id'])")
echo "Scenario ID: $SCENARIO_ID"
```

### Step 2: Monitor (Wait 30-60 seconds)

```bash
# Check status every 5 seconds
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/status | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
  
  if [ "$STATUS" = "completed" ]; then
    echo "✅ Completed!"
    break
  elif [ "$STATUS" = "error" ]; then
    echo "❌ Error!"
    break
  else
    echo "⏳ Status: $STATUS"
    sleep 5
  fi
done
```

### Step 3: Get Results (~1 second)

```bash
curl -s http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/results | \
  python3 -m json.tool > results.json
```

## Performance Comparison

| Steps | Years Simulated | Expected Time | Use Case |
|-------|-----------------|--------------|----------|
| 1     | 1 year (2023)   | 30-60 sec     | **Single shock demo** ⚡ |
| 3     | 3 years (2023-2025) | 1-2 min       | Short-term projection |
| 5     | 5 years (2023-2027) | 2-3 min       | Medium-term projection |
| 18    | 18 years (2023-2040) | 4-6 min       | Full long-term projection (default) |

## Tips for Faster Demo

1. ✅ **Use `steps: 1`** - Biggest time saver
2. ✅ **Keep `substeps: 1`** - Already optimal
3. ✅ **Keep `doiterative: FALSE`** - Already optimal
4. ✅ **Use simple shocks** - Complex shocks don't affect time much
5. ⚠️ **Variables don't affect computation time** - Only affects output size

## Example: Complete Demo Flow

```bash
# 1. Submit (instant)
SCENARIO_ID=$(curl -s -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{"scenario_name":"demo","year":2023,"steps":1,"shocks":{"realgdp":1.0}}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['scenario_id'])")

echo "Submitted: $SCENARIO_ID"

# 2. Wait for completion (30-60 seconds)
./monitor-scenario.sh $SCENARIO_ID

# 3. Get results
curl -s http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/results | \
  python3 -m json.tool > demo_results.json
```

## Summary

**For fastest demo:**
- ✅ `steps: 1` → **30-60 seconds** total
- ✅ All other settings already optimal
- ✅ Request returns immediately (async)
- ✅ Results fetch takes ~1 second

**The key is `steps: 1` - this reduces execution time by ~18x!**
