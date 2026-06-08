# Remote state backend — bucket must exist before terraform init.
# Created once: aws s3api create-bucket --bucket cost-terraform-state-bucket --region us-east-1

terraform {
  backend "s3" {
    bucket       = "cost-terraform-state-bucket"
    key          = "cost-optimizer/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
