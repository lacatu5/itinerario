#!/bin/bash
set -e

ENV_FILE=${1:-"environments/prod.tfvars"}
read -p "Are you sure? Type 'destroy' to confirm: " confirm

if [ "$confirm" != "destroy" ]; then
  exit 1
fi

cd "$(dirname "$0")/.."

terraform plan -destroy -var-file="$ENV_FILE" -out=tfplan
terraform apply tfplan
