terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.26.0"
    }
  }
}


terraform {
  backend "s3" {
    bucket = "ixd-terraform-tfstate-bucket"
    key    = "terraform-aws-beanstalk-deployment/terraform.tfstate"
    region = "us-east-1"
  }
}


provider "aws" {

}
