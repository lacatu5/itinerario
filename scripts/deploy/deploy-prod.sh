#!/bin/bash
set -e

PROJECT_ID=${PROJECT_ID:-"YOUR_PROJECT_ID"}
REGION=${REGION:-"europe-west1"}
CLUSTER=${CLUSTER:-"itinerario-gke"}
NAMESPACE="itinerario-prod"
DOMAIN=${DOMAIN:-"your-domain.com"}
API_DOMAIN=${API_DOMAIN:-"api.your-domain.com"}

if [ "$PROJECT_ID" = "YOUR_PROJECT_ID" ]; then
  echo "ERROR: PROJECT_ID not set!"
  echo "Set with: export PROJECT_ID=your-project-id"
  exit 1
fi

gcloud container clusters get-credentials $CLUSTER \
  --region $REGION \
  --project $PROJECT_ID

GIT_TAG=$(git rev-parse --short HEAD)

helm upgrade --install itinerario ../../helm \
  --namespace $NAMESPACE \
  --create-namespace \
  --values ../../helm/values-prod.yaml \
  --set image.tag=$GIT_TAG \
  --set services[0].image.tag=prod \
  --wait

echo "Deployed to prod!"
echo "Frontend: https://$DOMAIN"
echo "API: https://$API_DOMAIN"
echo "Check gateway: kubectl get gateway -n $NAMESPACE"
echo "Check pods: kubectl get pods -n $NAMESPACE"
