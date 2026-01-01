output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = var.cluster_name
}

output "cluster_location" {
  description = "Location of the GKE cluster"
  value       = var.region
}

output "cluster_endpoint" {
  description = "Endpoint of the GKE cluster (only if created by module)"
  value       = try(google_container_cluster.main[0].endpoint, null)
}

output "cluster_ca_certificate" {
  description = "CA certificate of the GKE cluster (only if created by module)"
  value       = try(google_container_cluster.main[0].master_auth[0].cluster_ca_certificate, null)
  sensitive   = true
}

output "database_instance_name" {
  description = "Name of the Cloud SQL instance"
  value       = google_sql_database_instance.main.name
}

output "database_instance_connection_name" {
  description = "Connection name of the Cloud SQL instance"
  value       = google_sql_database_instance.main.connection_name
}

output "database_instance_private_ip" {
  description = "Private IP of the Cloud SQL instance"
  value       = google_sql_database_instance.main.private_ip_address
}

output "storage_bucket_name" {
  description = "Name of the Cloud Storage bucket"
  value       = google_storage_bucket.main.name
}

output "storage_bucket_url" {
  description = "URL of the Cloud Storage bucket"
  value       = google_storage_bucket.main.url
}

output "firestore_database_id" {
  description = "ID of the Firestore database"
  value       = google_firestore_database.main.name
}

output "service_account_email" {
  description = "Email of the GKE workload service account"
  value       = google_service_account.gke_workload.email
}

output "namespace" {
  description = "Kubernetes namespace"
  value       = var.namespace
}
