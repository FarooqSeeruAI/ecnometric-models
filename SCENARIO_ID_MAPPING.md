# Scenario ID Mapping for Outputs and Cache

## Overview

All outputs and cache are now mapped to **scenario IDs** (UUIDs) for better organization and traceability.

## Directory Structure

### Outputs
- **Location**: `outputs/{scenario_id}/`
- **Files**: `base.xlsx`, `policy.xlsx`, `summary.xlsx`, `cache_link.json`
- **Example**: `outputs/a1b2c3d4-e5f6-7890-abcd-ef1234567890/`

Each scenario gets its own unique output directory based on its UUID, ensuring:
- No conflicts between scenarios with the same name
- Easy lookup by scenario ID
- Clear mapping to cache

### Cache
- **Location**: `cache/{cache_key}/`
- **Files**: `base.xlsx`, `policy.xlsx`, `summary.xlsx`, `scenario_ids.json`
- **Example**: `cache/cc96161fec9d090439ad96d0b68aaad3/`

Cache is organized by **cache_key** (MD5 hash of parameters) for deduplication:
- Same parameters → Same cache key → Shared cache
- Different parameters → Different cache key → Separate cache

## Mapping Files

### 1. `outputs/{scenario_id}/cache_link.json`
Created in each output directory, linking the scenario to its cache:

```json
{
  "cache_key": "cc96161fec9d090439ad96d0b68aaad3",
  "scenario_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Purpose**: 
- Quick lookup: Which cache does this scenario use?
- Reverse mapping: From scenario ID to cache key

### 2. `cache/{cache_key}/scenario_ids.json`
Created in each cache directory, listing all scenario IDs that used this cache:

```json
[
  "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "b2c3d4e5-f6g7-8901-bcde-f23456789012"
]
```

**Purpose**:
- Track which scenarios share the same cached results
- Identify scenarios that can be cleaned up
- Understand cache usage patterns

## Benefits

1. **Unique Outputs**: Each scenario has its own output directory, even if scenarios share the same name
2. **Cache Deduplication**: Multiple scenarios with identical parameters share the same cache
3. **Traceability**: Easy to find which cache a scenario used, and which scenarios used a cache
4. **Cleanup**: Can identify unused caches or scenarios
5. **Consistency**: All paths use scenario_id for reliable lookups

## Example Flow

### Scenario 1 (First Run)
```
1. Request: {"scenario_name": "test", "year": 2023, "steps": 1, "shocks": {"realgdp": 1.0}}
2. Generate scenario_id: "abc-123-def"
3. Generate cache_key: "cc96161fec9d090439ad96d0b68aaad3"
4. Cache doesn't exist → Run model
5. Save outputs to: outputs/abc-123-def/
6. Save to cache: cache/cc96161fec9d090439ad96d0b68aaad3/
7. Create mapping files:
   - outputs/abc-123-def/cache_link.json → {"cache_key": "cc96161...", "scenario_id": "abc-123-def"}
   - cache/cc96161.../scenario_ids.json → ["abc-123-def"]
```

### Scenario 2 (Same Parameters - Uses Cache)
```
1. Request: {"scenario_name": "test2", "year": 2023, "steps": 1, "shocks": {"realgdp": 1.0}}
2. Generate scenario_id: "xyz-789-ghi"
3. Generate cache_key: "cc96161fec9d090439ad96d0b68aaad3" (same as Scenario 1)
4. Cache exists → Load from cache
5. Copy cache to: outputs/xyz-789-ghi/
6. Update mapping files:
   - outputs/xyz-789-ghi/cache_link.json → {"cache_key": "cc96161...", "scenario_id": "xyz-789-ghi"}
   - cache/cc96161.../scenario_ids.json → ["abc-123-def", "xyz-789-ghi"]
```

## API Changes

### Output Directory
- **Before**: `outputs/{scenario_name}/`
- **After**: `outputs/{scenario_id}/`

### Cache Structure
- **Before**: `cache/{cache_key}/` (no scenario mapping)
- **After**: `cache/{cache_key}/` with `scenario_ids.json` mapping file

### Response Fields
All API responses remain the same. The `output_dir` field in responses now contains `outputs/{scenario_id}` instead of `outputs/{scenario_name}`.

## Migration Notes

- Existing scenarios with old structure (`outputs/{scenario_name}/`) will continue to work
- New scenarios will use the new structure (`outputs/{scenario_id}/`)
- Cache structure is backward compatible
- Mapping files are created automatically for new scenarios

## Querying Mappings

### Find cache for a scenario:
```bash
cat outputs/{scenario_id}/cache_link.json
```

### Find all scenarios using a cache:
```bash
cat cache/{cache_key}/scenario_ids.json
```

### Find scenario output directory:
```bash
# From API response
curl http://localhost:8000/api/v1/scenarios/{scenario_id}/status
# Returns: {"output_dir": "outputs/{scenario_id}", ...}
```
