# Local Setup with Nginx ✅

## Status: Running!

Your CGE Model API is now running locally behind nginx.

## Access URLs

### 🌐 Swagger UI (Interactive Documentation)
**http://localhost:8080/docs**

### 📋 OpenAPI Specification
**http://localhost:8080/openapi.json**

### ❤️ Health Check
**http://localhost:8080/health**

### 🔴 ReDoc (Alternative Documentation)
**http://localhost:8080/redoc**

## Architecture

```
Browser → nginx (port 8080) → FastAPI (port 8000)
```

- **Nginx**: Reverse proxy on port 8080
- **FastAPI**: API server on port 8000 (internal)

## Configuration Files

- **Nginx Config**: `/opt/homebrew/etc/nginx/servers/cge_api.conf`
- **API Server**: `api_server.py` (runs on port 8000)

## Logs

### API Server Logs
```bash
tail -f logs/api.log
```

### Nginx Access Logs
```bash
tail -f /opt/homebrew/var/log/nginx/cge_api_access.log
```

### Nginx Error Logs
```bash
tail -f /opt/homebrew/var/log/nginx/cge_api_error.log
```

## Management Commands

### Check API Server Status
```bash
ps aux | grep api_server
```

### Check Nginx Status
```bash
ps aux | grep nginx
```

### Restart API Server
```bash
pkill -f api_server.py
cd /Users/fseeru001/Documents/ClientEngagements/PoC/MoHRE/cge_model
python3 api_server.py > logs/api.log 2>&1 &
```

### Reload Nginx Config
```bash
sudo /opt/homebrew/opt/nginx/bin/nginx -s reload
```

### Stop Everything
```bash
# Stop API server
pkill -f api_server.py

# Stop nginx
sudo /opt/homebrew/opt/nginx/bin/nginx -s stop
```

## Test API Endpoints

### Health Check
```bash
curl http://localhost:8080/health
```

### Run Scenario
```bash
curl -X POST http://localhost:8080/api/run-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "test_scenario",
    "shocks": {
      "emirati_employment": 1.15
    }
  }'
```

### Chat Endpoint
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What if Emirati employment increases by 15%?"
  }'
```

## Nginx Features

- ✅ Reverse proxy to FastAPI
- ✅ Extended timeouts (300s) for long-running simulations
- ✅ Large file uploads (50MB max)
- ✅ Proper headers (X-Real-IP, X-Forwarded-For, etc.)
- ✅ WebSocket support (ready for future use)
- ✅ Access and error logging

## Troubleshooting

### API not responding
1. Check if API server is running: `ps aux | grep api_server`
2. Check API logs: `tail -f logs/api.log`
3. Test direct access: `curl http://localhost:8000/health`

### Nginx not proxying
1. Check nginx is running: `ps aux | grep nginx`
2. Check nginx config: `sudo /opt/homebrew/opt/nginx/bin/nginx -t`
3. Check nginx error logs: `tail -f /opt/homebrew/var/log/nginx/cge_api_error.log`

### Port conflicts
- Nginx uses port 8080 (Homebrew default)
- API uses port 8000 (internal)
- If 8080 is in use, edit `nginx_cge_api.conf` and change `listen 8080;`

## Next Steps

1. ✅ Local setup complete
2. 🔄 Test all API endpoints via Swagger UI
3. 🚀 When ready, deploy to OCI (we can revisit the OCI setup later)

Enjoy your local CGE Model API! 🎉
