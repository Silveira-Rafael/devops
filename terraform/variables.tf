variable "aws_region" {
  description = "Região da AWS onde a infraestrutura será criada."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "devops"
}

variable "environment" {
  description = "Ambiente de implantação."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "O ambiente deve ser dev, staging ou prod."
  }
}

variable "vpc_cidr" {
  description = "Bloco CIDR da VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Bloco CIDR da sub-rede pública."
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  description = "Tipo da instância EC2."
  type        = string
  default     = "t3.micro"
}

variable "app_port" {
  description = "Porta em que a aplicação escuta dentro do contêiner."
  type        = number
  default     = 8000
}

variable "allowed_ssh_cidr" {
  description = "CIDR autorizado a acessar a porta 22"
  type        = string
  default     = ""
}

variable "repository_url" {
  description = "URL HTTPS do repositório GitHub com o código e o Dockerfile."
  type        = string
  default     = "https://github.com/Silveira-Rafael/devops"
}
