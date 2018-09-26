# Infrastructure

## Setup Terraform
0. Install Terraform
1. Create a `terraform` IAM user with Administrator Access permissions
2. Add this key and secret to your AWS configuration file on your development machine. Fisrt, edit `~/.aws/config` and add:
```
[profile blockflix]
```
Then edit `~/.aws/credentials` and add:
```
[blockflix]
aws_access_key_id = xxxxxx
aws_secret_access_key = xxxxxx
```
3. Now, create a `infrastructure` directory in the root of this project
4. Initialize Terraform:
```
cd infrastructure
terraform init
```
:warning: You will want to delete `terraform.tfstate` and `terraform.tfstate.backup`
