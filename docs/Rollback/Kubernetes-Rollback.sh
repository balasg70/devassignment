# Step 1: Undo deployment
kubectl rollout undo deployment/petclinic-app -n petclinic

# Step 2: Monitor rollout status
kubectl rollout status deployment/petclinic-app -n petclinic

# Step 3: Verify pods
kubectl get pods -n petclinic -l app=petclinic

# Step 4: Check service
kubectl get svc petclinic-service -n petclinic