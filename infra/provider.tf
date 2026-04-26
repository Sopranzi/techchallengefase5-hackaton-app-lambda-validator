terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  backend "s3" {
    bucket = "terraform-state-soat-fase05-hackton-g15"
    
    key    = "lambda-auth/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project   = "SOAT-Tech-Challenge"
      ManagedBy = "Terraform"
      Component = "Auth-Lambda"
    }
  }
}