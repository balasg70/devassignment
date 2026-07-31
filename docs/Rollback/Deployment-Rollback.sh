# Step 1: Swap slots back
az webapp deployment slot swap \
  --name petclinic-app \
  --resource-group petclinic-rg \
  --slot staging \
  --target-slot production

# Step 2: Validate
az webapp show \
  --name petclinic-app \
  --resource-group petclinic-rg \
  --query "state"