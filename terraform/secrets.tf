resource "google_project_service" "secretmanager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_secret_manager_secret" "maps_api_key" {
  project   = var.project_id
  secret_id = "maps-api-key"
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret" "secret_key" {
  project   = var.project_id
  secret_id = "flask-secret-key"
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret" "gmail_app_password" {
  project   = var.project_id
  secret_id = "gmail-app-password"
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

# Grant the Compute default SA access to all secrets in this project
resource "google_project_iam_member" "compute_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}
