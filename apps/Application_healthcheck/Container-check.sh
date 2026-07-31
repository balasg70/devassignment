# Check Container App status
az containerapp show --name petclinic-app --resource-group petclinic-rg
# Check container logs
az containerapp logs show --name petclinic-app --resource-group petclinic-rg