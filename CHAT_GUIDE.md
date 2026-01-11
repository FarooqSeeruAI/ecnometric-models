# Conversational AI Guide for CGE Model

This guide explains how to interact with the CGE model through natural language questions and what payloads are prepared.

## Question Types & Examples

### 1. Scenario Analysis Questions

**What can be asked:**
- "What would happen if we increase Emirati employment by 15%?"
- "Run a scenario with 10% GDP growth"
- "Simulate the impact of 20% productivity increase in agriculture sector"
- "What if we reduce migrant employment by 5% and increase GDP by 4%?"
- "Show me what happens with 15% emiratization and 3% inflation"

**Generated Payload:**
```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "scenario_20240111_120000",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "realgdp": 5.0
    },
    "reporting_vars": ["x1labioEmplWgt", "employi", "realgdp", "INCGDP"]
  }
}
```

### 2. Status Check Questions

**What can be asked:**
- "What's the status of scenario_20240111_120000?"
- "Is the scenario done?"
- "How is scenario_emiratization_2024 running?"

**Generated Payload:**
```json
{
  "tool": "get_scenario_status",
  "arguments": {
    "scenario_id": "scenario_20240111_120000"
  }
}
```

### 3. Results Retrieval Questions

**What can be asked:**
- "Show me the results from scenario_20240111_120000"
- "What are the GDP results?"
- "Get employment data from the last scenario"
- "Show me realgdp and employi from scenario_123"

**Generated Payload:**
```json
{
  "tool": "get_scenario_results",
  "arguments": {
    "scenario_id": "scenario_20240111_120000",
    "variables": ["realgdp", "employi"],
    "format": "json"
  }
}
```

### 4. Information Questions

**What can be asked:**
- "What variables can I shock?"
- "List all available sectors"
- "What employment variables are available?"
- "Show me economic indicators I can use"

**Generated Payload:**
```json
{
  "tool": "list_available_variables",
  "arguments": {
    "category": "employment"
  }
}
```

or

```json
{
  "tool": "list_sectors",
  "arguments": {}
}
```

### 5. Comparison Questions

**What can be asked:**
- "Compare scenario_1 and scenario_2"
- "What's the difference between baseline and policy scenario?"
- "Show me scenario_1 versus scenario_2"

**Generated Payload:**
```json
{
  "tool": "compare_scenarios",
  "arguments": {
    "scenario_id_1": "scenario_1",
    "scenario_id_2": "scenario_2",
    "variables": ["realgdp", "employi"]
  }
}
```

## Payload Structures

### Payload 1: Run Scenario (Simple)

**Question:** "What if Emirati employment increases by 15%?"

**Payload:**
```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "emiratization_15pct",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0
    }
  }
}
```

### Payload 2: Run Scenario (Complex)

**Question:** "Run a 5-year scenario starting 2024 with 15% Emirati employment increase, 10% migrant decrease, and 5% GDP growth"

**Payload:**
```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "emiratization_5yr",
    "year": 2024,
    "steps": 5,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "x1labiEmplWgt_MIGRANTHH": -10.0,
      "realgdp": 5.0
    },
    "reporting_vars": [
      "x1labioEmplWgt",
      "employi",
      "realgdp",
      "INCGDP",
      "p3tot"
    ]
  }
}
```

### Payload 3: Sector Productivity Scenario

**Question:** "What happens if agriculture productivity increases by 20%?"

**Payload:**
```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "ag_productivity_boost",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "aprimRatio_AG": 20.0
    }
  }
}
```

### Payload 4: Multi-Sector Scenario

**Question:** "Simulate 15% productivity increase in agriculture, textiles, and manufacturing"

**Payload:**
```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "multi_sector_boost",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "aprimRatio_AG": 15.0,
      "aprimRatio_TEX": 15.0,
      "aprimRatio_MACH": 15.0
    }
  }
}
```

### Payload 5: Tax Policy Scenario

**Question:** "What's the impact of 5% tax increase?"

**Payload:**
```json
{
  "tool": "run_scenario",
  "arguments": {
    "scenario_name": "tax_increase_5pct",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "taxcsi": 5.0
    },
    "reporting_vars": [
      "realgdp",
      "INCGDP",
      "taxcsi",
      "p3tot"
    ]
  }
}
```

### Payload 6: Get Results (Filtered)

**Question:** "Show me GDP and employment results from scenario_123"

**Payload:**
```json
{
  "tool": "get_scenario_results",
  "arguments": {
    "scenario_id": "scenario_123",
    "variables": ["realgdp", "employi"],
    "format": "json"
  }
}
```

## Natural Language Mappings

### Employment Terms
- "Emirati employment" → `x1labiEmplWgt_EMIRATI`
- "Emiratization" → `x1labiEmplWgt_EMIRATI`
- "Migrant employment" → `x1labiEmplWgt_MIGRANTHH`
- "Commuting" → `x1labiEmplWgt_COMMUTING`
- "Employment" → `employi`
- "Wages" → `p1labi`

