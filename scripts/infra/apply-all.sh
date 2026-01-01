#!/bin/bash
set -e

ENV_FILE=${1:-"environments/prod.tfvars"}
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  exit 1
fi

cd "$(dirname "$0")/.."

terraform fmt -recursive
terraform validate
terraform plan -var-file="$ENV_FILE" -out=tfplan
terraform apply tfplan
terraform output -json
