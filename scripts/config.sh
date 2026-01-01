#!/bin/bash
export PROJECT_ID=${PROJECT_ID:-"YOUR_PROJECT_ID"}
export REGION=${REGION:-"europe-west1"}
export ZONE=${ZONE:-"europe-west1-d"}
export CLUSTER=${CLUSTER:-"itinerario-gke"}
export CLUSTER_NAME="${CLUSTER}"
export PROD_DOMAIN=${PROD_DOMAIN:-"your-domain.com"}
export PROD_API_DOMAIN=${PROD_API_DOMAIN:-"api.your-domain.com"}
export STAGING_DOMAIN=${STAGING_DOMAIN:-"staging.your-domain.com"}
export STAGING_API_DOMAIN=${STAGING_API_DOMAIN:-"api.staging.your-domain.com"}
export IMAGE_REGISTRY="${IMAGE_REGISTRY:-europe-west1-docker.pkg.dev/${PROJECT_ID}/itinerario}"
export STATE_BUCKET="${PROJECT_ID}-terraform-state-prod"

validate_config() {
  if [ "$PROJECT_ID" = "YOUR_PROJECT_ID" ]; then
    echo "ERROR: PROJECT_ID not set. Use: PROJECT_ID=your-project-id ./script.sh"
    return 1
  fi
  return 0
}

show_config() {
  echo "Project: $PROJECT_ID | Region: $REGION | Cluster: $CLUSTER | Registry: $IMAGE_REGISTRY"
}
