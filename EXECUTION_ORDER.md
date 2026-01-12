# Model Execution Order

## Sequential Execution: Base → Policy

Yes, **base and policy scenarios run sequentially**, not in parallel.

## Execution Flow (for steps=3)

```
1. BASE SIMULATION (Complete First)
   ├─ Step 0 (Year 2023)
   │   └─ Solve base scenario
   ├─ Step 1 (Year 2024)
   │   └─ Solve base scenario (continues from Step 0)
   └─ Step 2 (Year 2025)
       └─ Solve base scenario (continues from Step 1)
   
   ↓ Archive base results
   ↓ Reset model state
   
2. POLICY SIMULATION (Runs After Base)
   ├─ Step 0 (Year 2023)
   │   └─ Solve policy scenario (with shocks)
   ├─ Step 1 (Year 2024)
   │   └─ Solve policy scenario (continues from Step 0)
   └─ Step 2 (Year 2025)
       └─ Solve policy scenario (continues from Step 1)
```

## Code Structure

From `solver.py`:

```python
for simtype in ['base', 'policy']:  # Sequential loop
    for s in range(model.steps):     # For each year
        # Solve step s
    
    if simtype == "base":
        # Archive base results
        model.basedvarvals = copy.deepcopy(model.alldvarvals)
        model.basesvarvals = copy.deepcopy(model.allsvarvals)
        
        # Reset model for policy run
        model.alldvarvals = []
        model.allsvarvals = []
        model.solvarvals = []
        model.datavarvals = []
        model.read_datavars()  # Reload initial data
```

## Why Sequential?

1. **Base provides baseline** - Policy needs baseline values for comparison
2. **Policy uses base results** - Some policy shocks reference base values
3. **Clean separation** - Each simulation starts from initial state
4. **Comparison enabled** - Can compare base vs policy results

## Time Breakdown (for steps=3)

```
Total Time ≈ Base Time + Policy Time

Base Simulation:
  - Step 0: ~15-20 seconds
  - Step 1: ~15-20 seconds  
  - Step 2: ~15-20 seconds
  - Archive/Reset: ~2 seconds
  Base Total: ~47-62 seconds

Policy Simulation:
  - Step 0: ~15-20 seconds
  - Step 1: ~15-20 seconds
  - Step 2: ~15-20 seconds
  Policy Total: ~45-60 seconds

Total: ~1.5-2 minutes
```

## Key Points

1. ✅ **Base runs completely first** - All steps (0 to steps-1)
2. ✅ **Then policy runs** - All steps (0 to steps-1) again
3. ✅ **Model resets between** - Policy starts fresh from initial data
4. ✅ **Results are comparable** - Base and policy use same starting point

## Example: Steps=3 Execution

```
Time 0:00 → Start Base Step 0 (2023)
Time 0:20 → Complete Base Step 0
Time 0:20 → Start Base Step 1 (2024)
Time 0:40 → Complete Base Step 1
Time 0:40 → Start Base Step 2 (2025)
Time 1:00 → Complete Base Step 2
Time 1:00 → Archive base, reset model
Time 1:02 → Start Policy Step 0 (2023) with shocks
Time 1:22 → Complete Policy Step 0
Time 1:22 → Start Policy Step 1 (2024) with shocks
Time 1:42 → Complete Policy Step 1
Time 1:42 → Start Policy Step 2 (2025) with shocks
Time 2:02 → Complete Policy Step 2
Time 2:02 → Write outputs (base.xlsx, policy.xlsx)
Time 2:05 → Done!
```

## Why Not Parallel?

The model architecture requires:
- Base results to be archived before policy runs
- Policy to reference base values for some calculations
- Clean state reset between simulations
- Sequential comparison of results

This is standard CGE model practice - baseline first, then policy scenario.
