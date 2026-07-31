#!/bin/bash
# Script to set up Azure DevOps self-hosted agent on Ubuntu Linux

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}Azure DevOps Self-Hosted Agent Setup${NC}"
echo -e "${GREEN}===========================================${NC}"

# Variables - MODIFY THESE
AZP_URL="https://dev.azure.com/your-organization"
AZP_TOKEN="your-personal-access-token"
AZP_AGENT_NAME="linux-agent-$(hostname)"
AZP_POOL_NAME="ado-selfhosted-linux"
AZP_WORK="_work"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    curl \
    git \
    wget \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    openjdk-17-jdk \
    maven \
    docker.io \
    docker-compose \
    jq

# Install Azure CLI
echo -e "${YELLOW}Installing Azure CLI...${NC}"
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install kubectl
echo -e "${YELLOW}Installing kubectl...${NC}"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Helm
echo -e "${YELLOW}Installing Helm...${NC}"
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Install Trivy
echo -e "${YELLOW}Installing Trivy vulnerability scanner...${NC}"
wget https://github.com/aquasecurity/trivy/releases/download/v0.40.0/trivy_0.40.0_Linux-64bit.deb
sudo dpkg -i trivy_0.40.0_Linux-64bit.deb

# Install Terraform
echo -e "${YELLOW}Installing Terraform...${NC}"
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform

# Configure Docker to run without sudo
echo -e "${YELLOW}Configuring Docker...${NC}"
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Download and configure Azure DevOps agent
echo -e "${YELLOW}Downloading Azure DevOps agent...${NC}"
mkdir -p ~/azp-agent
cd ~/azp-agent

# Download the latest agent
AGENT_VERSION=$(curl -s https://api.github.com/repos/microsoft/azure-pipelines-agent/releases/latest | grep tag_name | cut -d '"' -f 4)
wget "https://github.com/microsoft/azure-pipelines-agent/releases/download/${AGENT_VERSION}/vsts-agent-linux-x64-${AGENT_VERSION}.tar.gz"
tar -xzf vsts-agent-linux-x64-${AGENT_VERSION}.tar.gz

# Configure the agent
echo -e "${YELLOW}Configuring Azure DevOps agent...${NC}"
./config.sh --unattended \
    --url $AZP_URL \
    --auth pat \
    --token $AZP_TOKEN \
    --pool $AZP_POOL_NAME \
    --agent $AZP_AGENT_NAME \
    --work $AZP_WORK \
    --replace \
    --acceptTeeEula

# Create systemd service
echo -e "${YELLOW}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/azp-agent.service > /dev/null <<EOF
[Unit]
Description=Azure DevOps Agent
After=network.target docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/azp-agent
ExecStart=/home/$USER/azp-agent/run.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable azp-agent.service
sudo systemctl start azp-agent.service

echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}Azure DevOps agent setup complete!${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo -e "${GREEN}Agent running as service: azp-agent${NC}"
echo -e "${GREEN}Check status: sudo systemctl status azp-agent${NC}"
echo -e "${GREEN}View logs: sudo journalctl -u azp-agent -f${NC}"
echo ""
echo -e "${YELLOW}NOTE: You may need to log out and back in for Docker group changes to take effect.${NC}"
echo -e "${YELLOW}NOTE: Update the variables at the top of this script before running.${NC}"