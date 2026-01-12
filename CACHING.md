# Result Caching for Demo Performance

## Overview

The API now includes **automatic result caching** to make demos run instantly. If a scenario with identical parameters has been run before, cached results are returned immediately without re-running the model.

## How It Works

### Cache Key Generation

The cache key is generated from:
- **year**: Starting year (e.g., 2023)
- **steps**: Number of years to simulate (e.g., 1)
- **shocks**: Dictionary of variable shocks (sorted for consistency)
- **reporting_vars**: Optional list of reporting variables

The cache key is a **MD5 hash** of these parameters, ensuring:
- Identical parameters → Same cache key
- Different parameters → Different cache keys
- Consistent hashing regardless of parameter order

### Cache Storage

- **Location**: `cache/{cache_key}/`
- **Files**: `base.xlsx`, `policy.xlsx`, `summary.xlsx`
- **Persistence**: Cached results persist across server restarts

### Execution Flow

```
1. Request received with parameters
   ↓
2. Generate cache key from parameters
   ↓
3. Check if cache exists
   ├─ YES → Load from cache → Return immediately (instant!)
   └─ NO  → Run model → Save to cache → Return results
```

## Example: First Run vs Cached Run

### First Run (No Cache)

```bash
# First request - runs model (~30-60 seconds)
curl -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "demo",
    "year": 2023,
    "steps": 1,
    "shocks": {"realgdp": 1.0}
  }'

# Response: {"status": "running", ...}
# Wait 30-60 seconds, then check status
# Response: {"status": "completed", ...}
```

### Cached Run (Instant!)

```bash
# Second request with SAME parameters - instant response!
curl -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "demo2",
    "year": 2023,
    "steps": 1,
    "shocks": {"realgdp": 1.0}
  }'

# Response: {"status": "completed", ...}  ← INSTANT!
# Results are immediately available
```

## Cache Matching Rules

### ✅ Same Cache Key (Cached)

These requests will use the same cache:

```json
// Request 1
{
  "year": 2023,
  "steps": 1,
  "shocks": {"realgdp": 1.0}
}

// Request 2 (same parameters, different scenario_name)
{
  "year": 2023,
  "steps": 1,
  "shocks": {"realgdp": 1.0}
}
```

### ❌ Different Cache Key (New Run)

These requests will run separately:

```json
// Request 1
{
  "year": 2023,
  "steps": 1,
  "shocks": {"realgdp": 1.0}
}

// Request 2 (different shock value)
{
  "year": 2023,
  "steps": 1,
  "shocks": {"realgdp": 2.0}  ← Different!
}

// Request 3 (different steps)
{
  "year": 2023,
  "steps": 3,  ← Different!
  "shocks": {"realgdp": 1.0}
}
```

## Demo Strategy

### For Quick Demos

1. **Pre-run common scenarios** before the demo:
   ```bash
   # Run these once to populate cache
   # Single shock, 1 year
   {"year": 2023, "steps": 1, "shocks": {"realgdp": 1.0}}
   {"year": 2023, "steps": 1, "shocks": {"x1labiEmplWgt_EMIRATI": 15.0}}
   
   # Multi-shock, 1 year
   {"year": 2023, "steps": 1, "shocks": {
     "x1labiEmplWgt_EMIRATI": 15.0,
     "x1labiEmplWgt_MIGRANTHH": -10.0,
     "realgdp": 5.0
   }}
   ```

2. **During demo**: All requests with these parameters return instantly!

### Cache Management

- **View cache**: `ls -la cache/`
- **Clear cache**: `rm -rf cache/*` (if needed)
- **Cache size**: Each cached scenario is ~1-5 MB

## API Response

### Cached Scenario Response

When a cached result is used, the response includes:
- `status: "completed"` (immediately)
- `completed_at`: Timestamp
- Results are immediately available via `/results` endpoint

### New Scenario Response

When cache doesn't exist:
- `status: "running"` (initially)
- Model runs in background
- Results saved to cache for future use

## Benefits

1. **⚡ Instant demos** - Pre-run scenarios return immediately
2. **💰 Cost savings** - No redundant model executions
3. **🔄 Consistent results** - Same parameters = same results
4. **📊 Faster iteration** - Test different scenarios quickly

## Technical Details

- **Cache key algorithm**: MD5 hash of JSON-serialized parameters
- **Cache location**: `{MODEL_DIR}/cache/{cache_key}/`
- **File format**: Excel files (base.xlsx, policy.xlsx, summary.xlsx)
- **Thread safety**: Cache operations are thread-safe

## Notes

- Cache persists across server restarts
- Cache is shared across all users/scenarios with same parameters
- `scenario_name` does NOT affect cache key (only parameters matter)
- Cache is automatically created on first successful run
