resource "google_cloud_run_service" "cloud_run_evaluation_system" {
  name     = "evaluation-system-server"
  location = var.region

  template {
    spec {
      containers {
        image = "asia.gcr.io/${var.project}/evaluation-system-server:${var.image_version}"
      }
    }
  }
  autogenerate_revision_name = true
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = var.evaluataion_system_members
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.cloud_run_evaluation_system.location
  project     = google_cloud_run_service.cloud_run_evaluation_system.project
  service     = google_cloud_run_service.cloud_run_evaluation_system.name

  policy_data = data.google_iam_policy.noauth.policy_data
}
