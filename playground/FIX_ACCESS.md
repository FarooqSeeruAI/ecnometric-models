# Fix: "Connection Refused" Error

## Problem
You're seeing: **"80.225.77.244 refused to connect"** when accessing `http://80.225.77.244:8000/docs`

## Root Cause
The OCI Security List is blocking incoming traffic on port 8000. The server is running, but OCI's network firewall is preventing external access.

## Solution: Add OCI Security List Rule

### Step-by-Step Instructions

1. **Log into OCI Console**
   - Go to: https://cloud.oracle.com/
   - Navigate to your instance

2. **Find Your Instance's Subnet**
   - Go to: **Compute** → **Instances**
   - Click on your instance: "ecnometric Model MOHRE"
   - Under **Primary VNIC**, note the **Subnet** name

3. **Open Security Lists**
   - Go to: **Networking** → **Virtual Cloud Networks**
   - Click on your VCN
   - Click **Security Lists** in the left menu
   - Find the Security List associated with your instance's subnet

4. **Add Ingress Rule**
   - Click on the Security List
   - Click **Add Ingress Rules** button
   - Fill in:
     ```
     Stateless: No
     Source Type: CIDR
     Source CIDR: 0.0.0.0/0
     IP Protocol: TCP
     Source Port Range: (leave blank)
     Destination Port Range: 8000
     Description: CGE Model API Access
     ```
   - Click **Add Ingress Rules**

5. **Wait 10-30 seconds** for the rule to propagate

6. **Test Again**
   - Try: http://80.225.77.244:8000/docs
   - Should now work! ✅

## Alternative: More Secure Rule

If you want to restrict access to specific IPs:

- **Source CIDR:** `YOUR_IP/32` (replace YOUR_IP with your actual IP)
- To find your IP: https://whatismyipaddress.com/

## Verify Server is Running

If you want to confirm the server is working:

```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
cd ~/ecnometric-models
curl http://localhost:8000/health
```

This should return: `{"status":"healthy"}`

## Quick Test Commands

After adding the security rule, test from your local machine:

```bash
# Test health endpoint
curl http://80.225.77.244:8000/health

# Test OpenAPI spec
curl http://80.225.77.244:8000/openapi.json | head -20

# Open in browser
open http://80.225.77.244:8000/docs
```

## Still Not Working?

1. **Check Security List Rule:**
   - Verify the rule was saved
   - Check it's for the correct subnet

2. **Check Instance Firewall:**
   ```bash
   ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
   sudo ufw status
   ```
   Should show: `8000/tcp ALLOW`

3. **Check Server is Running:**
   ```bash
   ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
   ps aux | grep api_server
   ```

4. **Check Server Logs:**
   ```bash
   ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
   cd ~/ecnometric-models
   tail -50 logs/api.log
   ```

## Visual Guide

The Security List rule should look like this:

```
┌─────────────────────────────────────────┐
│ Ingress Rules                           │
├─────────────────────────────────────────┤
│ Source      │ Protocol │ Port │ Action  │
├─────────────────────────────────────────┤
│ 0.0.0.0/0   │ TCP      │ 8000 │ Allow   │
└─────────────────────────────────────────┘
```
