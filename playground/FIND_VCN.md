# How to Find Your VCN (Virtual Cloud Network)

## Method 1: From Your Instance (Easiest)

1. **Log into OCI Console**
   - Go to: https://cloud.oracle.com/
   - Sign in with your credentials

2. **Navigate to Your Instance**
   - Click the **☰ (Menu)** icon (top left)
   - Go to: **Compute** → **Instances**
   - Click on your instance: **"ecnometric Model MOHRE"**

3. **Find VCN Information**
   - Scroll down to the **Primary VNIC** section
   - You'll see:
     - **Subnet:** `subnet-name` (click this link)
     - **VCN:** `vcn-name` (this is your VCN!)
     - **Private IP:** `10.0.1.64`
     - **Public IP:** `80.225.77.244`

4. **Click on the Subnet or VCN link** to go directly to it

## Method 2: From Networking Menu

1. **Go to Networking**
   - Click **☰ (Menu)** icon
   - Go to: **Networking** → **Virtual Cloud Networks**

2. **Find Your VCN**
   - You'll see a list of all VCNs
   - Look for the VCN in your compartment
   - The VCN name might be something like:
     - `vcn-<region>-<name>`
     - `Default VCN for <compartment>`
     - Or a custom name you created

3. **Verify it's the right VCN**
   - Click on the VCN
   - Go to **Subnets** (left menu)
   - Check if your instance's subnet (from Method 1) is listed here

## Method 3: Using OCI CLI (If Installed)

If you have OCI CLI installed, you can find it via command line:

```bash
# Get instance details
oci compute instance get --instance-id <instance-ocid>

# Or list VCNs
oci network vcn list --compartment-id <compartment-ocid>
```

## Quick Visual Guide

```
OCI Console
│
├── ☰ Menu
│   │
│   ├── Compute → Instances
│   │   └── "ecnometric Model MOHRE"
│   │       └── Primary VNIC
│   │           ├── Subnet: [Click here]
│   │           └── VCN: [This is your VCN!]
│   │
│   └── Networking → Virtual Cloud Networks
│       └── [List of all VCNs]
│           └── [Your VCN] → Security Lists
```

## What You Need to Do Next

Once you find your VCN:

1. **Click on the VCN name**
2. **Click "Security Lists"** in the left menu
3. **Find the Security List** that matches your instance's subnet
4. **Click on that Security List**
5. **Click "Add Ingress Rules"**
6. **Add the rule for port 8000**

## Finding the Right Security List

The Security List name might be:
- `Default Security List for <vcn-name>`
- Or a custom name

To verify it's the right one:
- Check the **Subnets** tab in the Security List
- Your instance's subnet should be listed there

## Still Can't Find It?

If you're having trouble:

1. **From your instance page:**
   - Look at **Primary VNIC** → **Subnet**
   - Click the subnet link
   - This will show you the subnet details
   - The VCN is shown at the top of the subnet page

2. **Check your compartment:**
   - Make sure you're looking in the correct compartment
   - Your instance's compartment is shown on the instance details page

## Quick Reference

- **Instance:** `ecnometric Model MOHRE`
- **Public IP:** `80.225.77.244`
- **Private IP:** `10.0.1.64`
- **VCN:** (Find using methods above)
- **Security List:** (Associated with your subnet)
