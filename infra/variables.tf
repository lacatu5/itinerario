variable "project_id" {
  description = "The Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
  default     = "europe-west1"
}

variable "node_service_account_email" {
  description = "Service account email for GKE nodes (shared)"
  type        = string
  default     = "gke-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"
}

# Staging Variables
variable "staging_node_count" {
  description = "Initial node count for staging"
  type        = number
  default     = 1
}

variable "staging_machine_type" {
  description = "Machine type for staging nodes"
  type        = string
  default     = "e2-medium"
}

variable "staging_disk_size_gb" {
  description = "Disk size for staging nodes in GB"
  type        = number
  default     = 20
}

variable "staging_min_nodes" {
  description = "Minimum nodes for staging autoscaling"
  type        = number
  default     = 1
}

variable "staging_max_nodes" {
  description = "Maximum nodes for staging autoscaling"
  type        = number
  default     = 3
}

variable "staging_database_tier" {
  description = "Database tier for staging"
  type        = string
  default     = "db-f1-micro"
}

variable "staging_database_disk_size" {
  description = "Database disk size for staging in GB"
  type        = number
  default     = 10
}

variable "staging_database_password" {
  description = "Database password for staging"
  type        = string
  sensitive   = true
}

# Production Variables
variable "prod_node_count" {
  description = "Initial node count for production"
  type        = number
  default     = 2
}

variable "prod_machine_type" {
  description = "Machine type for production nodes"
  type        = string
  default     = "e2-medium"
}

variable "prod_disk_size_gb" {
  description = "Disk size for production nodes in GB"
  type        = number
  default     = 30
}

variable "prod_min_nodes" {
  description = "Minimum nodes for production autoscaling"
  type        = number
  default     = 2
}

variable "prod_max_nodes" {
  description = "Maximum nodes for production autoscaling"
  type        = number
  default     = 6
}

variable "prod_database_tier" {
  description = "Database tier for production"
  type        = string
  default     = "db-g6-small"
}

variable "prod_database_disk_size" {
  description = "Database disk size for production in GB"
  type        = number
  default     = 20
}

variable "prod_database_password" {
  description = "Database password for production"
  type        = string
  sensitive   = true
}
