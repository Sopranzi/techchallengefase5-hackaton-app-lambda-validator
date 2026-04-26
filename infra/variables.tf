variable "aws_region" {
  description = "Região da AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "jwt_secret" {
  description = "Chave secreta para assinatura do Token JWT"
  type        = string
  sensitive   = true
  # Não definimos valor default aqui por segurança. 
  # O valor virá da flag -var="jwt_secret=..." no comando do Terraform
}

variable "project_name" {
  description = "Nome base do projeto para tags e identificação"
  type        = string
  default     = "soat-tech-challenge"
}

# --- Configurações do Banco de Dados (RDS) ---
variable "db_host" {
  description = "Endpoint do banco de dados (ex: terraform-rds.xxx.us-east-1.rds.amazonaws.com)"
  type        = string
}

variable "db_name" {
  description = "Nome do banco de dados"
  type        = string
}

variable "db_user" {
  description = "Usuário master do banco"
  type        = string
}

variable "db_password" {
  description = "Senha do banco de dados"
  type        = string
  sensitive   = true
}

# --- Configurações de Rede (VPC) ---
variable "vpc_subnet_ids" {
  description = "Lista de IDs das Subnets PRIVADAS onde a Lambda poderá criar interfaces de rede"
  type        = list(string) 
}

variable "vpc_security_group_ids" {
  description = "IDs dos Security Groups que a Lambda usará (separados por vírgula)"
  type        = list(string)
}