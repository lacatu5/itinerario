#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source scripts/config.sh
validate_config

BUCKET_NAME="${PROJECT_ID}-terraform-state-prod"

if ! gsutil ls gs://$BUCKET_NAME >/dev/null 2>&1; then
  gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME
  gsutil versioning set on gs://$BUCKET_NAME
fi

terraform init
