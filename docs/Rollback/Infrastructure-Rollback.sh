# Step 1: Identify last stable configuration
# Use previous Bicep/Terraform state

# Step 2: Apply previous configuration
az deployment group create \
  --resource-group petclinic-rg \
  --template-file iac/bicep/main.bicep.bak \
  --parameters @parameters.bak.json

# Step 3: Validate infrastructure
az resource list --resource-group petclinic-rg