# Migration Runbook
## CI/CD Toolchain Migration from Jenkins/Bamboo/GitLab to Azure DevOps

### Pre-Migration Checklist

- [ ] All application repositories forked/cloned
- [ ] Containerization completed for all applications
- [ ] Azure infrastructure provisioned (ACR, Key Vault, Container Apps)
- [ ] Self-hosted agent configured and tested
- [ ] Pipeline templates created and validated
- [ ] Service connections created with OIDC
- [ ] Security scanning tools configured
- [ ] Monitoring and alerts configured
- [ ] Jira Cloud migration prepared
- [ ] Rollback plan documented
- [ ] Hypercare team identified

### Migration Execution

#### 1. Infrastructure Setup (Day 1)
```bash
# Deploy Azure resources
az deployment group create \
  --resource-group petclinic-rg \
  --template-file iac/bicep/main.bicep \
  --parameters environment=dev

# Setup self-hosted agent
./self-hosted-agent/setup-agent.sh

# Verify agent registration in Azure DevOps
az pipelines agent list --pool-name "ado-selfhosted-linux"