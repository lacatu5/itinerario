# Staging Outputs
output "staging_cluster_name" {
  description = "Staging cluster name"
  value       = module.staging.cluster_name
}

output "staging_cluster_endpoint" {
  description = "Staging cluster endpoint"
  value       = module.staging.cluster_endpoint
}

output "staging_database_connection_name" {
  description = "Staging database connection name"
  value       = module.staging.database_instance_connection_name
}

output "staging_database_private_ip" {
  description = "Staging database private IP"
  value       = module.staging.database_instance_private_ip
}

output "staging_storage_bucket" {
  description = "Staging storage bucket name"
  value       = module.staging.storage_bucket_name
}

output "staging_firestore_database" {
  description = "Staging Firestore database ID"
  value       = module.staging.firestore_database_id
}

output "staging_service_account" {
  description = "Staging service account email"
  value       = module.staging.service_account_email
}

# Production Outputs
output "prod_cluster_name" {
  description = "Production cluster name"
  value       = module.prod.cluster_name
}

output "prod_cluster_endpoint" {
  description = "Production cluster endpoint"
  value       = module.prod.cluster_endpoint
}

output "prod_database_connection_name" {
  description = "Production database connection name"
  value       = module.prod.database_instance_connection_name
}

output "prod_database_private_ip" {
  description = "Production database private IP"
  value       = module.prod.database_instance_private_ip
}

output "prod_storage_bucket" {
  description = "Production storage bucket name"
  value       = module.prod.storage_bucket_name
}

output "prod_firestore_database" {
  description = "Production Firestore database ID"
  value       = module.prod.firestore_database_id
}

output "prod_service_account" {
  description = "Production service account email"
  value       = module.prod.service_account_email
}
