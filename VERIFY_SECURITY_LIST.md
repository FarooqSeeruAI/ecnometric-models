# Verify Security List for Your Subnet

## Your Network Details
- **VCN:** `momah-dev-vcn`
- **Subnet:** `momah-dev-vcn-public-subnet`
- **No NSGs** (good - one less thing to configure!)

## Next Step: Verify Security List

Since you don't have NSGs, the Security List rule should work. Let's verify it's on the correct Security List:

### Step 1: Go to Your Subnet
1. **Click on the subnet link** in your VNIC table: `momah-dev-vcn-public-subnet`
   - Or go to: **Networking** → **Virtual Cloud Networks** → `momah-dev-vcn` → **Subnets** → `momah-dev-vcn-public-subnet`

### Step 2: Check Security Lists Tab
1. On the subnet page, click **Security Lists** tab
2. You'll see which Security List(s) are attached to this subnet
3. **Note the Security List name(s)**

### Step 3: Verify the Rule
1. Click on the Security List name
2. Go to **Ingress Rules** tab
3. **Verify** you see a rule for port 8000:
   - Source: `0.0.0.0/0`
   - Protocol: TCP
   - Port: `8000`
   - Description: "CGE Model API" (or similar)

### Step 4: If Rule is Missing
If the rule is NOT on the Security List attached to `momah-dev-vcn-public-subnet`:
1. Add the Ingress Rule to that Security List
2. Wait 2-3 minutes for propagation
3. Test again: `curl http://80.225.77.244:8000/health`

## Quick Test

After verifying, test from your local machine:

```bash
curl -v http://80.225.77.244:8000/health
```

## Common Issue

If you added the rule to a **different Security List** (not the one attached to your subnet), it won't work. Make sure the rule is on the Security List that's actually attached to `momah-dev-vcn-public-subnet`.
