# Transcriptor de Videos

Aplicación de escritorio para Windows que convierte el audio de cualquier video en texto,
funcionando de forma local en tu computadora.

---

## Para usuarios

### Instalación

1. Ve a la sección **[Releases](../../releases)** de este repositorio.
2. Descarga el archivo `TranscriptorDeVideos-Setup.exe`.
3. Ejecútalo y sigue el asistente de instalación.
4. Al terminar tendrás un acceso directo en el escritorio y en el menú inicio.

> **Importante — la primera vez necesitas conexión a internet.**
> Al procesar tu primer video, la aplicación descarga automáticamente el modelo de
> reconocimiento de voz (aproximadamente 145 MB). Esto ocurre una sola vez.
> A partir de ahí el programa funciona completamente sin internet.

> **Aviso de Windows SmartScreen.**
> Como el instalador no cuenta con una firma digital de pago, Windows mostrará el mensaje
> "Windows protegió tu PC". Haz clic en **Más información → Ejecutar de todas formas**.

### Cómo se usa

1. Abre el programa.
2. Pulsa **Seleccionar Video** y elige tu archivo.
3. Pulsa **Procesar Video** y espera a que la barra llegue al 100 %.
4. El texto aparecerá en el área de transcripción. Desde ahí puedes:
   - **Copiar** — envía toda la transcripción al portapapeles.
   - **Guardar** — abre una ventana para elegir carpeta y nombre del archivo `.txt`.

### Requisitos

- Windows 10 u 11 (64 bits)
- Aproximadamente 3 GB de espacio libre
- Conexión a internet únicamente en el primer uso

---

## Características

- **Detección automática de idioma.** No hace falta indicar en qué idioma está el video.
- **Multiidioma.** Transcribe español, inglés, portugués, francés, alemán, italiano y muchos más.
- **Procesamiento local.** El audio nunca sale de tu computadora: no se sube a ningún servidor.
- **Funciona sin internet** una vez descargado el modelo.
- **Barra de progreso real,** sincronizada con el avance efectivo de la transcripción.
- **Interfaz gráfica sencilla,** sin necesidad de usar la línea de comandos.
- **Formatos compatibles:** MP4, AVI, MKV, MOV, WEBM y otros.
- **Exportación a texto plano** (`.txt`) o copiado directo al portapapeles.
- **FFmpeg incluido** en el instalador: no requiere instalaciones adicionales.

---

## Para desarrolladores

### Tecnologías

| Componente | Uso |
|---|---|
| [OpenAI Whisper](https://github.com/openai/whisper) | Motor de reconocimiento de voz |
| PyTorch (CPU) | Backend de inferencia |
| FFmpeg | Extracción y conversión de audio |
| Tkinter | Interfaz gráfica |
| langdetect | Detección de idioma del texto |
| PyInstaller | Empaquetado del ejecutable |
| Inno Setup | Generación del instalador |

### Estructura del proyecto

```
transcription-app/
├── main.py                        # Interfaz gráfica y punto de entrada
├── services/
│   ├── transcription_service.py   # Orquesta el proceso y reporta progreso
│   ├── video_processor.py         # Extracción de audio con FFmpeg
│   └── language_detection.py      # Detección de idioma
├── build.spec                     # Configuración de PyInstaller
├── installer.iss                  # Script de Inno Setup
├── requirements.txt
└── ffmpeg.exe                     # No incluido en el repositorio (ver abajo)
```

### Entorno de desarrollo

```powershell
git clone https://github.com/Abiezerk/Transcriptor.git
cd transcriptor-videos

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py
```

Necesitas además `ffmpeg.exe` en la raíz del proyecto. Descárgalo de
[gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (versión *essentials*) y copia el
ejecutable desde la carpeta `bin`.

### Compilar el ejecutable

Desde una terminal **sin permisos de administrador** (PyInstaller los rechaza):

```powershell
python -m PyInstaller build.spec
```

El resultado queda en `dist\TranscriptorDeVideos\`.

### Generar el instalador

1. Instala [Inno Setup](https://jrsoftware.org/isdl.php).
2. Abre `installer.iss` y pulsa **F9**.
3. El instalador se genera en la carpeta `Instalador\`.

---

## Licencia

Este proyecto utiliza OpenAI Whisper, publicado bajo licencia MIT.
