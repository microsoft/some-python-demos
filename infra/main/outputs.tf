output "openai_endpoint" {
  description = "Azure OpenAI endpoint URL for the /responses API."
  value       = azurerm_cognitive_account.openai.endpoint
}

output "deployment_name" {
  description = "Name of the gpt-4o model deployment."
  value       = azurerm_cognitive_deployment.gpt4o.name
}

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "ai_foundry_hub_name" {
  value = azurerm_ai_foundry.main.name
}

output "ai_foundry_project_name" {
  value = azurerm_ai_foundry_project.main.name
}
