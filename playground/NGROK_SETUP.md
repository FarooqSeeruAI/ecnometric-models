# Ngrok Setup for CGE Model API

Expose your FastAPI server to the internet using ngrok.

## Installation

1. **Install ngrok:**
   - Download from: https://ngrok.com/download
   - Or via Homebrew: `brew install ngrok`
   - Or via npm: `npm install -g ngrok`

2. **Sign up and get auth token:**
   - Sign up at: https://dashboard.ngrok.com/signup
   - Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
   - Configure: `ngrok config add-authtoken YOUR_TOKEN`

## Quick Start

### Option 1: Manual (Two Terminals)

**Terminal 1 - Start API Server:**
```bash
cd /Users/fseeru001/Documents/ClientEngagements/PoC/MoHRE/cge_model
python3 api_server.py
```

**Terminal 2 - Start ngrok:**
```bash
ngrok http 8000
```

### Option 2: Using the Script

```bash
chmod +x start_with_ngrok.sh
./start_with_ngrok.sh
```

### Option 3: Direct Command

```bash
# Start server in background
python3 api_server.py &

# Start ngrok
ngrok http 8000
```

## Ngrok Output

When ngrok starts, you'll see something like:

```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

## Access Your API

Once ngrok is running, you can access:

- **Public URL**: `https://abc123.ngrok-free.app`
- **Swagger UI**: `https://abc123.ngrok-free.app/docs`
- **ReDoc**: `https://abc123.ngrok-free.app/redoc`
- **OpenAPI JSON**: `https://abc123.ngrok-free.app/openapi.json`

## Example API Calls via Ngrok

```bash
# Replace YOUR_NGROK_URL with your actual ngrok URL
NGROK_URL="https://abc123.ngrok-free.app"

# Run scenario
curl -X POST "$NGROK_URL/api/v1/scenarios/run" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "test",
    "shocks": {
      "x1labiEmplWgt_EMIRATI": 15.0
    }
  }'

# Chat interface
curl -X POST "$NGROK_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What if Emirati employment increases by 15%?"
  }'
```

## Ngrok Web Interface

Ngrok provides a web interface to inspect requests:

- **Local**: http://localhost:4040
- View all requests, responses, and replay requests

## Advanced Options

### Custom Domain (Paid)

```bash
ngrok http 8000 --domain=your-custom-domain.ngrok.app
```

### Static Domain (Paid)

```bash
ngrok http 8000 --domain=static-cge-model.ngrok.app
```

### Authentication

```bash
ngrok http 8000 --basic-auth="username:password"
```

### Region Selection

```bash
ngrok http 8000 --region=us  # or eu, ap, au, sa, jp, in
```

## Security Notes

- Free ngrok URLs are public - anyone with the URL can access
- Consider adding authentication for production use
- Use ngrok's paid plans for custom domains and better security
- For production, use proper hosting (AWS, Azure, GCP)

## Troubleshooting

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

**Ngrok not found:**
```bash
# Check if ngrok is in PATH
which ngrok

# Add to PATH if needed
export PATH=$PATH:/path/to/ngrok
```

**Connection refused:**
- Make sure the FastAPI server is running on port 8000
- Check firewall settings
- Verify ngrok is pointing to correct port

## Production Deployment

For production, consider:

1. **Cloud hosting**: Deploy to AWS, Azure, or GCP
2. **Docker**: Containerize the application
3. **Reverse proxy**: Use nginx or similar
4. **SSL certificates**: Use Let's Encrypt
5. **Authentication**: Add API keys or OAuth

## Example Docker Setup

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then:
```bash
docker build -t cge-model-api .
docker run -p 8000:8000 cge-model-api
ngrok http 8000
```
