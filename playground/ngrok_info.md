# Ngrok Status

## Current Status

✅ **FastAPI Server**: Running on http://localhost:8000
✅ **Ngrok**: Running (process active)

## How to Get Your Public URL

### Option 1: Ngrok Web Interface
Open in your browser:
```
http://localhost:4040
```

This shows:
- Your public HTTPS URL
- All incoming requests
- Request/response details

### Option 2: Check Terminal Output
Look at the terminal where you ran `ngrok http 8000` - it will show:
```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

### Option 3: API Call
```bash
curl http://localhost:4040/api/tunnels | python3 -m json.tool
```

## Access Your API

Once you have the ngrok URL (e.g., `https://abc123.ngrok-free.app`):

- **API Root**: `https://abc123.ngrok-free.app/`
- **Swagger UI**: `https://abc123.ngrok-free.app/docs`
- **ReDoc**: `https://abc123.ngrok-free.app/redoc`
- **OpenAPI JSON**: `https://abc123.ngrok-free.app/openapi.json`
- **Health Check**: `https://abc123.ngrok-free.app/health`

## Test Your Public API

```bash
# Replace YOUR_NGROK_URL with your actual URL
NGROK_URL="https://your-ngrok-url.ngrok-free.app"

# Health check
curl "$NGROK_URL/health"

# Run scenario
curl -X POST "$NGROK_URL/api/v1/scenarios/run" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "test",
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0
    }
  }'
```

## Troubleshooting

If ngrok shows "No HTTPS tunnel found":
1. Check if ngrok is authenticated: `ngrok config check`
2. If not authenticated: `ngrok config add-authtoken YOUR_TOKEN`
3. Restart ngrok: `ngrok http 8000`

## Notes

- Free ngrok URLs change each time you restart ngrok
- For static URLs, upgrade to ngrok paid plan
- The ngrok web interface at localhost:4040 shows all requests in real-time
