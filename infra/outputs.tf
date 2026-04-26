output "lambda_arn" {
  description = "ARN da Lambda para ser usado no API Gateway"
  value       = aws_lambda_function.auth_function.arn
}

output "authorizer_arn" {
  value = aws_lambda_function.authorizer_function.arn
}