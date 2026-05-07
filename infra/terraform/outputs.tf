output "minio_api" {
  value       = "http://localhost:19005"
  description = "S3 API endpoint for the Terraform-provisioned MinIO container"
}

output "minio_console" {
  value       = "http://localhost:19006"
  description = "MinIO web console"
}
