# setup.ps1 - Instalación automática para Windows
# Ejecutar como: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALACIÓN: Transcriptor de Videos Offline              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$python = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "   Descárgalo desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Python encontrado: $python" -ForegroundColor Green
Write-Host ""

# Verificar si FFmpeg está instalado
Write-Host "🔍 Verificando FFmpeg..." -ForegroundColor Yellow
$ffmpeg = ffmpeg -version 2>&1 | Select-Object -First 1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  FFmpeg no está instalado" -ForegroundColor Yellow
    Write-Host "   Lo necesitas. Descárgalo desde: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    Write-Host "   O instálalo con chocolatey: choco install ffmpeg" -ForegroundColor Yellow
    Write-Host ""
}
else {
    Write-Host "✓ FFmpeg encontrado" -ForegroundColor Green
}
Write-Host ""

# Crear ambiente virtual
Write-Host "📦 Creando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  Ambiente virtual ya existe, omitiendo..." -ForegroundColor Yellow
}
else {
    python -m venv venv
    Write-Host "✓ Ambiente virtual creado" -ForegroundColor Green
}
Write-Host ""

# Activar ambiente virtual
Write-Host "🚀 Activando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Ambiente activado" -ForegroundColor Green
Write-Host ""

# Actualizar pip
Write-Host "📦 Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel | Out-Null
Write-Host "✓ pip actualizado" -ForegroundColor Green
Write-Host ""

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 20-30 minutos - procura no interrumpir)" -ForegroundColor Cyan
Write-Host ""

pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Instalación completada exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   PRÓXIMOS PASOS:                                          ║" -ForegroundColor Green
    Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║  1. Para ejecutar la app:                                 ║" -ForegroundColor Green
    Write-Host "║     python src/main.py                                    ║" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Green
    Write-Host "║  2. Para crear el .exe:                                   ║" -ForegroundColor Green
    Write-Host "║     pyinstaller --onefile --windowed src/main.py          ║" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "❌ Hubo un error durante la instalación" -ForegroundColor Red
    Write-Host "   Revisa los mensajes arriba para más detalles" -ForegroundColor Yellow
    exit 1
}
