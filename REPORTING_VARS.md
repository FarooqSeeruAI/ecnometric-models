# Reporting Variables (`reporting_vars`)

## What Are Reporting Variables?

`reporting_vars` is an **optional filter** that limits which variables are included in the output Excel files (`base.xlsx` and `policy.xlsx`).

## How It Works

### Without `reporting_vars` (Default)
- **All variables** are included in the output
- Output files contain **thousands of variables** (e.g., 4,089+ records)
- Full model results for all sectors, industries, and variables

### With `reporting_vars` (Filtered)
- **Only specified variables** are included in the output
- Output files contain **only the variables you care about**
- Reduces file size and makes results easier to analyze

## Example

### Request Without `reporting_vars`:
```json
{
  "scenario_name": "full_output",
  "year": 2023,
  "steps": 1,
  "shocks": {"realgdp": 5.0}
}
```
**Result:** ~4,089 variables in output

### Request With `reporting_vars`:
```json
{
  "scenario_name": "focused_output",
  "year": 2023,
  "steps": 1,
  "shocks": {"realgdp": 5.0},
  "reporting_vars": ["realgdp", "employi", "INCGDP"]
}
```
**Result:** Only `realgdp`, `employi`, and `INCGDP` (and related variables) in output

## Your Example

```json
{
  "scenario_name": "emiratization_gdp_growth",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 15.0,
    "realgdp": 5.0
  },
  "reporting_vars": [
    "realgdp",
    "employi",
    "x1labioEmplWgt",
    "INCGDP"
  ]
}
```

This will:
1. **Run the model** with both shocks (Emirati employment +15%, GDP +5%)
2. **Filter output** to only include:
   - `realgdp` - Real GDP
   - `employi` - Employment by industry
   - `x1labioEmplWgt` - Employment weights
   - `INCGDP` - GDP income

## Important Notes

1. **Variable Matching**: The model includes variables that **match or contain** the reporting variable names
   - Example: `"employi"` will include `employi_AG`, `employi_MIN`, etc. (all industries)

2. **Related Variables**: Some variables automatically include related ones
   - Example: `x1labioEmplWgt` may include sector-specific variants

3. **Cache Key**: `reporting_vars` is part of the cache key
   - Same parameters + same `reporting_vars` = same cache
   - Different `reporting_vars` = different cache (even with same shocks)

4. **Variable Names**: Must match exactly as defined in the model
   - Check available variables: `GET /api/v1/variables`
   - See `default.yml` for full list

## Common Reporting Variables

### Economic Indicators
- `realgdp` - Real GDP
- `INCGDP` - GDP income
- `p0gdpexp` - GDP deflator
- `V0GDPINC` - GDP income value

### Employment
- `employi` - Employment by industry
- `x1labioEmplWgt` - Employment weights
- `x1labiEmplWgt_EMIRATI` - Emirati employment weight
- `x1labiEmplWgt_MIGRANTHH` - Migrant employment weight

### Prices
- `p3tot` - Consumer price index
- `p1labi` - Labor price by industry

## Benefits

1. **Faster Results** - Smaller output files load faster
2. **Focused Analysis** - Only see what you need
3. **Reduced Bandwidth** - Smaller JSON responses
4. **Easier Comparison** - Compare specific variables across scenarios

## When to Use

✅ **Use `reporting_vars` when:**
- You only care about specific variables
- You want faster response times
- You're doing focused analysis
- You want smaller output files

❌ **Don't use `reporting_vars` when:**
- You need all model results
- You're doing comprehensive analysis
- You want to explore all variables

## Default Behavior

If `reporting_vars` is **not specified**:
- Uses the default list from `default.yml` (if defined)
- Or includes **all variables** if no default is set
