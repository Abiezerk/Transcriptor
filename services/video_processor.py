import subprocess
import logging
import platform
import shutil
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def find_ffmpeg():
    """Busca ffmpeg.exe: primero el empaquetado, luego el del sistema."""
    if getattr(sys, 'frozen', False):
        bundled = Path(sys._MEIPASS) / "ffmpeg.exe"
        if bundled.exists():
            return str(bundled)

    local = Path(__file__).parent.parent / "ffmpeg.exe"
    if local.exists():
        return str(local)

    en_path = shutil.which("ffmpeg")
    if en_path:
        return en_path

    return None


class VideoProcessor:
    @staticmethod
    def extract_audio(video_path, output_audio_path):
        ffmpeg_bin = find_ffmpeg()
        if not ffmpeg_bin:
            raise Exception("FFmpeg no encontrado. Reinstala la aplicacion.")

        try:
            command = [
                ffmpeg_bin,
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                output_audio_path
            ]

            if platform.system() == 'Windows':
                subprocess.run(command, capture_output=True, text=True, check=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run(command, capture_output=True, text=True, check=True)

            logger.info(f"Audio extraido: {output_audio_path}")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Error FFmpeg: {e.stderr}")
