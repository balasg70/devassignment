# Terraform configuration for Azure infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "petclinic"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

locals {
  resource_name_prefix = "${var.project_name}${var.environment}"
  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${local.resource_name_prefix}-rg"
  location = var.location
  tags     = local.tags
}

# Container Registry
resource "azurerm_container_registry" "acr" {
  name                = replace("${local.resource_name_prefix}acr", "-", "")
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"
  admin_enabled       = false
  tags                = local.tags
}

# Key Vault
resource "azurerm_key_vault" "kv" {
  name                       = replace("${local.resource_name_prefix}kv", "-", "")
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  tags                       = local.tags
}

data "azurerm_client_config" "current" {}

# Key Vault Access Policy
resource "azurerm_key_vault_access_policy" "devops" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Purge"
  ]
}

# Key Vault Secrets (example - will be populated by pipeline)
resource "azurerm_key_vault_secret" "database_url" {
  name         = "database-url"
  value        = "jdbc:mysql://mysql-server.database.windows.net:3306/petclinic"
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "database_username" {
  name         = "database-username"
  value        = "petclinic@mysql-server"
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "database_password" {
  name         = "database-password"
  value        = "ChangeMe123!"
  key_vault_id = azurerm_key_vault.kv.id
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "la" {
  name                = "${local.resource_name_prefix}-la"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

# Application Insights
resource "azurerm_application_insights" "ai" {
  name                = "${local.resource_name_prefix}-ai"
  location            = azurerm_resource_group.main.location
  resource_group_name = azorerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.la.id
  application_type    = "web"
  tags                = local.tags
}

# Container Apps Environment
resource "azurerm_container_app_environment" "env" {
  name                       = "${local.resource_name_prefix}-env"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.la.id
  tags                       = local.tags
}

# Container App
resource "azurerm_container_app" "app" {
  name                         = "${local.resource_name_prefix}-app"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.tags

  template {
    containers {
      name   = "petclinic-app"
      image  = "${azurerm_container_registry.acr.login_server}/petclinic:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "SPRING_PROFILES_ACTIVE"
        value = "azure"
      }
      
      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
      
      env {
        name        = "DATABASE_USERNAME"
        secret_name = "database-username"
      }
      
      env {
        name        = "DATABASE_PASSWORD"
        secret_name = "database-password"
      }
    }

    scale {
      min_replicas = 1
      max_replicas = 10
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  secret {
    name  = "database-url"
    value = azurerm_key_vault_secret.database_url.value
  }
  
  secret {
    name  = "database-username"
    value = azurerm_key_vault_secret.database_username.value
  }
  
  secret {
    name  = "database-password"
    value = azurerm_key_vault_secret.database_password.value
  }
}

# Outputs
output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "acr_name" {
  value = azurerm_container_registry.acr.name
}

output "key_vault_name" {
  value = azurerm_key_vault.kv.name
}

output "container_app_url" {
  value = azurerm_container_app.app.ingress[0].fqdn
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.la.workspace_id
}

output "app_insights_connection_string" {
  value = azurerm_application_insights.ai.connection_string
  sensitive = true
}