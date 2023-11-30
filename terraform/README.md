# Terraform AWS Elastic Beanstalk Deployment

This Terraform project sets up an AWS Elastic Beanstalk environment along with a VPC, security group, and S3 bucket for media storage. Follow the steps below to deploy the infrastructure.


## Initial Setup

1. **Add s3 backend key to `providers.tf` file**

     ```hcl
     terraform {
      backend "s3" {
         bucket = "ixd-terraform-tfstate-bucket"
         key    = "add your key here" #ex: terraform-aws-beanstalk-deployment/terraform.tfstate
         region = "us-east-1"
      }
   }
     ```

2. **Create S3 Bucket for Media Files**

   - Manually create an S3 bucket to store media files. Note the bucket name for use in later steps.

3. **Add User for Media Bucket Access**

   - Create an IAM user with S3 access and provide necessary permissions to access the media bucket.
   - Retrieve the access key ID and secret access key for this user.
   - add relevent env vars to terraform.yml file - USE_AWS_S3, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME, AWS_S3_ACCESS_KEY_ID and AWS_S3_SECRET_ACCESS_KEY


4. **Add other varibales also to `terraform.yml` file**

     ```hcl
     project_name = "your-project-name"
     env = "dev"
     vpc_cidr_block = "10.0.0.0/16"
     public_subnet_1_cidr_block = "10.0.1.0/24"
     public_subnet_1_avail_zone = "us-east-1a"
     stack_name = "64bit Amazon Linux 2 v5.8.1 running Python 3.8"
     instance_type = "t2.micro"
     ec2_keypair = "your-key-pair-name"

     # Additional variables as needed
     DATABASE_URL = "your_database_url"
     USE_AWS_S3 = true
     AWS_S3_ACCESS_KEY_ID = "your_s3_access_key_id"
     AWS_S3_SECRET_ACCESS_KEY = "your_s3_secret_access_key"
     AWS_STORAGE_BUCKET_NAME = "your_media_bucket_name"
     AWS_S3_REGION_NAME = "your_s3_region"
     DJANGO_ALLOWED_HOSTS = "your_allowed_hosts"
     DJANGO_SETTINGS_MODULE = "your_django_settings_module"
     ```

## Terraform Deployment

1. **Initialize Terraform**

   Run the following command to initialize the Terraform working directory:

   ```bash
   terraform init

2. **Review and Apply Terraform Changes**
   ```bash
   terraform plan
   terraform apply
