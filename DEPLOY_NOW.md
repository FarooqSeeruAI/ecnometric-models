# Quick Deployment to OCI

## Prerequisites
✅ SSH keys are in `keys/` folder
✅ Private key permissions set (600)

## Step 1: Get OCI Instance IP

From OCI Console, get your instance's **Public IP address**.

## Step 2: Deploy

Run the deployment script:

```bash
cd /Users/fseeru001/Documents/ClientEngagements/PoC/MoHRE/cge_model
./deploy_to_oci.sh <YOUR_INSTANCE_IP>
```

Example:
```bash
./deploy_to_oci.sh 129.213.45.67
```

## What the Script Does

1. ✅ Tests SSH connection
2. ✅ Installs git
3. ✅ Clones repository from GitHub
4. ✅ Runs deployment (installs dependencies)
5. ✅ Configures firewall
6. ✅ Provides next steps

## Manual Deployment (Alternative)

If you prefer to do it manually:

```bash
# 1. SSH into instance
ssh -i keys/ssh-key-2026-01-11.key ubuntu@<INSTANCE_IP>

# 2. Clone repository
git clone https://github.com/FarooqSeeruAI/ecnometric-models.git
cd ecnometric-models

# 3. Run quick deployment
chmod +x quick_deploy.sh
./quick_deploy.sh

# 4. Start API server
python3 api_server.py
```

## After Deployment

1. **Configure OCI Security Rules:**
   - OCI Console → Networking → Security Lists
   - Add Ingress Rule: TCP port 8000

2. **Access API:**
   - http://<INSTANCE_IP>:8000/docs
   - http://<INSTANCE_IP>:8000/openapi.json

3. **Run in Background:**
   ```bash
   nohup python3 api_server.py > logs/api.log 2>&1 &
   ```

## Troubleshooting

**Connection refused:**
- Check OCI Security Lists allow port 22 (SSH)
- Verify instance is running
- Check public IP is correct

**Permission denied:**
- Verify key permissions: `chmod 600 keys/ssh-key-2026-01-11.key`
- Check if public key is added to instance

**Port 8000 not accessible:**
- Add Security List rule for port 8000
- Check firewall: `sudo ufw status`
