# Rollback Plan
## Emergency Procedures for Migration Failure

### Rollback Triggers

**Critical Failures Requiring Immediate Rollback:**
1. Application unavailable > 5 minutes
2. Data loss or corruption detected
3. Security breach or vulnerability identified
4. Performance degradation > 50%
5. Critical business function failure
6. Major dependency failure (database, API)

**Non-Critical Rollback Triggers:**
1. Pipeline failure with manual intervention
2. Minor performance degradation
3. User-reported issues (non-critical)
4. Monitoring alerts (non-critical)

### Rollback Procedures

#### 1. Application Rollback (Azure Container Apps)

**Method A: Container App Revision Rollback**
```bash
# Step 1: Identify previous working revision
az containerapp revision list \
  --name petclinic-app \
  --resource-group petclinic-rg \
  --query "[?active==false].name"

# Step 2: Activate previous revision
az containerapp revision activate \
  --name <previous-revision> \
  --resource-group petclinic-rg

# Step 3: Verify rollback
az containerapp show \
  --name petclinic-app \
  --resource-group petclinic-rg \
  --query "properties.configuration.activeRevisionsMode"

# Step 4: Deactivate failed revision
az containerapp revision deactivate \
  --name <failed-revision> \
  --resource-group petclinic-rg

# Step 5: Verify health
curl -f https://petclinic-app.azurecontainerapps.io/actuator/health