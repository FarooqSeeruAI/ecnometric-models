# Deployment Status ✅

## Current Status

**Instance IP:** `80.225.77.244`  
**Status:** ✅ **DEPLOYED & RUNNING**

### What's Done

1. ✅ SSH connection established
2. ✅ Repository cloned from GitHub
3. ✅ Dependencies installed (Python, packages)
4. ✅ API server started and running
5. ✅ Firewall configured (port 8000 open)

### API Server

- **Process:** Running (PID 22217)
- **Port:** 8000
- **Status:** Active

## Access URLs

### Internal (from within OCI network)
- http://10.0.1.64:8000/docs
- http://10.0.1.64:8000/openapi.json

### External (from internet) - **REQUIRES OCI SECURITY RULE**
- http://80.225.77.244:8000/docs
- http://80.225.77.244:8000/openapi.json

## ⚠️ IMPORTANT: Configure OCI Security Rules

To access the API from the internet, you **must** add a security rule:

1. Go to **OCI Console** → **Networking** → **Security Lists**
2. Find the Security List for your instance's subnet
3. Click **Add Ingress Rules**
4. Add:
   - **Source Type:** CIDR
   - **Source CIDR:** `0.0.0.0/0` (or specific IPs)
   - **IP Protocol:** TCP
   - **Destination Port Range:** `8000`
   - **Description:** "CGE Model API"

## Verify Deployment

### Check server status:
```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
cd ~/ecnometric-models
ps aux | grep api_server
tail -f logs/api.log
```

### Test API locally (from instance):
```bash
curl http://localhost:8000/docs
```

### Test API externally (after security rule):
```bash
curl http://80.225.77.244:8000/openapi.json
```

## API Endpoints

Once accessible, you can use:

- **Swagger UI:** http://80.225.77.244:8000/docs
- **OpenAPI Spec:** http://80.225.77.244:8000/openapi.json
- **Health Check:** http://80.225.77.244:8000/health
- **Run Scenario:** POST http://80.225.77.244:8000/api/run-scenario
- **Chat:** POST http://80.225.77.244:8000/api/chat

## Troubleshooting

**Can't access from internet:**
- ✅ Check OCI Security Lists (add port 8000 rule)
- ✅ Verify firewall: `sudo ufw status`
- ✅ Check server logs: `tail -f ~/ecnometric-models/logs/api.log`

**Server not running:**
```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
cd ~/ecnometric-models
export PATH=$HOME/.local/bin:$PATH
python3 api_server.py
```

**Restart server:**
```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
cd ~/ecnometric-models
pkill -f api_server.py
export PATH=$HOME/.local/bin:$PATH
nohup python3 api_server.py > logs/api.log 2>&1 &
```
