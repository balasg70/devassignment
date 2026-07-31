# Step 1: Identify latest good backup
az mysql flexible-server backup list \
  --server-name mysql-server \
  --resource-group petclinic-rg

# Step 2: Restore to new server
az mysql flexible-server restore \
  --name mysql-server-restored \
  --resource-group petclinic-rg \
  --source-server mysql-server \
  --backup-name <backup-id>

# Step 3: Point application to restored DB
# Update environment variable in Container App

# Step 4: Verify data
# Run data validation queries