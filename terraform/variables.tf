variable "project" {
  type   = string
  default = "gcp-project-id"
}

variable "region" {
  type   = string
  default = "asia-northeast1"
}

variable "zone" {
  default = "asia-northeast1-b"
}

variable "evaluation_system_members" {
  default = [
    "user:user.mail.address@gmail.com",
    "allUsers",
  ]
}

variable "image_version" {
  type   = string
  default = "latest"
}

