output "resource_group_name" {
  description = "Name of the VoltGrid Resource Group"
  value       = azurerm_resource_group.rg.name
}

output "eventhub_namespace_name" {
  description = "Azure Event Hub Namespace for VoltGrid"
  value       = azurerm_eventhub_namespace.hubns.name
}

output "eventhub_name" {
  description = "VoltGrid Event Hub"
  value       = azurerm_eventhub.events.name
}

output "deployment_region" {
  description = "Azure deployment region"
  value       = var.location
}

output "environment" {
  description = "Current environment"
  value       = var.environment
}