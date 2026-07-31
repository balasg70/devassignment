# List revisions
az containerapp revision list --name petclinic-app --resource-group petclinic-rg

# Activate previous revision
az containerapp revision activate --revision <revision-name>

# Verify health after rollback
curl -f https://petclinic-app.azurecontainerapps.io/actuator/health