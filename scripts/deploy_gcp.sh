#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

echo -e "${BLUE}======================================================================${NC}"
# shellcheck disable=SC2145
echo -e "${BLUE}          Google Cloud Run Enterprise Deployment Blueprint            ${NC}"
echo -e "${BLUE}======================================================================${NC}\n"

# 1. Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✘ Google Cloud SDK (gcloud CLI) is not installed on your Mac.${NC}"
    echo -e "To install it, please follow these steps:"
    echo -e "  1. Run: brew install --cask google-cloud-sdk"
    echo -e "  2. Run: gcloud init"
    exit 1
fi

# 2. Configuration Settings
# REPLACE THESE WITH YOUR ACTUAL GOOGLE CLOUD VALUES:
PROJECT_ID="ai-platform-98765" # E.g., "my-production-app-12345"
REGION="us-east5"             # Select region closest to you
SERVICE_NAME="ai-knowledge-api"  # Name of your Cloud Run service

echo -e "Configured Settings:"
echo -e "  - GCP Project ID: ${BLUE}$PROJECT_ID${NC}"
echo -e "  - Deploy Region : ${BLUE}$REGION${NC}"
echo -e "  - Service Name  : ${BLUE}$SERVICE_NAME${NC}\n"

# Instruction to check if the user configured their Project ID
if [ "$PROJECT_ID" == "your-gcp-project-id" ]; then
    echo -e "${RED}⚠ Please edit 'scripts/deploy_gcp.sh' first and replace 'your-gcp-project-id' with your actual Google Cloud Project ID.${NC}"
    exit 1
fi

# 3. Authenticate & Set Project
echo -e "${BLUE}[1/4] Configuring gcloud context...${NC}"
gcloud config set project "$PROJECT_ID"

# 4. Enable Required Google Cloud APIs
echo -e "\n${BLUE}[2/4] Enabling required Google Cloud APIs...${NC}"
echo -e "This registers the container build, registry, and execution APIs in your GCP billing account:"
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com

# 5. Build and Deploy directly from source
echo -e "\n${BLUE}[3/4] Triggering Cloud Build & Deploy to Cloud Run...${NC}"
echo -e "Google Cloud Build will upload the './backend' folder, build your production Dockerfile"
echo -e "in the cloud, register it in Artifact Registry, and deploy it to a live public URL."
echo -e "This will take about 1-2 minutes...\n"

# Note: We pass --allow-unauthenticated so the public internet can access our REST endpoints
# In production, we'll configure database URL environment variables in the GCP Console under Cloud Run configuration!
gcloud run deploy "$SERVICE_NAME" \
    --source ./backend \
    --region "$REGION" \
    --allow-unauthenticated \
    --quiet \
    --set-env-vars "DATABASE_URL=postgresql://mydb_owner:npg_6QE2LpwGtcST@ep-falling-fire-b57jetpa-pooler.c-7.us-east-2.aws.neon.tech/mydb?sslmode=require&channel_binding=require,ALLOWED_ORIGINS=*"

echo -e "\n${GREEN}✔ [4/4] Enterprise Cloud Run Service Successfully Deployed!${NC}"
echo -e "Next Steps:"
echo -e "  1. Go to your Google Cloud Console."
echo -e "  2. Select Cloud Run -> ${SERVICE_NAME}."
echo -e "  3. Go to Variables & Secrets."
echo -e "  4. Set 'DATABASE_URL' to your production PostgreSQL connection string."
echo -e "  5. Set 'ALLOWED_ORIGINS' to your live Next.js Vercel URL."
echo -e "     (Note: If setting multiple domains, use semicolon delimiters instead of commas"
echo -e "      to prevent gcloud parsing issues, e.g., 'https://my-frontend.vercel.app;http://localhost:3000')"
echo -e "  6. Enjoy your live public API! 🎉"
