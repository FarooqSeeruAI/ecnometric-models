# FastAPI Server for CGE Model

REST API server with OpenAPI documentation for the CGE economic model.

## Installation

```bash
pip install -r requirements_api.txt
```

## Running the Server

```bash
python3 api_server.py
```

Or with uvicorn directly:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints

### General

- `GET /` - API information
- `GET /health` - Health check

### Scenarios

- `POST /api/v1/scenarios/run` - Run a scenario
- `GET /api/v1/scenarios` - List all scenarios
- `GET /api/v1/scenarios/{scenario_id}/status` - Get scenario status
- `GET /api/v1/scenarios/{scenario_id}/results` - Get scenario results
- `GET /api/v1/scenarios/{scenario_id}/download/{file_type}` - Download result files
- `POST /api/v1/scenarios/compare` - Compare two scenarios

### Chat

- `POST /api/v1/chat` - Natural language chat interface

### Variables

- `GET /api/v1/variables` - List available variables
- `GET /api/v1/sectors` - List available sectors

## Example Requests

### Run Scenario

```bash
curl -X POST "http://localhost:8000/api/v1/scenarios/run" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "emiratization_test",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0,
      "realgdp": 5.0
    },
    "reporting_vars": ["realgdp", "employi"]
  }'
```

### Chat Interface

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What if Emirati employment increases by 15%?"
  }'
```

### Get Scenario Status

```bash
curl "http://localhost:8000/api/v1/scenarios/emiratization_test_20240111_120000/status"
```

### Get Results

```bash
curl "http://localhost:8000/api/v1/scenarios/emiratization_test_20240111_120000/results?format=json&variables=realgdp,employi"
```

## OpenAPI Schema

The OpenAPI schema is automatically generated and available at `/openapi.json`. It includes:

- All endpoint definitions
- Request/response models
- Parameter descriptions
- Example values

## Python Client Example

```python
import requests

# Run scenario
response = requests.post(
    "http://localhost:8000/api/v1/scenarios/run",
    json={
        "scenario_name": "test_scenario",
        "shocks": {
            "x1labiEmplWgt_EMIRATI": 15.0
        }
    }
)
scenario_id = response.json()["scenario_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/v1/scenarios/{scenario_id}/status")
print(status.json())

# Get results
results = requests.get(f"http://localhost:8000/api/v1/scenarios/{scenario_id}/results")
print(results.json())
```

## Integration with Frontend

The API can be easily integrated with:

- React/Vue/Angular frontends
- Mobile apps
- Other microservices
- Data visualization tools

All endpoints return JSON and follow RESTful conventions.
