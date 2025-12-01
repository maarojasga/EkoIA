#!/bin/bash

# Script para desplegar en Google Cloud Run
# Uso: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Configuración
PROJECT_ID="${1:-tu-proyecto-id}"
REGION="${2:-us-central1}"
SERVICE_NAME="co2-microservice"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=========================================="
echo "🚀 Desplegando CO2 Microservice"
echo "=========================================="
echo "Proyecto: ${PROJECT_ID}"
echo "Región: ${REGION}"
echo "Servicio: ${SERVICE_NAME}"
echo "=========================================="

# 1. Configurar proyecto
echo "📝 Configurando proyecto..."
gcloud config set project ${PROJECT_ID}

# 2. Construir imagen Docker
echo "🔨 Construyendo imagen Docker..."
gcloud builds submit --tag ${IMAGE_NAME}

# 3. Desplegar en Cloud Run
echo "☁️  Desplegando en Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "ENVIRONMENT=production"

# 4. Obtener URL del servicio
echo "✅ Deployment completado!"
echo ""
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "🌐 URL del servicio: ${SERVICE_URL}"
echo ""
echo "Endpoints disponibles:"
echo "  ${SERVICE_URL}/health"
echo "  ${SERVICE_URL}/dashboard/data"
echo "  ${SERVICE_URL}/docs"
