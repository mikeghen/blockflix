# Infrastructure

## Setup Terraform
0. Install Terraform
1. Create a `terraform` IAM user with Administator Access permissions
2. Export the AWS access key and secret as environment variables:
```
export AWS_ACCESS_KEY_ID="xxxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxxx"
export AWS_DEFAULT_REGION="us-west-2"
```
3. Create a `infrastructure` directory
4. Initialize Terraform:
```
cd infrastructure
terraform init
```
:warning: You will want to delete `terraform.tfstate` and `terraform.tfstate.backup`
