@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   INSTALACIÓN: Transcriptor de Videos Offline              ║
echo ║   (Esta ventana se cerrará cuando termine)                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado.
    echo.
    echo    Descárgalo desde: https://www.python.org/downloads/
    echo    IMPORTANTE: Marca "Add Python to PATH" en la instalación
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

REM Crear ambiente virtual
if not exist "venv" (
    echo 📦 Creando ambiente virtual...
    python -m venv venv
    echo ✓ Ambiente creado
) else (
    echo ⚠️  Ambiente virtual ya existe
)
echo.

REM Activar ambiente
echo 🚀 Activando ambiente...
call venv\Scripts\activate.bat
echo ✓ Ambiente activado
echo.

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo ✓ pip actualizado
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias...
echo.
echo    ESPERA - Esto toma 20-30 minutos (~2.5 GB)
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Hubo un error durante la instalación
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Instalación completada exitosamente!
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   PRÓXIMOS PASOS:                                          ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  1. INSTALA FFmpeg desde:                                 ║
echo ║     https://ffmpeg.org/download.html                       ║
echo ║     O ejecuta: choco install ffmpeg                        ║
echo ║                                                            ║
echo ║  2. PARA EJECUTAR LA APP:                                 ║
echo ║     Crea un archivo ejecutar.bat con:                      ║
echo ║                                                            ║
echo ║     @echo off                                              ║
echo ║     call venv\Scripts\activate.bat                         ║
echo ║     python main.py                                         ║
echo ║                                                            ║
echo ║  3. LUEGO EJECUTA: ejecutar.bat                           ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
