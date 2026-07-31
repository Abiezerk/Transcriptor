"""
Interfaz Principal de la Aplicación
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QFileDialog, QLabel, QProgressBar,
    QTextEdit, QTabWidget, QComboBox, QMessageBox,
    QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from services.transcription_service import TranscriptionWorker

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.worker = None
        self.thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🎬 Transcriptor de Videos - Offline")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.load_styles())
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # ===== SECCIÓN DE CARGA =====
        load_section = self.create_load_section()
        layout.addWidget(load_section)
        
        # ===== TABS =====
        tabs = QTabWidget()
        transcription_tab = self.create_transcription_tab()
        tabs.addTab(transcription_tab, "📝 Transcripción")
        
        translation_tab = self.create_translation_tab()
        tabs.addTab(translation_tab, "🌐 Traducción")
        
        layout.addWidget(tabs)
        
        central_widget.setLayout(layout)
        
        # Barra de estado
        self.statusBar().showMessage("Listo")
    
    def create_load_section(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📁 Cargar Video")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("📁 Seleccionar Video")
        self.btn_load.setMinimumHeight(40)
        self.btn_load.setFont(QFont("Arial", 11))
        self.btn_load.clicked.connect(self.load_video)
        button_layout.addWidget(self.btn_load)
        
        self.btn_process = QPushButton("⚙️ Procesar Video")
        self.btn_process.setMinimumHeight(40)
        self.btn_process.setFont(QFont("Arial", 11))
        self.btn_process.clicked.connect(self.start_processing)
        self.btn_process.setEnabled(False)
        button_layout.addWidget(self.btn_process)
        
        self.btn_export = QPushButton("💾 Guardar Resultados")
        self.btn_export.setMinimumHeight(40)
        self.btn_export.setFont(QFont("Arial", 11))
        self.btn_export.clicked.connect(self.save_results)
        self.btn_export.setEnabled(False)
        button_layout.addWidget(self.btn_export)
        
        layout.addLayout(button_layout)
        
        # Info del archivo
        self.label_file_info = QLabel("❌ Ningún archivo seleccionado")
        self.label_file_info.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.label_file_info)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        widget.setLayout(layout)
        return widget
    
    def create_transcription_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Idioma detectado:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Detectando...", "Español", "Inglés", "Francés", "Alemán"])
        lang_layout.addWidget(self.combo_lang)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        self.text_transcription = QTextEdit()
        self.text_transcription.setFont(QFont("Courier", 10))
        layout.addWidget(self.text_transcription)
        
        button_layout = QHBoxLayout()
        btn_copy = QPushButton("📋 Copiar")
        btn_copy.clicked.connect(lambda: self.copy_to_clipboard(self.text_transcription.toPlainText()))
        button_layout.addWidget(btn_copy)
        
        btn_save = QPushButton("💾 Guardar .txt")
        btn_save.clicked.connect(self.save_transcription)
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
        widget.setLayout(layout)
        return widget
    
    def create_translation_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        trans_layout = QHBoxLayout()
        trans_layout.addWidget(QLabel("Traducir a:"))
        self.combo_trans_lang = QComboBox()
        self.combo_trans_lang.addItems(["Español", "Inglés"])
        trans_layout.addWidget(self.combo_trans_lang)
        trans_layout.addStretch()
        layout.addLayout(trans_layout)
        
        self.text_translation = QTextEdit()
        self.text_translation.setFont(QFont("Courier", 10))
        layout.addWidget(self.text_translation)
        
        button_layout = QHBoxLayout()
        btn_copy = QPushButton("📋 Copiar")
        btn_copy.clicked.connect(lambda: self.copy_to_clipboard(self.text_translation.toPlainText()))
        button_layout.addWidget(btn_copy)
        
        btn_save = QPushButton("💾 Guardar .txt")
        btn_save.clicked.connect(self.save_translation)
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
        widget.setLayout(layout)
        return widget
    
    def load_styles(self):
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #ccc;
            color: #999;
        }
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: white;
        }
        QLabel {
            color: #333;
        }
        QComboBox {
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        QProgressBar {
            border: 1px solid #ddd;
            border-radius: 3px;
            height: 25px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
        }
        """
    
    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov *.webm);;Todos (*)"
        )
        
        if file_path:
            self.video_path = file_path
            file_name = Path(file_path).name
            file_size = Path(file_path).stat().st_size / (1024 * 1024)
            self.label_file_info.setText(
                f"✓ Archivo: {file_name} ({file_size:.1f} MB)"
            )
            self.btn_process.setEnabled(True)
            self.statusBar().showMessage("Listo para procesar")
    
    def start_processing(self):
        if not self.video_path:
            QMessageBox.warning(self, "Error", "Selecciona un video primero")
            return
        
        self.btn_process.setEnabled(False)
        self.btn_load.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage("⏳ Procesando...")
        
        self.thread = QThread()
        self.worker = TranscriptionWorker(self.video_path)
        self.worker.moveToThread(self.thread)
        
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.statusBar().showMessage)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.thread.started.connect(self.worker.run)
        
        self.thread.start()
    
    def on_finished(self, results):
        self.thread.quit()
        self.thread.wait()
        
        self.text_transcription.setPlainText(results['transcription'])
        self.text_translation.setPlainText(results['translation'])
        
        lang_map = {'es': 'Español', 'en': 'Inglés', 'fr': 'Francés', 'de': 'Alemán', 'it': 'Italiano'}
        lang_name = lang_map.get(results['detected_language'], 'Desconocido')
        self.combo_lang.setCurrentText(lang_name)
        
        self.progress_bar.setVisible(False)
        self.btn_process.setEnabled(True)
        self.btn_load.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.statusBar().showMessage("✓ Completado")
        
        QMessageBox.information(self, "Éxito", "✓ Video procesado correctamente")
    
    def on_error(self, error_msg):
        self.thread.quit()
        self.thread.wait()
        self.progress_bar.setVisible(False)
        self.btn_process.setEnabled(True)
        self.btn_load.setEnabled(True)
        self.statusBar().showMessage("✗ Error")
        
        QMessageBox.critical(self, "Error", f"Error al procesar:\n\n{error_msg}")
    
    def copy_to_clipboard(self, text):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Éxito", "✓ Copiado al portapapeles")
    
    def save_transcription(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar transcripción", "", "Archivos de texto (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_transcription.toPlainText())
            QMessageBox.information(self, "Éxito", f"✓ Guardado en:\n{file_path}")
    
    def save_translation(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar traducción", "", "Archivos de texto (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_translation.toPlainText())
            QMessageBox.information(self, "Éxito", f"✓ Guardado en:\n{file_path}")
    
    def save_results(self):
        if not self.text_transcription.toPlainText():
            QMessageBox.warning(self, "Error", "No hay resultados para guardar")
            return
        
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            # Guardar transcripción
            with open(f"{folder}/transcripcion.txt", 'w', encoding='utf-8') as f:
                f.write(self.text_transcription.toPlainText())
            
            # Guardar traducción
            with open(f"{folder}/traduccion.txt", 'w', encoding='utf-8') as f:
                f.write(self.text_translation.toPlainText())
            
            QMessageBox.information(
                self, "Éxito",
                f"✓ Archivos guardados en:\n{folder}"
            )
