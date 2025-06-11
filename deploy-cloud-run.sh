#!/bin/bash
# deploy-cloud-run.sh - Deploy Pileup Buster to Google Cloud Run

set -e

# Check if project ID is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <PROJECT_ID> [REGION]"
    echo "Example: $0 my-project-id us-central1"
    exit 1
fi

PROJECT_ID=$1
REGION=${2:-us-central1}
SERVICE_NAME="pileup-buster"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Pileup Buster to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Check if required environment variables are set
if [ -z "$MONGO_URI" ]; then
    echo "❌ MONGO_URI environment variable is required"
    echo "Please set it with: export MONGO_URI='your-mongodb-connection-string'"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY environment variable is required"
    echo "Please set it with: export SECRET_KEY='your-secret-key'"
    exit 1
fi

if [ -z "$ADMIN_USERNAME" ]; then
    echo "❌ ADMIN_USERNAME environment variable is required"
    echo "Please set it with: export ADMIN_USERNAME='admin'"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    echo "❌ ADMIN_PASSWORD environment variable is required"
    echo "Please set it with: export ADMIN_PASSWORD='your-secure-password'"
    exit 1
fi

echo "✅ Environment variables configured"

# Build and push Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "📤 Pushing to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "MONGO_URI=$MONGO_URI" \
    --set-env-vars "SECRET_KEY=$SECRET_KEY" \
    --set-env-vars "ADMIN_USERNAME=$ADMIN_USERNAME" \
    --set-env-vars "ADMIN_PASSWORD=$ADMIN_PASSWORD" \
    ${QRZ_USERNAME:+--set-env-vars "QRZ_USERNAME=$QRZ_USERNAME"} \
    ${QRZ_PASSWORD:+--set-env-vars "QRZ_PASSWORD=$QRZ_PASSWORD"} \
    --project $PROJECT_ID

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID)

echo "🎉 Deployment completed!"
echo "🌍 Service URL: $SERVICE_URL"
echo "📖 API Docs: $SERVICE_URL/docs"
echo "👨‍💼 Admin Panel: Use basic auth with your ADMIN_USERNAME/ADMIN_PASSWORD"

echo ""
echo "📝 To update environment variables later:"
echo "gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars \"VAR_NAME=value\" --project $PROJECT_ID"