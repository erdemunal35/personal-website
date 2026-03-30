resource "google_cloud_run_v2_service" "personal_website" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = "${var.project_number}-compute@developer.gserviceaccount.com"

    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }

    timeout = "300s"

    max_instance_request_concurrency = 80

    containers {
      # Image is managed by Cloud Build — Terraform tracks the latest deployed image.
      # To update: push to GitHub (Cloud Build trigger) or run `gcloud run deploy --source .`
      image = "${var.region}-docker.pkg.dev/${var.project_id}/cloud-run-source-deploy/${var.service_name}/${var.service_name}:latest"

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      env {
        name  = "MAPS_API_KEY"
        value = var.maps_api_key
      }

      env {
        name  = "SECRET_KEY"
        value = var.secret_key
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    # Ignore image changes — Cloud Build handles deployments independently
    ignore_changes = [
      template[0].containers[0].image,
      template[0].revision,
      client,
      client_version,
    ]
  }
}

# Allow unauthenticated (public) access
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.personal_website.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
