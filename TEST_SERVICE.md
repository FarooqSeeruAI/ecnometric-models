# CGE Model Service - Testing & Status

## ✅ Fixed Issues

1. **Database file missing** - Uploaded `database/oranignm.xlsx` ✅
2. **Closure files missing** - Uploaded all `closures/*.txt` files ✅
3. **Container restarted** - Service is running ✅

## Current Status

- **Service URL**: http://13.203.193.142
- **Swagger UI**: http://13.203.193.142/docs
- **Health Check**: http://13.203.193.142/health
- **Container**: Running and healthy
- **Files**: All required files uploaded

## Quick Test Commands

### 1. Health Check
```bash
curl http://13.203.193.142/health
```

### 2. Run Simple Test Scenario
```bash
curl -X POST http://13.203.193.142/api/v1/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "test_simple",
    "year": 2023,
    "steps": 1,
    "shocks": {
      "realgdp": 1.0
    }
  }'
```

### 3. Check Scenario Status
```bash
# Replace SCENARIO_ID with the ID from step 2
curl http://13.203.193.142/api/v1/scenarios/SCENARIO_ID/status
```

### 4. Get Results (after completion)
```bash
curl http://13.203.193.142/api/v1/scenarios/SCENARIO_ID/results
```

## Common Issues & Solutions

### Issue: 502 Bad Gateway
**Solution**: Container may have crashed. Restart it:
```bash
ssh -i pem/ecnometric_model.pem ubuntu@13.203.193.142 "docker restart cge-model-api"
```

### Issue: Missing files error
**Solution**: Files are mounted as volumes. Ensure files exist on host:
```bash
ssh -i pem/ecnometric_model.pem ubuntu@13.203.193.142 "ls -la ~/cge_model/database/oranignm.xlsx ~/cge_model/closures/base2023.txt"
```

### Issue: Scenario fails with file errors
**Solution**: Check container can see files:
```bash
ssh -i pem/ecnometric_model.pem ubuntu@13.203.193.142 "docker exec cge-model-api ls -la /app/database/oranignm.xlsx /app/closures/base2023.txt"
```

## Monitoring

### Check Container Logs
```bash
ssh -i pem/ecnometric_model.pem ubuntu@13.203.193.142 "docker logs cge-model-api --tail 50"
```

### Check for Errors
```bash
ssh -i pem/ecnometric_model.pem ubuntu@13.203.193.142 "docker logs cge-model-api 2>&1 | grep -i error | tail -20"
```

### Check Container Status
```bash
ssh -i pem/ecnometric_model.pem ubuntu@13.203.193.142 "docker ps | grep cge-model-api"
```

## Files Required

- ✅ `orani.model` - Model definition
- ✅ `default.yml` - Configuration
- ✅ `database/oranignm.xlsx` - Input data
- ✅ `closures/base*.txt` - Base closure files (2023-2040)
- ✅ `closures/pol*.txt` - Policy closure files (2023-2040)

## Next Steps

1. Test a simple scenario via Swagger UI
2. Monitor logs for any runtime errors
3. Verify results are generated correctly
4. Test with different shock values
