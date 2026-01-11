# Final Troubleshooting Steps

## Current Status
✅ Security List rule configured (port 8000)
✅ Route table has Internet Gateway route
✅ Server running and binding to 0.0.0.0:8000
✅ Firewall (ufw) allows port 8000
✅ iptables shows ACCEPT for port 8000
❌ Connection still refused from external network

## Remaining Checks

### 1. Check Subnet-Level Network Security Groups

NSGs can be attached at the **subnet level** (not just VNIC level):

1. Go to: **Networking** → **Virtual Cloud Networks** → `momah-dev-vcn`
2. Click **Subnets** → `momah-dev-vcn-public-subnet`
3. Look for **Network Security Groups** section
4. If NSGs are listed, click on them
5. Add Ingress Rule for port 8000 (same as Security List)

### 2. Verify Internet Gateway is Enabled

1. Go to: **Networking** → **Virtual Cloud Networks** → `momah-dev-vcn`
2. Click **Internet Gateways** (left menu)
3. Find your Internet Gateway
4. Verify it shows **"Available"** status (green)
5. If it's disabled, enable it

### 3. Check Public IP Association

1. Go to: **Compute** → **Instances** → "ecnometric Model MOHRE"
2. Scroll to **Primary VNIC**
3. Verify **Public IP** shows: `80.225.77.244`
4. If it shows "No Public IP", you need to assign one

### 4. Restart the API Server

Sometimes a restart helps pick up network changes:

```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
cd ~/ecnometric-models
pkill -f api_server.py
export PATH=$HOME/.local/bin:$PATH
nohup python3 api_server.py > logs/api.log 2>&1 &
sleep 3
tail -20 logs/api.log
```

### 5. Test from Inside the Instance

Verify the server responds to the public IP from inside:

```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
curl http://80.225.77.244:8000/health
```

If this works but external access doesn't, it's definitely a network routing/firewall issue.

## Most Likely Remaining Issues

1. **Subnet-level NSG** - Check if NSGs are attached to the subnet itself
2. **Internet Gateway disabled** - Verify it's enabled
3. **Propagation delay** - Sometimes OCI changes take 5-10 minutes to fully propagate

## Quick Test After Changes

```bash
curl -v http://80.225.77.244:8000/health
```

If it still doesn't work, try waiting 5-10 minutes and test again - OCI network changes can take time to propagate.
