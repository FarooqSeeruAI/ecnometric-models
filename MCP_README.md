# CGE Model MCP Server

Model Context Protocol (MCP) server for the CGE economic model, enabling agentic workflows for MoHRE UAE scenario analysis.

## Installation

1. Install dependencies:
```bash
pip install -r requirements_mcp.txt
```

2. Make the server executable:
```bash
chmod +x mcp_server.py
```

## Configuration

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

**For Claude Desktop**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**For Cursor**: Edit your MCP settings

```json
{
  "mcpServers": {
    "cge-model": {
      "command": "python3",
      "args": [
        "/Users/fseeru001/Documents/ClientEngagements/PoC/MoHRE/cge_model/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/fseeru001/Documents/ClientEngagements/PoC/MoHRE/cge_model"
      }
    }
  }
}
```

## Available Tools

### 1. `run_scenario`
Run a CGE model scenario with specified shocks.

**Parameters:**
- `scenario_name` (required): Unique name for the scenario
- `year` (optional): Starting year (default: 2023)
- `steps` (optional): Number of years to simulate (default: 1)
- `shocks` (required): Dictionary of variable shocks
  ```json
  {
    "x1labiEmplWgt_EMIRATI": 10.0,
    "realgdp": 5.0,
    "aprimRatio_AG": 15.0
  }
  ```
- `reporting_vars` (optional): List of variables to include in output
- `output_dir` (optional): Directory for output files

**Returns:** Scenario ID for tracking

### 2. `get_scenario_status`
Get the status of a running or completed scenario.

**Parameters:**
- `scenario_id` (required): Scenario ID from `run_scenario`

**Returns:** Status information (running, completed, error)

### 3. `get_scenario_results`
Get results from a completed scenario.

**Parameters:**
- `scenario_id` (required): Scenario ID
- `variables` (optional): Specific variables to retrieve
- `format` (optional): "json" or "excel" (default: "json")

**Returns:** Scenario results in requested format

### 4. `list_available_variables`
List all available variables for shocks or reporting.

**Parameters:**
- `category` (optional): Filter by category ("employment", "economic", "productivity", "tax", "all")

**Returns:** List of variables by category

### 5. `list_sectors`
List all available sectors for productivity shocks.

**Returns:** List of sector codes

### 6. `compare_scenarios`
Compare results between two scenarios.

**Parameters:**
- `scenario_id_1` (required): First scenario ID
- `scenario_id_2` (required): Second scenario ID
- `variables` (optional): Variables to compare

**Returns:** Comparison results

## Example Usage

### Example 1: Employment Policy Scenario

```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "emiratization_2024",
    "year": 2024,
    "steps": 5,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "x1labiEmplWgt_MIGRANTHH": -10.0,
      "realgdp": 4.5
    },
    "reporting_vars": [
      "x1labioEmplWgt",
      "employi",
      "realgdp",
      "INCGDP"
    ]
  }
}
```

### Example 2: Sector Productivity Scenario

```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "agriculture_boost",
    "year": 2024,
    "steps": 10,
    "shocks": {
      "aprimRatio_AG": 20.0,
      "realgdp": 6.0
    }
  }
}
```

### Example 3: Get Results

```json
{
  "tool": "get_scenario_results",
  "arguments": {
    "scenario_id": "emiratization_2024_20241201_143022",
    "format": "json",
    "variables": ["realgdp", "employi"]
  }
}
```

## Key Variables for MoHRE UAE

### Employment Variables
- `x1labiEmplWgt_EMIRATI`: Emirati employment weight
- `x1labiEmplWgt_MIGRANTHH`: Migrant household employment
- `x1labiEmplWgt_MIGRANTCOMB`: Migrant combined employment
- `x1labiEmplWgt_COMMUTING`: Commuting employment
- `x1labi_EMIRATI`: Direct Emirati employment
- `employi`: Employment by industry

### Economic Indicators
- `realgdp`: Real GDP growth
- `INCGDP`: GDP income
- `p0gdpexp`: GDP expenditure price
- `p3tot`: Consumer price index

### Sector Productivity
- `aprimRatio_{SECTOR}`: Productivity ratio by sector
  - Sectors: AG, MIN, FBT, TEX, LEATHER, WOOD, PPP, PC, CHM, RUBBER, NMM, METAL, MACH, ELEC, TRNEQUIP, ROMAN, ELYGASWTR, CNS, TRD, AFS, OTP, WTP, ATP, WHS, CMN, OFI, RSA, OBS, GOV, EDU, HHT, REC, DWE

### Tax Policy
- `taxcsi`: Tax rate
- `ftax`: Tax function parameter
- `f1taxcsi`, `f2taxcsi`, `f3taxcs`, `f5taxcs`: Sector-specific taxes

## Agentic Workflow Example

```
1. Agent: "I want to analyze the impact of increasing Emirati employment by 15%"
   
2. MCP Server: Uses `list_available_variables` to find employment variables
   
3. Agent: "Run a scenario with 15% Emirati employment increase and 5% GDP growth"
   
4. MCP Server: Calls `run_scenario` with:
   - shocks: {"x1labiEmplWgt_EMIRATI": 15.0, "realgdp": 5.0}
   - Returns scenario_id
   
5. Agent: "Check the status"
   
6. MCP Server: Calls `get_scenario_status` with scenario_id
   
7. Agent: "Get the results"
   
8. MCP Server: Calls `get_scenario_results` with scenario_id
   
9. Agent: Analyzes results and provides insights
```

## Resources

The server exposes scenario results as resources:
- `scenario://{scenario_id}/base`: Base simulation results
- `scenario://{scenario_id}/policy`: Policy simulation results

## Error Handling

All tools return structured error messages in JSON format:
```json
{
  "error": "Error message",
  "traceback": "Full traceback (in development mode)"
}
```

## Testing

To test the server locally:

```bash
python3 mcp_server.py
```

The server communicates via stdio using JSON-RPC 2.0 protocol.

## Notes

- Scenarios run asynchronously in the background
- Results are cached for quick retrieval
- Closure files are created automatically based on shocks
- Output files are saved in the specified output directory
- Temporary closure files are created in `temp_closures/{scenario_name}/`
