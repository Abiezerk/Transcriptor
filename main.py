import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import os
import sys
import threading
from pathlib import Path

# --- Blindaje para modo --windowed (sin consola) ---
# PyInstaller deja sys.stdout/stderr en None y la barra tqdm interna
# de Whisper escribe ahi, lo que provoca un crash al procesar.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

# --- FFmpeg empaquetado ---
# Se agrega al PATH del proceso para que lo encuentren tanto
# video_processor como el load_audio interno de Whisper.
def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

BUNDLE_DIR = get_bundle_dir()
os.environ['PATH'] = str(BUNDLE_DIR) + os.pathsep + os.environ.get('PATH', '')

from services.transcription_service import TranscriptionWorker

# El log va a AppData porque Program Files es de solo lectura
LOG_DIR = Path(os.getenv('LOCALAPPDATA', Path.home())) / "TranscriptorDeVideos"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "transcriptor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg="#4A90E2", fg="white", width=150, height=45, radius=15, **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.bg = bg
        self.fg = fg
        self.radius = radius
        self.width = width
        self.height = height
        
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.draw_button()
    
    def draw_button(self, color=None):
        self.delete("all")
        if color is None:
            color = self.bg
        
        self.create_oval(0, 0, self.radius*2, self.radius*2, fill=color, outline=color)
        self.create_oval(self.width-self.radius*2, 0, self.width, self.radius*2, fill=color, outline=color)
        self.create_oval(0, self.height-self.radius*2, self.radius*2, self.height, fill=color, outline=color)
        self.create_oval(self.width-self.radius*2, self.height-self.radius*2, self.width, self.height, fill=color, outline=color)
        
        self.create_rectangle(self.radius, 0, self.width-self.radius, self.height, fill=color, outline=color)
        self.create_rectangle(0, self.radius, self.width, self.height-self.radius, fill=color, outline=color)
        
        self.create_text(self.width/2, self.height/2, text=self.text, fill=self.fg, font=("Segoe UI", 10, "bold"))
    
    def on_enter(self, e):
        shade = tuple(max(0, int(int(self.bg[i:i+2], 16) * 0.85)) for i in (1, 3, 5))
        darker = '#{:02x}{:02x}{:02x}'.format(*shade)
        self.draw_button(darker)
    
    def on_leave(self, e):
        self.draw_button()

