# Script para desplegar en Google Cloud Run (PowerShell)
# Uso: .\deploy.ps1 -ProjectId "tu-proyecto-id" -Region "us-central1"

param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = "tu-proyecto-id",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "co2-microservice"
)

$ImageName = "gcr.io/$ProjectId/$ServiceName"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Desplegando CO2 Microservice" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Proyecto: $ProjectId"
Write-Host "Región: $Region"
Write-Host "Servicio: $ServiceName"
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Configurar proyecto
Write-Host "`n📝 Configurando proyecto..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# 2. Construir imagen Docker
Write-Host "`n🔨 Construyendo imagen Docker..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageName

# 3. Desplegar en Cloud Run
Write-Host "`n☁️  Desplegando en Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
  --image $ImageName `
  --platform managed `
  --region $Region `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300 `
  --max-instances 10 `
  --set-env-vars "ENVIRONMENT=production"

# 4. Obtener URL del servicio
Write-Host "`n✅ Deployment completado!" -ForegroundColor Green
$ServiceUrl = gcloud run services describe $ServiceName --region $Region --format 'value(status.url)'
Write-Host "`n🌐 URL del servicio: $ServiceUrl" -ForegroundColor Green
Write-Host "`nEndpoints disponibles:"
Write-Host "  $ServiceUrl/health"
Write-Host "  $ServiceUrl/dashboard/data"
Write-Host "  $ServiceUrl/docs"
