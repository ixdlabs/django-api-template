# Define VPC using the terraform-aws-modules/vpc/aws module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.2.0"

  # Set VPC name and CIDR block
  name = "my-vpc"
  cidr = var.vpc_cidr_block

  # Specify availability zones and subnets
  azs            = [var.public_subnet_1_avail_zone]
  public_subnets = [var.public_subnet_1_cidr_block]

  # Set tags for various resources within the VPC
  public_subnet_tags          = { Name = "${var.project_name}-${var.env}-public-subnet-1" }
  igw_tags                    = { Name = "${var.project_name}-${var.env}-igw" }
  default_security_group_tags = { Name = "${var.project_name}-${var.env}-default-sg" }
  default_route_table_tags    = { Name = "${var.project_name}-${var.env}-main-rtb" }
  public_route_table_tags     = { Name = "${var.project_name}-${var.env}-public-rtb" }

  # Set overall tags for the VPC
  tags = {
    Name = "${var.project_name}-${var.env}-vpc"
  }
}

###########################################################################

# Define Security Group using terraform-aws-modules/security-group/aws module
module "security-group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.0"

  # Set Security Group name and associate it with the VPC created above
  name   = "${var.project_name}-${var.env}-sg"
  vpc_id = module.vpc.vpc_id

  # Configure ingress and egress rules for the Security Group
  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["https-443-tcp", "ssh-tcp", "http-80-tcp"]
  egress_rules        = ["all-all"]

  # Set tags for the Security Group
  tags = {
    Name = "${var.project_name}-${var.env}-sg"
  }
}

#############################################################################

# Define S3 bucket for deployments using terraform-aws-modules/s3-bucket/aws module
module "s3_bucket_deployments" {
  source = "terraform-aws-modules/s3-bucket/aws"

  # Set the name for the S3 bucket
  bucket = "${var.project_name}-${var.env}-deployments"
}




# Define Elastic Beanstalk Application and Environment
resource "aws_elastic_beanstalk_application" "beanstalk-app" {
  name        = "${var.project_name}-${var.env}"
  description = "${var.project_name}-${var.env} Elastic Beanstalk Application"
}

resource "aws_elastic_beanstalk_environment" "beanstalk-env" {
  # Set the name and link to the Beanstalk Application
  name                = "${var.project_name}-${var.env}-env"
  application         = aws_elastic_beanstalk_application.beanstalk-app.name
  solution_stack_name = var.stack_name

  # Define dynamic settings for environment variables
  dynamic "setting" {
    for_each = {
      DATABASE_URL             = var.DATABASE_URL
      USE_AWS_S3               = var.USE_AWS_S3
      AWS_S3_ACCESS_KEY_ID     = var.AWS_S3_ACCESS_KEY_ID
      AWS_S3_SECRET_ACCESS_KEY = var.AWS_S3_SECRET_ACCESS_KEY
      AWS_STORAGE_BUCKET_NAME  = var.AWS_STORAGE_BUCKET_NAME
      AWS_S3_REGION_NAME       = var.AWS_S3_REGION_NAME
      DJANGO_SETTINGS_MODULE   = var.DJANGO_SETTINGS_MODULE
      DJANGO_ALLOWED_HOSTS     = var.DJANGO_ALLOWED_HOSTS
      # Add other environment variables here
    }

    content {
      namespace = "aws:elasticbeanstalk:application:environment"
      name      = setting.key
      value     = setting.value
    }
  }

  # Set VPC related settings
  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = module.vpc.vpc_id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "AssociatePublicIpAddress"
    value     = "True"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = module.vpc.public_subnets[0]
  }

  # Set role for launch configuration
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = "aws-elasticbeanstalk-ec2-role"
  }

  # Set service role for Elastic Beanstalk environment
  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = "aws-elasticbeanstalk-service-role"
  }

  # Set environment type, single instance or load balanced
  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "SingleInstance"
  }

  # Set EC2 instance type
  setting {
    namespace = "aws:ec2:instances"
    name      = "InstanceTypes"
    value     = var.instance_type
  }

  # Set security group and key pair related settings
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = module.security-group.security_group_id
  }


  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "EC2KeyName"
    value     = var.ec2_keypair
  }



  # Set CloudWatch logs related settings
  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "StreamLogs"
    value     = "true"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs:health"
    name      = "HealthStreamingEnabled"
    value     = "true"
  }
}
