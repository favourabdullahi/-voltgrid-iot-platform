variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment (dev, test, prod)"
  type        = string
  default     = "dev"
}

locals {
  rg_name = "voltgrid-${var.environment}-rg"

  tags = {
    Environment = var.environment
    Project     = "VoltGrid"
    ManagedBy   = "Terraform"
  }
}