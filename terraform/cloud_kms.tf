resource "google_kms_key_ring" "evaluation_system_ring" {
  name     = "evaluation_system_ring"
  location = var.region
}

resource "google_kms_crypto_key" "evaluation_system_user_auth" {
  name     = "user_auth"
  key_ring = google_kms_key_ring.evaluation_system_ring.id

  lifecycle {
    prevent_destroy = true
  }
}
