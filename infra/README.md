# infra

Infrastructure required to accomplish relevant demonstrations. Note: not Python code!

## Architecture

Two Terraform root modules, deployed in order:

| Module      | Purpose                                                        |
|-------------|----------------------------------------------------------------|
| `bootstrap` | Resource group and storage account for remote Terraform state  |
| `main`      | AI Foundry hub, project, Azure OpenAI deployment, and RBAC     |

The `main` module provisions:

* Azure OpenAI cognitive account with **key-based access disabled** (`local_auth_enabled = false`)
* A `gpt-4o` (GlobalStandard) deployment that supports the `/responses` API
* AI Foundry hub and project (with Key Vault and Storage Account dependencies)
* `Cognitive Services OpenAI User` role assignment for the deploying principal

Access the model from Python using `DefaultAzureCredential` against the `openai_endpoint` output.

## Requirements

* `tf` >= 1.9 — <https://developer.hashicorp.com/terraform/install>
* `az` CLI — <https://learn.microsoft.com/cli/azure/install-azure-cli>
* AzureRM provider ~> 4.0

## Quickstart

```shell
az login

# 1. Bootstrap state storage (uses local state)
cd bootstrap
terraform init
terraform apply -var="subscription_id=<YOUR_SUBSCRIPTION_ID>"

# 2. Deploy AI Foundry infrastructure (uses remote state)
cd ../main
terraform init
terraform apply -var="subscription_id=<YOUR_SUBSCRIPTION_ID>"
```

Note you can write a `main/terraform.tfvars` file like so to avoid having to re-enter your subscription:

```shell
subscription_id = "<YOUR_SUBSCRIPTION_ID>"
```

Both modules accept these variables:

| Variable          | Default    | Description                |
|-------------------|------------|----------------------------|
| `subscription_id` | (required) | Azure subscription ID      |
| `location`        | `eastus2`  | Azure region for resources |
| `prefix`          | `pydemos`  | Naming prefix              |

> [!IMPORTANT]
> If you change `prefix` in the bootstrap module, update the hardcoded backend
> block in `main/main.tf` to match the new storage account and resource group names.
