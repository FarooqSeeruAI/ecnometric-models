# Troubleshooting: Connection Still Refused

## Current Status
- ✅ Security List rule added (port 8000)
- ✅ Server running on instance
- ❌ Connection refused from external network

## Possible Causes

### 1. Network Security Groups (NSGs)
OCI instances can have **Network Security Groups** in addition to Security Lists. NSGs take precedence over Security Lists.

**Check for NSGs:**
1. Go to OCI Console → **Compute** → **Instances**
2. Click your instance: "ecnometric Model MOHRE"
3. Scroll to **Primary VNIC** section
4. Look for **Network Security Groups** field
5. If NSGs are listed, click on them
6. Add Ingress Rule for port 8000 (same as Security List)

### 2. Security List Not Attached to Subnet
Verify the Security List is actually attached:
1. Go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN
3. Click **Subnets**
4. Click your subnet
5. Check **Security Lists** tab
6. Ensure your Security List is listed there

### 3. Rule Propagation Delay
Security rules can take **2-5 minutes** to fully propagate. Wait a bit longer and try again.

### 4. Wrong Security List
Make sure you added the rule to the Security List that's actually attached to your instance's subnet.

## Step-by-Step Verification

### Step 1: Verify Server is Running
```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
ps aux | grep api_server
curl http://localhost:8000/health
```

### Step 2: Check for Network Security Groups
1. OCI Console → Compute → Instances
2. Click "ecnometric Model MOHRE"
3. Primary VNIC → Check "Network Security Groups"
4. If present, add rule there too

### Step 3: Verify Security List Attachment
1. OCI Console → Networking → Virtual Cloud Networks
2. Your VCN → Subnets
3. Your subnet → Security Lists tab
4. Confirm your Security List is listed

### Step 4: Double-Check Security List Rule
1. Go to your Security List
2. Ingress Rules tab
3. Verify rule exists:
   - Source: `0.0.0.0/0`
   - Protocol: TCP
   - Port: `8000`

## Quick Fix: Add NSG Rule (If NSGs Exist)

If your instance has Network Security Groups:

1. **Find NSG:**
   - Instance → Primary VNIC → Network Security Groups
   - Click the NSG name

2. **Add Ingress Rule:**
   - Click **Add Ingress Rules**
   - Source Type: CIDR
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: TCP
   - Destination Port Range: `8000`
   - Description: "CGE Model API"

3. **Save and wait 1-2 minutes**

## Alternative: Check Instance Firewall

The instance firewall (ufw) is already configured, but let's verify:

```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
sudo ufw status
```

Should show: `8000/tcp ALLOW`

## Test Connection Again

After checking NSGs and waiting 2-3 minutes:

```bash
curl -v http://80.225.77.244:8000/health
```

## Most Likely Issue

**Network Security Groups (NSGs)** - If your instance uses NSGs, they override Security Lists. You must add the rule to the NSG as well.

Check your instance's Primary VNIC details to see if NSGs are configured.
