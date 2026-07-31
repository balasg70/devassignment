#!/bin/bash
# Configuration script for containerized agent

set -e

echo "Configuring Azure DevOps agent..."

# Configure agent
./config.sh --unattended \
    --url $AZP_URL \
    --auth pat \
    --token $AZP_TOKEN \
    --pool $AZP_POOL_NAME \
    --agent $AZP_AGENT_NAME \
    --work _work \
    --replace \
    --acceptTeeEula

echo "Starting agent..."
./run.sh --once