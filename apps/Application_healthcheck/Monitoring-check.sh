# Check Application Insights
az monitor app-insights metrics show --metric "availabilityResults/count"
# Verify Log Analytics queries
az monitor log-analytics query --workspace-id <workspace-id>