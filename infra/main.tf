# infra/main.tf

# 1. Empacotamento do Código (Zip)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../build" 
  output_path = "lambda_function.zip"
}

# 2. A Função Lambda
resource "aws_lambda_function" "auth_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "soat-auth-function"
  
  # Usando a LabRole existente (Conforme seu ambiente AWS Academy)
  role             = data.aws_iam_role.lab_role.arn 

  handler          = "src.main.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 10 # Aumentamos um pouco pois conexão com banco pode demorar

  # --- CONFIGURAÇÃO DE REDE (VPC) ---
  vpc_config {
    subnet_ids         = var.vpc_subnet_ids         # Correto
    security_group_ids = var.vpc_security_group_ids # Remova o split() se houver
  }

  # --- VARIÁVEIS DE AMBIENTE ---
  environment {
    variables = {
      JWT_SECRET = var.jwt_secret
      DB_HOST    = var.db_host
      DB_NAME    = var.db_name
      DB_USER    = var.db_user
      DB_PASS    = var.db_password
    }
  }

  tags = {
    Project   = "SOAT-Tech-Challenge"
    ManagedBy = "Terraform"
    Component = "Auth-Lambda"
  }
}

# Nova Função: Authorizer
resource "aws_lambda_function" "authorizer_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "soat-authorizer-function" # Nome diferente
  role             = data.aws_iam_role.lab_role.arn
  handler          = "src.authorizer.lambda_handler" # Aponta para o novo arquivo
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.9"

  environment {
    variables = {
      JWT_SECRET = var.jwt_secret
      # Authorizer não precisa de banco de dados, só da chave secreta
    }
  }
  tags = {
    Component = "Auth-Authorizer"
  }
}
