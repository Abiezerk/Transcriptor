@echo off
chcp 65001 >nul
cls

REM Activar ambiente virtual y ejecutar aplicación
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo.
    echo ❌ Error: No se pudo activar el ambiente virtual
    echo.
    echo Por favor, ejecuta primero: instalar.bat
    echo.
    pause
    exit /b 1
)

echo 🎬 Iniciando Transcriptor de Videos...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar la aplicación
    echo.
    echo Revisa transcriptor.log para más detalles
    echo.
    pause
)
