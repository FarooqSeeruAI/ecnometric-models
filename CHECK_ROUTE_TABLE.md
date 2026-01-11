# Check Route Table and Internet Gateway

## Current Status
✅ Security List rule configured correctly (port 8000)
✅ Server running and listening
❌ Connection still refused from external network

## Possible Issue: Route Table Configuration

Your subnet is `momah-dev-vcn-public-subnet` and route table is `momah-dev-vcn-public-rt`. 

For external access to work, the route table must route traffic through an **Internet Gateway**.

## Check Route Table

1. **Go to your subnet:**
   - OCI Console → Networking → Virtual Cloud Networks
   - Click `momah-dev-vcn`
   - Click **Subnets**
   - Click `momah-dev-vcn-public-subnet`

2. **Check Route Table:**
   - On the subnet page, look at the **Route Table** field
   - It should show: `momah-dev-vcn-public-rt`
   - Click on the route table name

3. **Verify Internet Gateway Route:**
   - On the route table page, go to **Route Rules** tab
   - You should see a rule like:
     ```
     Target Type: Internet Gateway
     Destination CIDR Block: 0.0.0.0/0
     Description: Internet Gateway
     ```
   - If this rule is missing, external traffic won't work!

## If Internet Gateway Route is Missing

1. **Check if Internet Gateway exists:**
   - VCN → **Internet Gateways** (left menu)
   - If none exist, create one

2. **Add route to route table:**
   - Go to your route table: `momah-dev-vcn-public-rt`
   - Click **Add Route Rules**
   - Target Type: **Internet Gateway**
   - Destination CIDR Block: `0.0.0.0/0`
   - Target Internet Gateway: (select your Internet Gateway)
   - Description: "Internet Gateway"
   - Click **Add Route Rules**

## Alternative: Check Instance Firewall

Even though ufw is configured, let's double-check:

```bash
ssh -i keys/ssh-key-2026-01-11.key ubuntu@80.225.77.244
sudo iptables -L -n | grep 8000
```

Should show ACCEPT rules for port 8000.

## Quick Verification Checklist

- [ ] Security List rule exists (✅ Confirmed)
- [ ] Server is running (✅ Confirmed)
- [ ] Route table has Internet Gateway route (❓ Need to check)
- [ ] Internet Gateway exists and is enabled (❓ Need to check)
- [ ] Subnet is public (name suggests it is: `public-subnet`)

## Most Likely Issue

**Missing Internet Gateway route** - If the route table doesn't route `0.0.0.0/0` through an Internet Gateway, external traffic can't reach your instance.

Check the route table `momah-dev-vcn-public-rt` for an Internet Gateway route.
