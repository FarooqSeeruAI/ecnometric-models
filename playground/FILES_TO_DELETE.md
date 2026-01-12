# Files to Delete - Temporary/Unnecessary Files

## Summary
This document lists files that are temporary, one-time fixes, or no longer needed.

## Files to Delete

### 1. Temporary/Troubleshooting Scripts (One-time fixes)
- `troubleshoot-502.sh` - One-time troubleshooting script for 502 errors
- `fix-502.sh` - One-time fix script
- `fix-nginx-502.sh` - One-time nginx fix script
- `deploy-async-fix.sh` - One-time async deployment fix
- `test-async-endpoint.sh` - Temporary test script (functionality now in test-cache.sh)
- `test-end-to-end.sh` - Temporary test script

### 2. OCI-Related Files (Not using OCI, using AWS)
- `deploy_oci.sh` - OCI deployment script
- `deploy_to_oci.sh` - OCI deployment script (duplicate)
- `upload_to_oci.sh` - OCI upload script
- `OCI_DEPLOYMENT.md` - OCI deployment documentation
- `DEPLOYMENT_STATUS.md` - Outdated deployment status

### 3. Troubleshooting Documentation (One-time fixes, now resolved)
- `FINAL_TROUBLESHOOT.md` - One-time troubleshooting guide
- `FIND_VCN.md` - OCI-specific troubleshooting
- `FIX_ACCESS.md` - One-time access fix documentation
- `TROUBLESHOOT_ACCESS.md` - Access troubleshooting (duplicate)
- `CHECK_ROUTE_TABLE.md` - OCI-specific route table check
- `VERIFY_SECURITY_LIST.md` - OCI-specific security verification

### 4. Ngrok Files (Not using ngrok)
- `ngrok_fix.md` - Ngrok troubleshooting
- `ngrok_info.md` - Ngrok information
- `NGROK_SETUP.md` - Ngrok setup guide
- `start_with_ngrok.sh` - Ngrok startup script

### 5. Local Setup Files (Using AWS deployment, not local)
- `LOCAL_NGINX_SETUP.md` - Local nginx setup
- `start_local.sh` - Local startup script
- `start_local_with_nginx.sh` - Local nginx startup script

### 6. Temporary Output Files (In root directory - should be in outputs/)
- `base.xlsx` - Model output (1.4 MB) - should be in outputs/
- `policy.xlsx` - Model output (1.4 MB) - should be in outputs/
- `summary.xlsx` - Model output (75 KB) - should be in outputs/

### 7. Log Files
- `logs/api.log` - Application log file

### 8. Python Cache Files
- `ENV_new/` - Virtual environment directory (should use .venv or venv)
- All `__pycache__/` directories
- All `*.pyc` files

### 9. System Files
- `.DS_Store` - macOS system file

### 10. Duplicate/Redundant Files
- `swagger_test_payloads.json` - Redundant (all scenarios now in SWAGGER_TEST_GUIDE.md)
- `example_payloads.json` - Might be duplicate of swagger_test_payloads.json

### 11. Outdated/Redundant Documentation
- `DEPLOY_NOW.md` - Outdated deployment instructions
- `API_READY.md` - Outdated status document
- `SECURITY_NOTICE.md` - If no longer relevant

## Files to KEEP (Important)
- `test-cache.sh` - Useful for testing caching
- `check-scenario.sh` - Useful for checking scenarios
- `deploy-to-ec2.sh` - Active deployment script
- `check-aws-server.sh` - Useful for AWS monitoring
- `check-aws-files.sh` - Useful for file verification
- `monitor-scenario.sh` - Useful for monitoring
- `submit-and-monitor.sh` - Useful workflow script
- `get-scenario-results.sh` - Useful helper script
- All core Python files (api_server.py, solver.py, etc.)
- All documentation files (SWAGGER_TEST_GUIDE.md, CACHING.md, etc.)
- Configuration files (default.yml, docker-compose.yml, etc.)

## Total Files to Delete: ~35-40 files
