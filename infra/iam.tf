# infra/iam.tf

data "aws_caller_identity" "current" {}

# 2. Busca a Role existente chamada "LabRole"
# Isso substitui a necessidade de escrever o ARN manualmente, o Terraform busca para você.
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}