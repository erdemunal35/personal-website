output "cloud_run_url" {
  description = "The public URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.personal_website.uri
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.cloud_run_source.repository_id}"
}

output "cloud_build_trigger_id" {
  description = "Cloud Build trigger ID"
  value       = google_cloudbuild_trigger.deploy_on_push.trigger_id
}