class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor de Videos")
        self.root.geometry("1400x850")
        self.root.configure(bg="#f8f9fa")
        self.video_path = None
        
        # Colores claros
        self.bg_main = "#f8f9fa"
        self.bg_card = "#ffffff"
        self.color_primary = "#4A90E2"
        self.color_accent = "#7CB342"
        self.text_primary = "#1a1a1a"
        self.text_secondary = "#666666"
        self.border_color = "#e0e0e0"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header elegante
        header = tk.Frame(self.root, bg=self.bg_card, height=100)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Separador sutil
        sep_top = tk.Frame(header, bg=self.border_color, height=1)
        sep_top.pack(fill="x", side="top")
        
        header_inner = tk.Frame(header, bg=self.bg_card)
        header_inner.pack(expand=True, padx=40)
        
        title = tk.Label(header_inner, text="Transcriptor de Videos", font=("Segoe UI", 26, "bold"), bg=self.bg_card, fg=self.color_primary)
        title.pack(anchor="w", pady=(15, 5))
        
        subtitle = tk.Label(header_inner, text="Convierte tus videos a texto automáticamente", font=("Segoe UI", 10), bg=self.bg_card, fg=self.text_secondary)
        subtitle.pack(anchor="w", pady=(0, 15))
        
        # Línea separadora
        sep = tk.Frame(self.root, bg=self.border_color, height=1)
        sep.pack(fill="x")
        
        # Main content
        content = tk.Frame(self.root, bg=self.bg_main)
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Card de carga
        load_card = tk.Frame(content, bg=self.bg_card, relief="flat", bd=0)
        load_card.pack(fill="x", pady=(0, 30))
        
        # Sombra sutil
        shadow = tk.Frame(content, bg="#e8e8e8", height=1)
        shadow.pack_configure(in_=load_card, fill="x", side="bottom", before=load_card)
        
        load_inner = tk.Frame(load_card, bg=self.bg_card)
        load_inner.pack(padx=35, pady=30, fill="x")
        
        file_label = tk.Label(load_inner, text="📁 Selecciona tu video", font=("Segoe UI", 13, "bold"), bg=self.bg_card, fg=self.text_primary)
        file_label.pack(anchor="w", pady=(0, 12))
        
        self.label_file = tk.Label(load_inner, text="Sin archivo seleccionado", font=("Segoe UI", 10), bg=self.bg_card, fg=self.text_secondary)
        self.label_file.pack(anchor="w", pady=(0, 20))
        
        # Botones
        btn_container = tk.Frame(load_inner, bg=self.bg_card)
        btn_container.pack(fill="x", pady=(0, 15))
        
        self.btn_select = RoundedButton(btn_container, "Seleccionar Video", self.load_video, bg=self.color_primary, fg="white", width=170, height=50, radius=12)
        self.btn_select.pack(side="left", padx=(0, 15))
        
        self.btn_process = RoundedButton(btn_container, "Procesar Video", self.start_processing, bg=self.color_accent, fg="white", width=170, height=50, radius=12)
        self.btn_process.pack(side="left")
        
        # Progress con porcentaje
        progress_frame = tk.Frame(load_inner, bg=self.bg_card)
        progress_frame.pack(fill="x", pady=15)
        progress_frame.pack_forget()
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400, style="TProgressbar")
        self.progress.pack(side="left", fill="x", expand=True)
        
        self.label_progress = tk.Label(progress_frame, text="0%", font=("Segoe UI", 10, "bold"), bg=self.bg_card, fg=self.color_primary, width=5)
        self.label_progress.pack(side="left", padx=(10, 0))
        
        self.progress_container = progress_frame
        
        # Contenedor de tabs
        tab_container = tk.Frame(content, bg=self.bg_main)
        tab_container.pack(fill="both", expand=True)
        
        # Botones de tab
        tab_btn_frame = tk.Frame(tab_container, bg=self.bg_main)
        tab_btn_frame.pack(fill="x", pady=(0, 20))
        
        self.tab_trans_btn = tk.Button(tab_btn_frame, text="📝 Transcripción", font=("Segoe UI", 11, "bold"), bg=self.bg_card, fg=self.color_primary, relief="flat", bd=0, cursor="hand2", padx=25, pady=12, activebackground=self.bg_card, activeforeground=self.color_primary)
        self.tab_trans_btn.pack(side="left", padx=0)
        
        # Frame para tabs
        self.tab_content = tk.Frame(tab_container, bg=self.bg_main)
        self.tab_content.pack(fill="both", expand=True)
        
        # Tab 1 - Transcripción
        self.frame_trans = tk.Frame(self.tab_content, bg=self.bg_card, relief="flat", bd=0)
        self.frame_trans.pack(fill="both", expand=True)
        
        trans_inner = tk.Frame(self.frame_trans, bg=self.bg_card)
        trans_inner.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Botones tab 1 (se empaquetan PRIMERO, anclados abajo, para
        # que el area de texto no les robe el espacio al expandirse)
        btn_frame_trans = tk.Frame(trans_inner, bg=self.bg_card)
        btn_frame_trans.pack(side="bottom", fill="x", pady=(20, 0))

        RoundedButton(btn_frame_trans, "💾 Guardar", self.save_transcription, bg=self.color_primary, fg="white", width=150, height=42, radius=10).pack(side="right")
        RoundedButton(btn_frame_trans, "📋 Copiar", lambda: self.copy_text(self.text_transcription), bg="#999999", fg="white", width=150, height=42, radius=10).pack(side="right", padx=(0, 12))

        # Scrollbar y area de texto
        text_frame = tk.Frame(trans_inner, bg=self.bg_card)
        text_frame.pack(side="top", fill="both", expand=True)
        
        scrollbar_trans = tk.Scrollbar(text_frame, bg="#e0e0e0")
        scrollbar_trans.pack(side="right", fill="y", padx=(10, 0))
        
        self.text_transcription = tk.Text(text_frame, height=10, font=("Courier New", 11), bg=self.bg_card, fg=self.text_primary, relief="flat", bd=0, yscrollcommand=scrollbar_trans.set, insertbackground=self.color_primary, padx=10, pady=10)
        self.text_transcription.pack(side="left", fill="both", expand=True)
        scrollbar_trans.config(command=self.text_transcription.yview)
        
    def load_video(self):
        file_path = filedialog.askopenfilename(title="Seleccionar video", filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov *.webm"), ("Todos", "*.*")])
        if file_path:
            self.video_path = file_path
            file_name = Path(file_path).name
            file_size = Path(file_path).stat().st_size / (1024 * 1024)
            self.label_file.config(text=f"✓ {file_name} ({file_size:.1f} MB)", fg=self.color_accent)
    
    def start_processing(self):
        if not self.video_path:
            messagebox.showwarning("Error", "Selecciona un video")
            return
        
        self.progress_container.pack(fill="x", pady=15)
        self.progress.config(value=0)
        self.label_progress.config(text="0%")
        
        def progress_callback(value, message=""):
            self.progress.config(value=value)
            self.label_progress.config(text=f"{value}%")
            self.root.update_idletasks()
        
        def process():
            try:
                worker = TranscriptionWorker(self.video_path, progress_callback=progress_callback)
                results = worker.run()
                
                self.text_transcription.config(state="normal")
                self.text_transcription.delete(1.0, "end")
                self.text_transcription.insert(1.0, results['transcription'])
                
                messagebox.showinfo("Éxito", "Video procesado correctamente")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.progress_container.pack_forget()
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    

    def copy_text(self, text_widget):
        text = text_widget.get(1.0, "end")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Éxito", "Copiado al portapapeles")
    
    def save_transcription(self):
        contenido = self.text_transcription.get(1.0, "end").strip()
        if not contenido:
            messagebox.showwarning("Aviso", "No hay transcripcion para guardar")
            return

        # Sugiere el nombre del video como nombre del .txt
        sugerido = "transcripcion.txt"
        if self.video_path:
            sugerido = Path(self.video_path).stem + ".txt"

        file_path = filedialog.asksaveasfilename(
            title="Guardar transcripcion",
            defaultextension=".txt",
            initialfile=sugerido,
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo("Éxito", f"Guardado:\n{file_path}")


if __name__ == '__main__':
    root = tk.Tk()
    app = TranscriptorApp(root)
    root.mainloop()
