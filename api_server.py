#!/usr/bin/env python3
"""
FastAPI Server for CGE Model
Provides REST API endpoints with OpenAPI documentation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
import os
from pathlib import Path
import traceback

# Import chat agent and model components
from chat_agent import CGEModelChatAgent
from solver import Model, ModelException, run_model
import yaml
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="CGE Model API",
    description="REST API for CGE Economic Model - MoHRE UAE",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat agent
chat_agent = CGEModelChatAgent()

# In-memory storage for scenarios
scenarios_db: Dict[str, Dict[str, Any]] = {}

# Model directory
MODEL_DIR = Path(__file__).parent.absolute()


# Pydantic Models for Request/Response
class ShockRequest(BaseModel):
    """Single shock parameter"""
    variable: str = Field(..., description="Variable name (e.g., x1labiEmplWgt_EMIRATI)")
    value: float = Field(..., description="Shock value in percentage")


class RunScenarioRequest(BaseModel):
    """Request to run a scenario"""
    scenario_name: str = Field(..., description="Unique name for the scenario")
    year: int = Field(2023, description="Starting year", ge=2020, le=2100)
    steps: int = Field(1, description="Number of years to simulate", ge=1, le=50)
    shocks: Dict[str, float] = Field(..., description="Dictionary of variable shocks")
    reporting_vars: Optional[List[str]] = Field(None, description="Variables to include in output")
    output_dir: Optional[str] = Field(None, description="Directory for output files")


class ChatRequest(BaseModel):
    """Natural language chat request"""
    question: str = Field(..., description="Natural language question")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ScenarioStatusResponse(BaseModel):
    """Scenario status response"""
    scenario_id: str
    status: str
    scenario_name: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_dir: Optional[str] = None


class ScenarioResultsResponse(BaseModel):
    """Scenario results response"""
    scenario_id: str
    results: Dict[str, Any]
    format: str


class ChatResponse(BaseModel):
    """Chat response"""
    intent: str
    tool: Optional[str] = None
    payload: Dict[str, Any]
    confidence: float
    message: str
    scenario_id: Optional[str] = None


class VariableListResponse(BaseModel):
    """Variable list response"""
    category: str
    variables: Dict[str, List[str]]


class SectorListResponse(BaseModel):
    """Sector list response"""
    sectors: List[str]


class CompareScenariosRequest(BaseModel):
    """Request to compare scenarios"""
    scenario_id_1: str
    scenario_id_2: str
    variables: Optional[List[str]] = None


# API Endpoints

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CGE Model API",
        "version": "1.0.0",
        "description": "REST API for CGE Economic Model - MoHRE UAE",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/scenarios/run", response_model=ScenarioStatusResponse, tags=["Scenarios"])
async def run_scenario(request: RunScenarioRequest, background_tasks: BackgroundTasks):
    """
    Run a CGE model scenario with specified shocks
    
    - **scenario_name**: Unique name for the scenario
    - **year**: Starting year (default: 2023)
    - **steps**: Number of years to simulate (default: 1)
    - **shocks**: Dictionary of variable shocks {variable_name: shock_value}
    - **reporting_vars**: Optional list of variables to include in output
    """
    scenario_id = f"{request.scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = request.output_dir or f"outputs/{request.scenario_name}"
    
    # Store scenario info
    scenarios_db[scenario_id] = {
        "scenario_id": scenario_id,
        "status": "running",
        "scenario_name": request.scenario_name,
        "started_at": datetime.now().isoformat(),
        "year": request.year,
        "steps": request.steps,
        "shocks": request.shocks,
        "output_dir": output_dir
    }
    
    # Run scenario in background
    background_tasks.add_task(
        execute_scenario,
        scenario_id,
        request.scenario_name,
        request.year,
        request.steps,
        request.shocks,
        request.reporting_vars,
        output_dir
    )
    
    return ScenarioStatusResponse(
        scenario_id=scenario_id,
        status="running",
        scenario_name=request.scenario_name,
        started_at=scenarios_db[scenario_id]["started_at"]
    )


async def execute_scenario(
    scenario_id: str,
    scenario_name: str,
    year: int,
    steps: int,
    shocks: Dict[str, float],
    reporting_vars: Optional[List[str]],
    output_dir: str
):
    """Execute scenario in background"""
    try:
        # Create config
        config = create_scenario_config(
            scenario_name, year, steps, shocks, reporting_vars, output_dir
        )
        
        # Create temp config file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, dir=MODEL_DIR) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        # Change to model directory
        original_dir = os.getcwd()
        os.chdir(MODEL_DIR)
        
        try:
            # Run model
            run_model(model_file="orani.model", do_policy=True)
            
            # Update status
            scenarios_db[scenario_id]["status"] = "completed"
            scenarios_db[scenario_id]["completed_at"] = datetime.now().isoformat()
            
        finally:
            os.chdir(original_dir)
            if os.path.exists(config_path):
                os.unlink(config_path)
                
    except Exception as e:
        scenarios_db[scenario_id]["status"] = "error"
        scenarios_db[scenario_id]["error"] = str(e)
        scenarios_db[scenario_id]["error_traceback"] = traceback.format_exc()


def create_scenario_config(
    scenario_name: str, year: int, steps: int,
    shocks: Dict[str, float], reporting_vars: Optional[List[str]],
    output_dir: str
) -> Dict[str, Any]:
    """Create scenario configuration"""
    with open(MODEL_DIR / "default.yml", 'r') as f:
        base_config = yaml.safe_load(f)
    
    # Create closure files
    base_closures = []
    policy_closures = []
    
    closures_dir = MODEL_DIR / "closures"
    temp_closures_dir = MODEL_DIR / f"temp_closures/{scenario_name}"
    temp_closures_dir.mkdir(parents=True, exist_ok=True)
    
    for step in range(steps):
        current_year = year + step
        base_closure = closures_dir / f"base{current_year}.txt"
        if not base_closure.exists():
            base_closure = closures_dir / "base2023.txt"
        base_closures.append(str(base_closure))
        
        policy_closure = temp_closures_dir / f"pol{current_year}.txt"
        create_shock_closure(base_closure, shocks, policy_closure)
        policy_closures.append(str(policy_closure))
    
    config = base_config.copy()
    config["steps"] = steps
    config["basefiles"] = base_closures
    config["polfiles"] = policy_closures
    if reporting_vars:
        config["reportingvars"] = reporting_vars
    
    return config


def create_shock_closure(base_closure: Path, shocks: Dict[str, float], output_path: Path):
    """Create closure file with shocks"""
    lines = []
    if base_closure.exists():
        with open(base_closure, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    
    for var_name, shock_value in shocks.items():
        var_found = False
        for i, line in enumerate(lines):
            if line.startswith('shock') and var_name in line:
                lines[i] = f"shock {var_name} {shock_value}"
                var_found = True
                break
            elif line.startswith('add') and var_name in line:
                var_found = True
                if not any(lines[j].startswith('shock') and var_name in lines[j] 
                          for j in range(i+1, len(lines))):
                    lines.insert(i+1, f"shock {var_name} {shock_value}")
                break
        
        if not var_found:
            lines.append(f"add {var_name}")
            lines.append(f"shock {var_name} {shock_value}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for line in lines:
            f.write(line + '\n')


@app.get("/api/v1/scenarios/{scenario_id}/status", response_model=ScenarioStatusResponse, tags=["Scenarios"])
async def get_scenario_status(scenario_id: str):
    """
    Get the status of a running or completed scenario
    
    - **scenario_id**: Scenario ID returned from run_scenario
    """
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    scenario = scenarios_db[scenario_id]
    return ScenarioStatusResponse(**scenario)


@app.get("/api/v1/scenarios/{scenario_id}/results", response_model=ScenarioResultsResponse, tags=["Scenarios"])
async def get_scenario_results(
    scenario_id: str,
    variables: Optional[str] = None,
    format: str = "json"
):
    """
    Get results from a completed scenario
    
    - **scenario_id**: Scenario ID
    - **variables**: Comma-separated list of variables to retrieve (optional)
    - **format**: Output format - "json" or "excel" (default: json)
    """
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    scenario = scenarios_db[scenario_id]
    if scenario["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Scenario not completed. Status: {scenario['status']}"
        )
    
    output_dir = Path(scenario.get("output_dir", f"outputs/{scenario['scenario_name']}"))
    if not output_dir.is_absolute():
        output_dir = MODEL_DIR / output_dir
    
    if format == "json":
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
                var_list = [v.strip() for v in variables.split(",")]
                filtered_results = {}
                for sim_type in results:
                    filtered_results[sim_type] = [
                        row for row in results[sim_type]
                        if any(var in str(row.get("SVAR", "")) for var in var_list)
                    ]
                results = filtered_results
            
            return ScenarioResultsResponse(
                scenario_id=scenario_id,
                results=results,
                format="json"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read results: {str(e)}")
    else:
        # Return file paths
        return ScenarioResultsResponse(
            scenario_id=scenario_id,
            results={
                "base_file": str(output_dir / "base.xlsx"),
                "policy_file": str(output_dir / "policy.xlsx")
            },
            format="excel"
        )


@app.get("/api/v1/scenarios/{scenario_id}/download/{file_type}", tags=["Scenarios"])
async def download_scenario_file(scenario_id: str, file_type: str):
    """
    Download scenario result files
    
    - **scenario_id**: Scenario ID
    - **file_type**: "base" or "policy"
    """
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    scenario = scenarios_db[scenario_id]
    output_dir = Path(scenario.get("output_dir", f"outputs/{scenario['scenario_name']}"))
    if not output_dir.is_absolute():
        output_dir = MODEL_DIR / output_dir
    
    file_path = output_dir / f"{file_type}.xlsx"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_type}.xlsx not found")
    
    return FileResponse(
        path=str(file_path),
        filename=f"{scenario_id}_{file_type}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Natural language chat interface
    
    Ask questions in natural language and get parsed responses with MCP tool payloads
    
    - **question**: Natural language question
    - **context**: Additional context (optional)
    """
    try:
        parsed = chat_agent.parse_question(request.question)
        
        # If it's a run_scenario intent, actually run it
        scenario_id = None
        if parsed["intent"] == "run_scenario" and parsed["tool"] == "run_scenario":
            payload = parsed["payload"]
            if payload and "shocks" in payload:
                # Create a background task to run the scenario
                scenario_id = f"{payload.get('scenario_name', 'chat_scenario')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                # Note: In production, you'd want to use BackgroundTasks here
                parsed["scenario_id"] = scenario_id
        
        return ChatResponse(
            intent=parsed["intent"],
            tool=parsed.get("tool"),
            payload=parsed.get("payload", {}),
            confidence=parsed.get("confidence", 0.0),
            message=parsed.get("message", ""),
            scenario_id=scenario_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/api/v1/variables", response_model=VariableListResponse, tags=["Variables"])
async def list_variables(category: str = "all"):
    """
    List all available variables that can be used in shocks or reporting
    
    - **category**: Filter by category - "employment", "economic", "productivity", "tax", or "all"
    """
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
    
    return VariableListResponse(category=category, variables=result)


@app.get("/api/v1/sectors", response_model=SectorListResponse, tags=["Variables"])
async def list_sectors():
    """
    List all available sectors for productivity shocks
    """
    sectors = [
        "AG", "MIN", "FBT", "TEX", "LEATHER", "WOOD", "PPP", "PC",
        "CHM", "RUBBER", "NMM", "METAL", "MACH", "ELEC", "TRNEQUIP",
        "ROMAN", "ELYGASWTR", "CNS", "TRD", "AFS", "OTP", "WTP",
        "ATP", "WHS", "CMN", "OFI", "RSA", "OBS", "GOV", "EDU",
        "HHT", "REC", "DWE"
    ]
    
    return SectorListResponse(sectors=sectors)


@app.post("/api/v1/scenarios/compare", tags=["Scenarios"])
async def compare_scenarios(request: CompareScenariosRequest):
    """
    Compare results between two scenarios
    
    - **scenario_id_1**: First scenario ID
    - **scenario_id_2**: Second scenario ID
    - **variables**: Optional list of variables to compare
    """
    if request.scenario_id_1 not in scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {request.scenario_id_1} not found")
    if request.scenario_id_2 not in scenarios_db:
        raise HTTPException(status_code=404, detail=f"Scenario {request.scenario_id_2} not found")
    
    # Get results for both scenarios
    results_1 = await get_scenario_results(request.scenario_id_1, None, "json")
    results_2 = await get_scenario_results(request.scenario_id_2, None, "json")
    
    comparison = {
        "scenario_1": request.scenario_id_1,
        "scenario_2": request.scenario_id_2,
        "results_1": results_1.results,
        "results_2": results_2.results,
        "comparison": "Detailed comparison would be implemented here"
    }
    
    return comparison


@app.get("/api/v1/scenarios", tags=["Scenarios"])
async def list_scenarios():
    """
    List all scenarios
    """
    return {
        "scenarios": [
            {
                "scenario_id": sid,
                "scenario_name": data.get("scenario_name"),
                "status": data.get("status"),
                "started_at": data.get("started_at")
            }
            for sid, data in scenarios_db.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