### Economic Terms
- "GDP" / "GDP growth" → `realgdp`
- "Economic growth" → `realgdp`
- "Inflation" / "CPI" → `p3tot`
- "Consumer prices" → `p3tot`

### Sector Terms
- "Agriculture" / "Farming" → `aprimRatio_AG`
- "Mining" → `aprimRatio_MIN`
- "Food" / "Food and beverages" → `aprimRatio_FBT`
- "Textiles" → `aprimRatio_TEX`
- "Manufacturing" / "Machinery" → `aprimRatio_MACH`
- "Construction" → `aprimRatio_CNS`
- "Trade" → `aprimRatio_TRD`
- "Finance" → `aprimRatio_OFI`
- "Government" → `aprimRatio_GOV`
- "Education" → `aprimRatio_EDU`
- "Health" → `aprimRatio_HHT`

### Tax Terms
- "Tax" / "Tax rate" → `taxcsi`
- "Taxation" → `taxcsi`

## Example Conversations

### Conversation 1: Simple Employment Scenario

**User:** "What would happen if we increase Emirati employment by 15%?"

**Agent Response:**
```
I'll run a scenario with 15% increase in Emirati employment.
Scenario ID: emiratization_15pct_20240111_120000
Status: Running...
```

**User:** "What's the status?"

**Agent Response:**
```
The scenario is still running. It typically takes 1-2 minutes.
```

**User:** "Show me the results"

**Agent Response:**
```
Here are the key results:
- Emirati employment increased by 15.0%
- GDP impact: +2.3%
- Overall employment: +3.1%
- Consumer prices: +0.8%
```

### Conversation 2: Multi-Parameter Scenario

**User:** "Run a scenario with 10% Emirati employment increase, 5% migrant decrease, and 4% GDP growth for 5 years starting 2024"

**Agent Response:**
```
I've prepared a 5-year scenario starting 2024 with:
- Emirati employment: +10%
- Migrant employment: -5%
- GDP growth target: 4%

Scenario ID: multi_param_2024_20240111_120000
Running simulation...
```

### Conversation 3: Sector Analysis

**User:** "What happens if agriculture productivity increases by 20%?"

**Agent Response:**
```
Running scenario with 20% agriculture productivity increase...
Scenario ID: ag_boost_20240111_120000

Results:
- Agriculture output: +18.5%
- GDP impact: +1.2%
- Employment in agriculture: +5.3%
- Food prices: -3.2%
```

### Conversation 4: Comparison

**User:** "Compare the baseline scenario with the emiratization policy scenario"

**Agent Response:**
```
Comparing scenarios:
- Baseline GDP growth: 3.5%
- Policy GDP growth: 4.2% (+0.7%)
- Baseline Emirati employment: 0%
- Policy Emirati employment: +15%
- Employment impact: +8.3% overall
```

## Integration with Chat Interface

### Using with OpenAI/Anthropic API

```python
from chat_agent import CGEModelChatAgent
import openai  # or anthropic

agent = CGEModelChatAgent()

def chat_with_model(user_message: str, conversation_history: List[Dict]):
    # Parse user question
    parsed = agent.parse_question(user_message)
    
    if parsed["intent"] == "run_scenario":
        # Call MCP server
        mcp_response = call_mcp_tool(parsed["tool"], parsed["payload"])
        return agent.format_response(mcp_response, user_message)
    
    # For other intents, handle similarly
    ...
```

### Using with LangChain

```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from chat_agent import CGEModelChatAgent

agent = CGEModelChatAgent()

def create_cge_tool():
    def run_cge_scenario(query: str):
        parsed = agent.parse_question(query)
        if parsed["tool"]:
            return call_mcp_tool(parsed["tool"], parsed["payload"])
        return "I didn't understand. Please rephrase."
    
    return Tool(
        name="CGE_Model",
        func=run_cge_scenario,
        description="Run economic simulations and analyze scenarios"
    )
```

## Response Format

All responses follow this structure:

```json
{
  "intent": "run_scenario|status|results|list|compare",
  "tool": "mcp_tool_name",
  "payload": {
    // Tool-specific arguments
  },
  "confidence": 0.0-1.0,
  "message": "Human-readable message"
}
```

## Error Handling

If the agent can't parse a question:

```json
{
  "intent": "unknown",
  "tool": null,
  "payload": {},
  "confidence": 0.0,
  "message": "I didn't understand. Try asking: 'What if we increase Emirati employment by 15%?' or 'Show me available variables'"
}
```

## Best Practices

1. Be specific with percentages: "15%" not "some increase"
2. Mention variable names when possible: "Emirati employment" not just "employment"
3. Specify timeframes: "5 years" or "starting 2024"
4. Ask for status before results
5. Use scenario IDs for follow-up questions
