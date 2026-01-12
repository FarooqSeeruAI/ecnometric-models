# Multi-Shock Scenario Example

## Scenario Request

**Goal:** Run a scenario with:
- 15% Emirati employment increase
- 10% migrant decrease  
- 5% GDP growth
- Over 3 years

## How It Works

### Variable Names

- **Emirati employment**: `x1labiEmplWgt_EMIRATI`
- **Migrant employment**: `x1labiEmplWgt_MIGRANTHH`
- **GDP growth**: `realgdp`

### Request Structure

```bash
curl -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "emiratization_policy",
    "year": 2023,
    "steps": 3,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "x1labiEmplWgt_MIGRANTHH": -10.0,
      "realgdp": 5.0
    }
  }'
```

### How Steps=3 Works

When you set `steps: 3`, the model simulates **3 years**:

1. **Year 1 (2023)**: Applies all shocks
2. **Year 2 (2024)**: Continues from Year 1 results, applies shocks again
3. **Year 3 (2025)**: Continues from Year 2 results, applies shocks again

### Execution Flow

```
For steps=3:
  Step 0: Year 2023
    ├─ Base simulation (with shocks)
    └─ Policy simulation (with shocks)
  
  Step 1: Year 2024
    ├─ Base simulation (with shocks)
    └─ Policy simulation (with shocks)
  
  Step 2: Year 2025
    ├─ Base simulation (with shocks)
    └─ Policy simulation (with shocks)
```

### Shock Values Explained

- `x1labiEmplWgt_EMIRATI: 15.0` = **15% increase** in Emirati employment
- `x1labiEmplWgt_MIGRANTHH: -10.0` = **10% decrease** in migrant employment (negative value)
- `realgdp: 5.0` = **5% growth** in real GDP

**Note:** Values are in **percentage points**, not multipliers:
- `15.0` = 15% increase
- `-10.0` = 10% decrease
- `5.0` = 5% growth

### Expected Execution Time

- **Steps: 3** = 3 years simulation
- **Expected time: 1-2 minutes** (vs 30-60 seconds for 1 step)
- Each additional step adds ~20-30 seconds

### Complete Example

```bash
# 1. Submit scenario
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "emiratization_policy",
    "year": 2023,
    "steps": 3,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "x1labiEmplWgt_MIGRANTHH": -10.0,
      "realgdp": 5.0
    }
  }')

SCENARIO_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['scenario_id'])")
echo "Scenario ID: $SCENARIO_ID"

# 2. Monitor (wait 1-2 minutes)
./monitor-scenario.sh $SCENARIO_ID

# 3. Get results
curl -s http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/results | \
  python3 -m json.tool > results.json
```

### Results Structure

The results will show:
- **Base scenario**: Baseline without shocks
- **Policy scenario**: With all shocks applied
- **For each year (S0, S1, S2)**:
  - S0 = Year 2023 (step 0)
  - S1 = Year 2024 (step 1)
  - S2 = Year 2025 (step 2)

### Understanding the Output

Each variable in results has values for each step:
```json
{
  "SVAR": "x1labiEmplWgt_EMIRATI",
  "S0": 0.0,      // Base year 2023
  "S1": 15.0,     // Year 2024 with shock
  "S2": 30.0      // Year 2025 (cumulative effect)
}
```

## Key Points

1. **`steps: 3`** = Simulate 3 years (2023, 2024, 2025)
2. **Shocks apply to each year** - same values used for all steps
3. **Multiple shocks work together** - all applied simultaneously
4. **Results show progression** - see how effects evolve over 3 years
5. **Execution time scales** - 3 steps ≈ 1-2 minutes

## For AWS Server

Replace `localhost:8000` with `http://13.203.193.142`:

```bash
curl -X POST http://13.203.193.142/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "emiratization_policy",
    "year": 2023,
    "steps": 3,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "x1labiEmplWgt_MIGRANTHH": -10.0,
      "realgdp": 5.0
    }
  }'
```
