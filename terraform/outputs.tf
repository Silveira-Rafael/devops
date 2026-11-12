output "vpc_id" {
  description = "ID da VPC criada."
  value       = aws_vpc.main.id
}

output "instance_public_ip" {
  description = "IP público da instância EC2."
  value       = aws_instance.app.public_ip
}

output "app_url" {
  description = "URL da aplicação"
  value       = "http://${aws_instance.app.public_ip}/health"
}

output "artifacts_bucket" {
  description = "Nome do bucket S3 de artefatos."
  value       = aws_s3_bucket.artifacts.bucket
}
