variable "project_id" {
  description = "The Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
}

variable "environment" {
  description = "Environment name (staging/prod)"
  type        = string
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace for this environment"
  type        = string
}

variable "node_count" {
  description = "Initial number of nodes"
  type        = number
  default     = 2
}

variable "machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-medium"
}

variable "disk_size_gb" {
  description = "Node disk size in GB"
  type        = number
  default     = 30
}

variable "min_nodes" {
  description = "Minimum number of nodes for autoscaling"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of nodes for autoscaling"
  type        = number
  default     = 6
}

variable "node_service_account_email" {
  description = "Service account email for GKE nodes"
  type        = string
}

variable "database_name" {
  description = "Name of the Cloud SQL instance and database"
  type        = string
}

variable "database_tier" {
  description = "Cloud SQL tier"
  type        = string
}

variable "database_availability_type" {
  description = "Cloud SQL availability type"
  type        = string
  default     = "ZONAL"
}

variable "database_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 10
}

variable "database_backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "database_password" {
  description = "Password for the database user"
  type        = string
  sensitive   = true
}

variable "storage_bucket_name" {
  description = "Name of the Cloud Storage bucket"
  type        = string
}

variable "storage_force_destroy" {
  description = "Force destroy bucket even if not empty"
  type        = bool
  default     = false
}

variable "firestore_database_id" {
  description = "Firestore database ID"
  type        = string
}

variable "firestore_location" {
  description = "Firestore location"
  type        = string
  default     = var.region
}

variable "firestore_delete_protection" {
  description = "Firestore delete protection"
  type        = string
  default     = "DELETE_PROTECTION_ENABLED"
}
