provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location
  tags     = local.tags
}

resource "azurerm_eventhub_namespace" "hubns" {
  name                = "voltgrid-hub-ns"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1
  tags                = local.tags
}

resource "azurerm_eventhub" "events" {
  name                = "voltgrid-events"
  namespace_name      = azurerm_eventhub_namespace.hubns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}