# Check main application
curl -f https://petclinic-app.azurecontainerapps.io/
# Check health endpoint
curl -f https://petclinic-app.azurecontainerapps.io/actuator/health
# Check metrics
curl -f https://petclinic-app.azurecontainerapps.io/actuator/metrics