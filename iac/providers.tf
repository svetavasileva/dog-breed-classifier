provider "aws" {
  region = "us-east-1"
}

terraform {
  required_version = ">= 1.9.0"
  backend "s3" {
    bucket = "terraform-s3-backend-lana"
    key    = "tfstate"
    region = "us-east-1"
  }
}
