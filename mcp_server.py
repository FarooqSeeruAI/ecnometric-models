#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for CGE Model
Enables agentic workflows for economic simulations
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import traceback
import yaml
import pandas as pd

# Add the model directory to path
MODEL_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(MODEL_DIR))

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        Resource,
        Prompt,
        PromptMessage,
        PromptArgument,
    )
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import model components
from solver import Model, ModelException, run_model


class CGEModelServer:
    """MCP Server for CGE Model operations"""
    
    def __init__(self):
        self.server = Server("cge-model-server")
        self.scenarios = {}
        self.results_cache = {}
        self.setup_handlers()
    
    def setup_handlers(self):
        """Register all MCP handlers"""
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
        self.server.list_resources = self.list_resources
        self.server.read_resource = self.read_resource
        self.server.list_prompts = self.list_prompts
        self.server.get_prompt = self.get_prompt
    
    async def list_tools(self) -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="run_scenario",
                description="Run a CGE model scenario with specified shocks and parameters. Returns scenario ID for tracking.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scenario_name": {
                            "type": "string",
                            "description": "Unique name for this scenario"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Starting year (default: 2023)",
                            "default": 2023
                        },
                        "steps": {
                            "type": "integer",
                            "description": "Number of years to simulate (default: 1)",
                            "default": 1
                        },
                        "shocks": {
                            "type": "object",
                            "description": "Dictionary of variable shocks. Key is variable name, value is shock percentage.",
                            "additionalProperties": {
                                "type": "number"
                            },
                            "examples": {
                                "x1labiEmplWgt_EMIRATI": 10.0,
                                "realgdp": 5.0,
                                "aprimRatio_AG": 15.0
                            }
                        },
                        "reporting_vars": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of variables to include in output (optional)"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Directory for output files (optional)"
                        }
                    },
                    "required": ["scenario_name", "shocks"]
                }
            ),
            Tool(
                name="get_scenario_status",
                description="Get the status of a running or completed scenario",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scenario_id": {
                            "type": "string",
                            "description": "Scenario ID returned from run_scenario"
                        }
                    },
                    "required": ["scenario_id"]
                }
            ),
            Tool(
                name="get_scenario_results",
                description="Get results from a completed scenario. Returns JSON summary of key variables.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scenario_id": {
                            "type": "string",
                            "description": "Scenario ID"
                        },
                        "variables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific variables to retrieve (optional, returns all if not specified)"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "excel"],
                            "description": "Output format (default: json)",
                            "default": "json"
                        }
                    },
                    "required": ["scenario_id"]
                }
            ),
            Tool(
                name="list_available_variables",
                description="List all available variables that can be used in shocks or reporting",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["employment", "economic", "productivity", "tax", "all"],
                            "description": "Filter by variable category",
                            "default": "all"
                        }
                    }
                }
            ),
            Tool(
                name="list_sectors",
                description="List all available sectors for productivity shocks",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="compare_scenarios",
                description="Compare results between two scenarios",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scenario_id_1": {
                            "type": "string",
                            "description": "First scenario ID"
                        },
                        "scenario_id_2": {
                            "type": "string",
                            "description": "Second scenario ID"
                        },
                        "variables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Variables to compare (optional)"
                        }
                    },
                    "required": ["scenario_id_1", "scenario_id_2"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        try:
            if name == "run_scenario":
                return await self._run_scenario(arguments)
            elif name == "get_scenario_status":
                return await self._get_scenario_status(arguments)
            elif name == "get_scenario_results":
                return await self._get_scenario_results(arguments)
            elif name == "list_available_variables":
                return await self._list_available_variables(arguments)
            elif name == "list_sectors":
                return await self._list_sectors(arguments)
            elif name == "compare_scenarios":
                return await self._compare_scenarios(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }, indent=2)
            )]
    
    async def _run_scenario(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run a scenario"""
        scenario_name = args["scenario_name"]
        year = args.get("year", 2023)
        steps = args.get("steps", 1)
        shocks = args.get("shocks", {})
        reporting_vars = args.get("reporting_vars")
        output_dir = args.get("output_dir", f"outputs/{scenario_name}")
        
        scenario_id = f"{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create temporary config
        config = self._create_scenario_config(
            scenario_name=scenario_name,
            year=year,
            steps=steps,
            shocks=shocks,
            reporting_vars=reporting_vars,
            output_dir=output_dir
        )
        
        # Store scenario info
        self.scenarios[scenario_id] = {
            "status": "running",
            "config": config,
            "started_at": datetime.now().isoformat(),
            "scenario_name": scenario_name,
            "output_dir": output_dir
        }
        
        # Run in background
        asyncio.create_task(self._execute_scenario(scenario_id, config))
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "scenario_id": scenario_id,
                "status": "started",
                "message": f"Scenario '{scenario_name}' started. Use get_scenario_status to check progress."
            }, indent=2)
        )]
    
    async def _execute_scenario(self, scenario_id: str, config: Dict[str, Any]):
        """Execute scenario in background"""
        try:
            # Create temp config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, dir=MODEL_DIR) as f:
                yaml.dump(config, f)
                config_path = f.name
            
            # Change to model directory
            original_dir = os.getcwd()
            os.chdir(MODEL_DIR)
            
            try:
                # Create model instance with custom config
                model = Model(ymlfile=config_path)
                
                # Parse model file
                model.parse_model_file(config.get("model_file", "orani.model"))
                
                # Read data
                model.read_datavars()
                
                if model.solve:
                    # Take differentials
                    model.equation_manager.diffall(model.solvarhandler, model.datavarvals)
                    
                    # Read closures
                    model.read_closure_shocks()
                    
                    # Run simulation (simplified - uses existing run_model logic)
                    # This would need full porting of the solving logic
                    # For now, we'll use the existing run_model function
                    run_model(model_file=config.get("model_file", "orani.model"), do_policy=True)
                
                # Update status
                self.scenarios[scenario_id]["status"] = "completed"
                self.scenarios[scenario_id]["completed_at"] = datetime.now().isoformat()
                
            finally:
                os.chdir(original_dir)
                if os.path.exists(config_path):
                    os.unlink(config_path)
            
        except Exception as e:
            self.scenarios[scenario_id]["status"] = "error"
            self.scenarios[scenario_id]["error"] = str(e)
            self.scenarios[scenario_id]["error_traceback"] = traceback.format_exc()
    
    def _create_scenario_config(self, scenario_name: str, year: int, steps: int,
                                shocks: Dict[str, float], reporting_vars: Optional[List[str]],
                                output_dir: str) -> Dict[str, Any]:
        """Create scenario configuration"""
        # Load base config
        config_path = MODEL_DIR / "default.yml"
        with open(config_path, 'r') as f:
            base_config = yaml.safe_load(f)
        
        # Create closure files for each step
        base_closures = []
        policy_closures = []
        
        closures_dir = MODEL_DIR / "closures"
        temp_closures_dir = MODEL_DIR / f"temp_closures/{scenario_name}"
        temp_closures_dir.mkdir(parents=True, exist_ok=True)
        
        for step in range(steps):
            current_year = year + step
            
            # Base closure
            base_closure = closures_dir / f"base{current_year}.txt"
            if base_closure.exists():
                base_closures.append(str(base_closure))
            else:
                # Use first available base closure as template
                first_base = closures_dir / "base2023.txt"
                if first_base.exists():
                    base_closures.append(str(first_base))
                else:
                    base_closures.append(str(base_closure))
            
            # Policy closure with shocks
            policy_closure = temp_closures_dir / f"pol{current_year}.txt"
            self._create_shock_closure(
                base_closure if base_closure.exists() else closures_dir / "base2023.txt",
                shocks,
                policy_closure
            )
            policy_closures.append(str(policy_closure))
        
        config = base_config.copy()
        config["steps"] = steps
        config["basefiles"] = base_closures
        config["polfiles"] = policy_closures
        if reporting_vars:
            config["reportingvars"] = reporting_vars
        config["scenario_name"] = scenario_name
        config["output_dir"] = output_dir
        config["model_file"] = "orani.model"
        
        return config
    
    def _create_shock_closure(self, base_closure: Path, 
                             shocks: Dict[str, float], 
                             output_path: Path):
        """Create closure file with shocks"""
        lines = []
        
        if base_closure and base_closure.exists():
            with open(base_closure, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Apply shocks
        for var_name, shock_value in shocks.items():
            # Check if variable is already in closure
            var_found = False
            for i, line in enumerate(lines):
                if line.startswith('shock') and var_name in line:
                    lines[i] = f"shock {var_name} {shock_value}"
                    var_found = True
                    break
                elif line.startswith('add') and var_name in line:
                    var_found = True
                    # Add shock after add statement
                    insert_pos = i + 1
                    has_shock = any(
                        lines[j].startswith('shock') and var_name in lines[j]
                        for j in range(i+1, len(lines))
                    )
                    if not has_shock:
                        lines.insert(insert_pos, f"shock {var_name} {shock_value}")
                    break
            
            if not var_found:
                lines.append(f"add {var_name}")
                lines.append(f"shock {var_name} {shock_value}")
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            for line in lines:
                f.write(line + '\n')
    
    async def _get_scenario_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get scenario status"""
        scenario_id = args["scenario_id"]
        
        if scenario_id not in self.scenarios:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Scenario {scenario_id} not found"}, indent=2)
            )]
        
        status = self.scenarios[scenario_id].copy()
        # Remove large config from status
        if "config" in status:
            del status["config"]
        return [TextContent(
            type="text",
            text=json.dumps(status, indent=2, default=str)
        )]
    
    async def _get_scenario_results(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get scenario results"""
        scenario_id = args["scenario_id"]
        variables = args.get("variables")
        format_type = args.get("format", "json")
        
        if scenario_id not in self.scenarios:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Scenario {scenario_id} not found"}, indent=2)
            )]
        
        scenario = self.scenarios[scenario_id]
        if scenario["status"] != "completed":
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Scenario not completed. Status: {scenario['status']}"
                }, indent=2)
            )]
        
        output_dir = Path(scenario.get("output_dir", f"outputs/{scenario['scenario_name']}"))
        if not output_dir.is_absolute():
            output_dir = MODEL_DIR / output_dir
        
        if format_type == "json":
            # Read Excel and convert to JSON
            try:
                base_file = output_dir / "base.xlsx"
                policy_file = output_dir / "policy.xlsx"
                
                results = {}
                if base_file.exists():
                    base_df = pd.read_excel(base_file, sheet_name="svars")
                    results["base"] = base_df.to_dict(orient="records")
                
                if policy_file.exists():
                    policy_df = pd.read_excel(policy_file, sheet_name="svars")
                    results["policy"] = policy_df.to_dict(orient="records")
                
                if variables:
                    # Filter to requested variables
                    filtered_results = {}
                    for sim_type in results:
                        filtered_results[sim_type] = [
                            row for row in results[sim_type]
                            if any(var in str(row.get("SVAR", "")) for var in variables)
                        ]
                    results = filtered_results
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Failed to read results: {str(e)}"}, indent=2)
                )]
        else:
            # Return file paths
            return [TextContent(
                type="text",
                text=json.dumps({
                    "base_file": str(output_dir / "base.xlsx"),
                    "policy_file": str(output_dir / "policy.xlsx")
                }, indent=2)
            )]
    
    async def _list_available_variables(self, args: Dict[str, Any]) -> List[TextContent]:
        """List available variables"""
        category = args.get("category", "all")
        
        variables = {
            "employment": [
                "x1labiEmplWgt_EMIRATI",
                "x1labiEmplWgt_MIGRANTHH",
                "x1labiEmplWgt_MIGRANTCOMB",
                "x1labiEmplWgt_COMMUTING",
                "x1labi_EMIRATI",
                "employi",
                "f1labio",
                "p1labi"
            ],
            "economic": [
                "realgdp",
                "INCGDP",
                "p0gdpexp",
                "p3tot",
                "x0gdpexp",
                "V0GDPINC"
            ],
            "productivity": [
                f"aprimRatio_{sector}" for sector in [
                    "AG", "MIN", "FBT", "TEX", "LEATHER", "WOOD", "PPP", "PC",
                    "CHM", "RUBBER", "NMM", "METAL", "MACH", "ELEC", "TRNEQUIP",
                    "ROMAN", "ELYGASWTR", "CNS", "TRD", "AFS", "OTP", "WTP",
                    "ATP", "WHS", "CMN", "OFI", "RSA", "OBS", "GOV", "EDU",
                    "HHT", "REC", "DWE"
                ]
            ],
            "tax": [
                "taxcsi",
                "ftax",
                "f1taxcsi",
                "f2taxcsi",
                "f3taxcs",
                "f5taxcs",
                "f0taxs"
            ]
        }
        
        if category == "all":
            result = variables
        else:
            result = {category: variables.get(category, [])}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _list_sectors(self, args: Dict[str, Any]) -> List[TextContent]:
        """List available sectors"""
        sectors = [
            "AG", "MIN", "FBT", "TEX", "LEATHER", "WOOD", "PPP", "PC",
            "CHM", "RUBBER", "NMM", "METAL", "MACH", "ELEC", "TRNEQUIP",
            "ROMAN", "ELYGASWTR", "CNS", "TRD", "AFS", "OTP", "WTP",
            "ATP", "WHS", "CMN", "OFI", "RSA", "OBS", "GOV", "EDU",
            "HHT", "REC", "DWE"
        ]
        
        return [TextContent(
            type="text",
            text=json.dumps({"sectors": sectors}, indent=2)
        )]
    
    async def _compare_scenarios(self, args: Dict[str, Any]) -> List[TextContent]:
        """Compare two scenarios"""
        scenario_id_1 = args["scenario_id_1"]
        scenario_id_2 = args["scenario_id_2"]
        variables = args.get("variables")
        
        # Get results for both scenarios
        results_1_data = await self._get_scenario_results({
            "scenario_id": scenario_id_1,
            "format": "json",
            "variables": variables
        })
        results_2_data = await self._get_scenario_results({
            "scenario_id": scenario_id_2,
            "format": "json",
            "variables": variables
        })
        
        # Parse JSON from TextContent
        results_1 = json.loads(results_1_data[0].text) if results_1_data else {}
        results_2 = json.loads(results_2_data[0].text) if results_2_data else {}
        
        comparison = {
            "scenario_1": scenario_id_1,
            "scenario_2": scenario_id_2,
            "comparison": "Results comparison would be implemented here",
            "results_1": results_1,
            "results_2": results_2
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(comparison, indent=2, default=str)
        )]
    
    async def list_resources(self) -> List[Resource]:
        """List available resources"""
        resources = []
        
        for scenario_id, scenario in self.scenarios.items():
            if scenario["status"] == "completed":
                resources.append(Resource(
                    uri=f"scenario://{scenario_id}/base",
                    name=f"{scenario['scenario_name']} - Base Results",
                    description=f"Base simulation results for {scenario['scenario_name']}",
                    mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ))
                resources.append(Resource(
                    uri=f"scenario://{scenario_id}/policy",
                    name=f"{scenario['scenario_name']} - Policy Results",
                    description=f"Policy simulation results for {scenario['scenario_name']}",
                    mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ))
        
        return resources
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource"""
        if uri.startswith("scenario://"):
            parts = uri.split("/")
            scenario_id = parts[1]
            result_type = parts[2] if len(parts) > 2 else "base"
            
            if scenario_id in self.scenarios:
                scenario = self.scenarios[scenario_id]
                output_dir = Path(scenario.get("output_dir", f"outputs/{scenario['scenario_name']}"))
                if not output_dir.is_absolute():
                    output_dir = MODEL_DIR / output_dir
                file_path = output_dir / f"{result_type}.xlsx"
                
                if file_path.exists():
                    return str(file_path)
        
        raise ValueError(f"Resource not found: {uri}")
    
    async def list_prompts(self) -> List[Prompt]:
        """List available prompts"""
        return [
            Prompt(
                name="employment_policy_scenario",
                description="Create a scenario for employment policy analysis",
                arguments=[
                    PromptArgument(
                        name="emirati_change",
                        description="Percentage change in Emirati employment",
                        required=True
                    ),
                    PromptArgument(
                        name="migrant_change",
                        description="Percentage change in migrant employment",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="productivity_scenario",
                description="Create a scenario for sector productivity analysis",
                arguments=[
                    PromptArgument(
                        name="sector",
                        description="Sector code (e.g., AG, MIN, FBT)",
                        required=True
                    ),
                    PromptArgument(
                        name="productivity_change",
                        description="Percentage change in productivity",
                        required=True
                    )
                ]
            )
        ]
    
    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Get a prompt"""
        if name == "employment_policy_scenario":
            emirati_change = arguments.get("emirati_change", 0)
            migrant_change = arguments.get("migrant_change", 0)
            
            return [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Run a scenario with Emirati employment change of {emirati_change}% and migrant employment change of {migrant_change}%"
                    )
                )
            ]
        elif name == "productivity_scenario":
            sector = arguments.get("sector")
            productivity_change = arguments.get("productivity_change", 0)
            
            return [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Run a scenario with {productivity_change}% productivity increase in {sector} sector"
                    )
                )
            ]
        
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main entry point"""
    server_instance = CGEModelServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
