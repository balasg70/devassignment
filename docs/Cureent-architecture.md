# Architecture Documentation
## DevOps Migration - Azure DevOps & Jira Cloud

### Current State Architecture

**On-Premise Toolchain:**
- **CI/CD:** Jenkins, Bamboo, GitLab with self-managed runners
- **Source Control:** Mixed - GitLab, GitHub, Bitbucket
- **Work Management:** Jira Server/Data Center
- **Artifact Management:** Nexus/JFrog
- **Runtime:** VMware VMs
- **Deployment Method:** SSH scripts, manual processes

**Current Application Architecture:**