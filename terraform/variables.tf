variable "project_name" {}               # Project name
variable "env" {}                        # environment (dev, stag, or prod)
variable "vpc_cidr_block" {}             # CIDR block for the VPC
variable "public_subnet_1_cidr_block" {} # CIDR block for the public subnet 1
variable "public_subnet_1_avail_zone" {} # Availability zone for the public subnet 1
variable "stack_name" {}                 # Elastic Beanstalk solution stack name
variable "instance_type" {}              # EC2 instance type
variable "ec2_keypair" {}                # EC2 key pair for SSH access, create a keypair manually


# Environment Variables
variable "DATABASE_URL" {}             # Database connection string
variable "USE_AWS_S3" {}               # Flag to indicate whether to use AWS S3 for storage
variable "AWS_S3_ACCESS_KEY_ID" {}     # Access key ID of the IAM user with permission to AWS S3 media bucket
variable "AWS_S3_SECRET_ACCESS_KEY" {} # Secret access key of the IAM user with permission to AWS S3 media bucket
variable "AWS_STORAGE_BUCKET_NAME" {}  # Name of the AWS Storage media bucket
variable "AWS_S3_REGION_NAME" {}       # Region name for AWS S3 media bucket
variable "DJANGO_ALLOWED_HOSTS" {}     # Allowed hosts for Django application
variable "DJANGO_SETTINGS_MODULE" {}   # Django settings module for the application
