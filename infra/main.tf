terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "YOUR_PROJECT_ID-terraform-state-prod"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs at root level
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Reserve global IP address for Cloud SQL (shared across environments)
resource "google_compute_global_address" "private_ip_address" {
  name          = "itinerario-private-ip"
  project       = var.project_id
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = "projects/${var.project_id}/global/networks/default"
}

# Service Networking Connection for Cloud SQL (shared across environments)
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = "projects/${var.project_id}/global/networks/default"
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  lifecycle {
    ignore_changes = all
  }
}

# Single shared GKE Cluster with Autopilot
resource "google_container_cluster" "shared" {
  name     = "itinerario-cluster"
  project  = var.project_id
  location = var.region

  enable_autopilot = true

  network    = "default"
  subnetwork = "default"

  networking_mode = "VPC_NATIVE"

  depends_on = [google_project_service.apis]

  lifecycle {
    ignore_changes = [
      deletion_protection,
      initial_node_count,
      remove_default_node_pool
    ]
  }
}

# Staging Environment (databases + storage only)
module "staging" {
  source = "./modules/environment"

  project_id   = var.project_id
  region       = var.region
  environment  = "staging"
  cluster_name = google_container_cluster.shared.name
  namespace    = "itinerario-staging"

  # Disable cluster creation (using shared cluster)
  node_count                 = 0
  machine_type               = "e2-medium"
  disk_size_gb               = 0
  min_nodes                  = 0
  max_nodes                  = 0
  node_service_account_email = var.node_service_account_email

  database_name               = "itinerario-staging"
  database_tier               = var.staging_database_tier
  database_availability_type  = "ZONAL"
  database_disk_size          = var.staging_database_disk_size
  database_backup_enabled     = true
  database_password           = var.staging_database_password
  storage_bucket_name         = "itinerario-staging-storage"
  storage_force_destroy       = false
  firestore_database_id       = "itinerario-staging"
  firestore_location          = var.region
  firestore_delete_protection = "DELETE_PROTECTION_ENABLED"
}

# Production Environment (databases + storage only)
module "prod" {
  source = "./modules/environment"

  project_id   = var.project_id
  region       = var.region
  environment  = "prod"
  cluster_name = google_container_cluster.shared.name
  namespace    = "itinerario-prod"

  # Disable cluster creation (using shared cluster)
  node_count                 = 0
  machine_type               = "e2-medium"
  disk_size_gb               = 0
  min_nodes                  = 0
  max_nodes                  = 0
  node_service_account_email = var.node_service_account_email

  database_name               = "itinerario-prod"
  database_tier               = var.prod_database_tier
  database_availability_type  = "ZONAL"
  database_disk_size          = var.prod_database_disk_size
  database_backup_enabled     = true
  database_password           = var.prod_database_password
  storage_bucket_name         = "itinerario-prod-storage"
  storage_force_destroy       = false
  firestore_database_id       = "itinerario-prod"
  firestore_location          = var.region
  firestore_delete_protection = "DELETE_PROTECTION_ENABLED"
}
