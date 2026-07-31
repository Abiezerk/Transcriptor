import whisper
import logging
import tempfile
import os
import time
from tqdm import tqdm
from pathlib import Path
from .language_detection import detect_language
from .video_processor import VideoProcessor

logger = logging.getLogger(__name__)

class TranscriptionWorker:
    def __init__(self, video_path, progress_callback=None):
        self.video_path = video_path
        self.whisper_model = None
        self.progress_callback = progress_callback
        
    def update_progress(self, value):
        if self.progress_callback:
            self.progress_callback(max(0, min(100, int(value))), "")
    
    def run(self):
        try:
            # 1. Extracción de audio (1% - 5%)
            self.update_progress(1)
            audio_path = self.extract_audio()
            self.update_progress(5)
            
            # 2. Carga del modelo (5% - 10%)
            logger.info("Cargando modelo Whisper...")
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            self.update_progress(10)
            
            # 3. Transcripción sincronizada con tqdm (10% - 95%)
            logger.info("Transcribiendo...")
            
            original_tqdm_init = tqdm.__init__
            worker_self = self

            # Capturamos el avance interno de la barra de terminal
            def custom_tqdm_init(tqdm_instance, *args, **kwargs):
                original_tqdm_init(tqdm_instance, *args, **kwargs)
                
                old_update = tqdm_instance.update
                def custom_update(n=1):
                    result = old_update(n)
                    if tqdm_instance.total and tqdm_instance.total > 0:
                        whisper_pct = tqdm_instance.n / tqdm_instance.total
                        # Mapeamos el progreso de Whisper (0-100%) al rango 10% - 95% de la interfaz
                        ui_pct = 10 + (whisper_pct * 85)
                        worker_self.update_progress(ui_pct)
                    return result
                
                tqdm_instance.update = custom_update

            tqdm.__init__ = custom_tqdm_init
            
            try:
                result = self.whisper_model.transcribe(
                    audio_path, 
                    language=None, 
                    verbose=False
                )
            finally:
                # Restauramos tqdm a su estado original siempre
                tqdm.__init__ = original_tqdm_init

            self.update_progress(95)
            transcription = result['text']
            
            # 4. Detección de idioma y finalización (95% - 100%)
            logger.info("Detectando idioma...")
            detected_lang = detect_language(transcription)
            
            self.update_progress(100)

            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return {
                'transcription': transcription,
                'detected_language': detected_lang
            }
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise
    
    def extract_audio(self):
        try:
            processor = VideoProcessor()
            temp_dir = tempfile.gettempdir()
            audio_path = os.path.join(temp_dir, "temp_audio.wav")
            processor.extract_audio(self.video_path, audio_path)
            return audio_path
        except Exception as e:
            raise Exception(f"Error extrayendo audio: {str(e)}")