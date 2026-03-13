terraform {
  required_version = ">= 1.9"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-pydemos-tfstate"
    storage_account_name = "stpydemostfstate"
    container_name       = "tfstate"
    key                  = "main.tfstate"
    use_azuread_auth     = true
  }
}

provider "azurerm" {
  features {}
  subscription_id      = var.subscription_id
  storage_use_azuread  = true
}

variable "subscription_id" {
  type        = string
  description = "Azure subscription ID."
}

variable "location" {
  type        = string
  default     = "eastus2"
  description = "Azure region for resources."
}

variable "prefix" {
  type        = string
  default     = "pydemos"
  description = "Naming prefix for all resources."
}

data "azurerm_client_config" "current" {}

# ---------------------------------------------------------------------------
# Resource group
# ---------------------------------------------------------------------------

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.prefix}"
  location = var.location
}

# ---------------------------------------------------------------------------
# Dependencies for AI Foundry Hub
# ---------------------------------------------------------------------------

resource "azurerm_key_vault" "main" {
  name                      = "kv-${var.prefix}"
  location                  = azurerm_resource_group.main.location
  resource_group_name       = azurerm_resource_group.main.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  purge_protection_enabled   = false
}

resource "azurerm_storage_account" "main" {
  name                            = "st${var.prefix}"
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
}

# ---------------------------------------------------------------------------
# Azure OpenAI (key-based access disabled)
# ---------------------------------------------------------------------------

resource "azurerm_cognitive_account" "openai" {
  name                  = "oai-${var.prefix}"
  location              = azurerm_resource_group.main.location
  resource_group_name   = azurerm_resource_group.main.name
  kind                  = "OpenAI"
  sku_name              = "S0"
  local_auth_enabled    = false
  custom_subdomain_name = "oai-${var.prefix}"
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  rai_policy_name      = "Microsoft.DefaultV2" 

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 10
  }
}

# ---------------------------------------------------------------------------
# AI Foundry Hub & Project
# ---------------------------------------------------------------------------

resource "azurerm_ai_foundry" "main" {
  name                   = "hub-${var.prefix}"
  location               = azurerm_resource_group.main.location
  resource_group_name    = azurerm_resource_group.main.name
  storage_account_id     = azurerm_storage_account.main.id
  key_vault_id           = azurerm_key_vault.main.id
  public_network_access  = "Disabled"

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_ai_foundry_project" "main" {
  name                = "proj-${var.prefix}"
  location            = azurerm_ai_foundry.main.location
  ai_services_hub_id  = azurerm_ai_foundry.main.id

  identity {
    type = "SystemAssigned"
  }
}

# ---------------------------------------------------------------------------
# Application Insights (workspace-based)
# ---------------------------------------------------------------------------

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "main" {
  name                = "appi-${var.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
}

# ---------------------------------------------------------------------------
# RBAC – grant the deploying principal OpenAI access
# ---------------------------------------------------------------------------

resource "azurerm_role_assignment" "openai_user" {
  scope                = azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = data.azurerm_client_config.current.object_id
}
