# Run smoke tests
curl https://petclinic-app.azurecontainerapps.io/actuator/health

# Validate monitoring
az monitor app-insights query -a <app-insights-id>

# Check secrets in Key Vault
az keyvault secret list --vault-name petclinic-kv

# Verify security scanning reports
az acr check-health --name petclinicacr