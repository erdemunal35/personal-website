variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "erdem-personal-website-prod"
}

variable "project_number" {
  description = "GCP project number"
  type        = string
  default     = "157799560453"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "personal-website"
}

variable "maps_api_key" {
  description = "Google Maps Embed API key (set via TF_VAR_maps_api_key or terraform.tfvars)"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask SECRET_KEY for session management (set via TF_VAR_secret_key or terraform.tfvars)"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "erdemunal35"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "personal-website"
}
