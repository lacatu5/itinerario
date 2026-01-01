# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "container.googleapis.com",
    "cloudbuild.googleapis.com",
    "sqladmin.googleapis.com",
    "sql-component.googleapis.com",
    "iam.googleapis.com",
    "compute.googleapis.com",
    "run.googleapis.com",
    "firestore.googleapis.com",
    "servicenetworking.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# GKE Cluster (only create if node_count > 0)
resource "google_container_cluster" "main" {
  count    = var.node_count > 0 ? 1 : 0
  name     = var.cluster_name
  project  = var.project_id
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = "default"
  subnetwork = "default"

  networking_mode = "VPC_NATIVE"

  depends_on = [google_project_service.apis]
}

# GKE Node Pool (only create if node_count > 0)
resource "google_container_node_pool" "main" {
  count    = var.node_count > 0 ? 1 : 0
  name     = "${var.cluster_name}-pool"
  project  = var.project_id
  location = var.region
  cluster  = var.cluster_name

  node_count = var.node_count

  node_config {
    machine_type = var.machine_type
    disk_size_gb = var.disk_size_gb

    service_account = var.node_service_account_email

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  autoscaling {
    min_node_count = var.min_nodes
    max_node_count = var.max_nodes
  }

  management {
    auto_repair  = true
    auto_upgrade = false
  }
}

# Cloud SQL Instance
resource "google_sql_database_instance" "main" {
  name             = var.database_name
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_15"

  depends_on = [google_project_service.apis]

  settings {
    tier              = var.database_tier
    availability_type = var.database_availability_type
    disk_size         = var.database_disk_size
    disk_type         = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = false
      private_network = "projects/${var.project_id}/global/networks/default"
      ssl_mode        = "ENCRYPTED_ONLY"
    }

    backup_configuration {
      enabled = var.database_backup_enabled
    }
  }

  deletion_protection = false
}

# Cloud SQL Database
resource "google_sql_database" "main" {
  name     = var.database_name
  project  = var.project_id
  instance = google_sql_database_instance.main.name
}

# Cloud SQL User
resource "google_sql_user" "main" {
  name     = "postgres"
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  password = var.database_password
}

# Cloud Storage Bucket
resource "google_storage_bucket" "main" {
  name          = var.storage_bucket_name
  location      = var.region
  project       = var.project_id
  force_destroy = var.storage_force_destroy

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Firestore Database
resource "google_firestore_database" "main" {
  name                    = var.firestore_database_id
  project                 = var.project_id
  location_id             = var.firestore_location
  type                    = "FIRESTORE_NATIVE"
  concurrency_mode        = "OPTIMISTIC"
  delete_protection_state = var.firestore_delete_protection

  depends_on = [google_project_service.apis]
}

# Service Account for GKE Workloads
resource "google_service_account" "gke_workload" {
  account_id   = "${var.environment}-workload-sa"
  display_name = "${var.environment} Workload Service Account"
  project      = var.project_id
}

# IAM Permissions for GKE Workload SA
resource "google_project_iam_member" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}

resource "google_project_iam_member" "artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}

resource "google_storage_bucket_iam_member" "bucket_admin" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.gke_workload.email}"
}

# Workload Identity Binding
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.gke_workload.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.namespace}/${var.environment}-workload-sa]"
}

# Kubernetes Namespace (via kubectl provider, optional)
# Note: This will be created by Helm during deployment
