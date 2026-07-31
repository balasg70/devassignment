# Step 1: Identify last working commit
git log --oneline --grep="successful deployment"

# Step 2: Revert changes
git revert <failed-commit-hash>
git push

# Step 3: Trigger rollback pipeline
az pipelines build queue \
  --definition-name petclinic-pipeline \
  --variables "ROLLBACK=true"

# Revert pipeline YAML changes
#git revert <commit-hash>

# Disable problematic pipeline
#az pipelines build queue --id <pipeline-id> --status canceled

# Restore from artifact backup
#az acr repository import --name petclinicacr --image <image-name>