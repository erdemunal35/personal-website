resource "google_cloudbuild_trigger" "deploy_on_push" {
  name     = "personal-website-deploy"
  location = var.region

  github {
    owner = var.github_owner
    name  = var.github_repo

    push {
      branch = "^main$"
    }
  }

  build {
    step {
      name = "gcr.io/k8s-skaffold/pack"
      args = [
        "build",
        "${var.region}-docker.pkg.dev/${var.project_id}/cloud-run-source-deploy/${var.service_name}/${var.service_name}",
        "--builder=gcr.io/buildpacks/builder:v1",
        "--path=.",
      ]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "push",
        "${var.region}-docker.pkg.dev/${var.project_id}/cloud-run-source-deploy/${var.service_name}/${var.service_name}",
      ]
    }

    step {
      name = "gcr.io/cloud-builders/gcloud"
      args = [
        "run", "deploy", var.service_name,
        "--image=${var.region}-docker.pkg.dev/${var.project_id}/cloud-run-source-deploy/${var.service_name}/${var.service_name}",
        "--region=${var.region}",
        "--platform=managed",
      ]
    }

    options {
      logging = "CLOUD_LOGGING_ONLY"
    }
  }

}
