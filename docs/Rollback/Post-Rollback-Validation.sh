# 1. Check application health
curl -f https://petclinic-app.azurecontainerapps.io/actuator/health

# 2. Verify application functionality
# Perform critical business operations

# 3. Check application logs
az containerapp logs show \
  --name petclinic-app \
  --resource-group petclinic-rg

# 4. Verify monitoring
az monitor app-insights metrics show

# 5. Validate all integrations
# Check database connections
# Check API integrations
# Check user authentication